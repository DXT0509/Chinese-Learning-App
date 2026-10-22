package com.example.chineselearningapp.feature.auth.data

import com.example.chineselearningapp.core.network.*
import com.example.chineselearningapp.domain.repository.*
import java.util.Locale
import javax.inject.Inject
import javax.inject.Singleton
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext
import retrofit2.HttpException

@Singleton
class RemoteSessionRepository @Inject constructor(private val api: SessionApi, private val vault: SessionTokenStore) : SessionRepository {
    private val mutex = Mutex()
    private var tokens: TokensDto? = null
    private var loaded = false
    private fun load(): TokensDto? {
        if (!loaded) { tokens = vault.read(); loaded = true }
        return tokens
    }
    private fun save(value: TokensDto?) {
        if (value == null) vault.clear() else vault.write(value)
        tokens = value
        loaded = true
    }
    internal suspend fun <T> authorized(call: suspend (String) -> T): T = withContext(Dispatchers.IO) {
        mutex.withLock {
            val current = load() ?: throw SessionExpired()
            try { call("Bearer ${current.access}") }
            catch (error: HttpException) {
                if (error.code() != 401) throw error
                val renewed = try { api.refresh(RefreshDto(current.refresh)) }
                catch (refreshError: HttpException) {
                    if (refreshError.code() == 401) { save(null); throw SessionExpired() }
                    throw refreshError
                }
                save(renewed)
                try { call("Bearer ${renewed.access}") }
                catch (retryError: HttpException) {
                    if (retryError.code() == 401) { save(null); throw SessionExpired() }
                    throw retryError
                }
            }
        }
    }
    override suspend fun authenticate(email: String, password: String, register: Boolean) = withContext(Dispatchers.IO) {
        mutex.withLock {
            val data = CredentialsDto(email.trim().lowercase(Locale.ROOT), password)
            save(if (register) api.register(data) else api.login(data))
        }
    }
    override suspend fun account(): Account? {
        return try { authorized { api.me(it) }.let { Account(it.id, it.email, it.displayName.orEmpty()) } }
        catch (_: SessionExpired) { null }
    }
    override suspend fun logout() = withContext(Dispatchers.IO) {
        mutex.withLock {
            val current = load()
            if (current != null) {
                try { api.logout(RefreshDto(current.refresh)) }
                catch (error: HttpException) { if (error.code() != 401) throw error }
            }
            save(null)
        }
    }
    override suspend fun catalog() = authorized { api.catalog(it) }.map { CatalogLesson(it.versionId, it.title, it.version) }
    override suspend fun runs() = authorized { api.runs(it) }.map { it.domain() }
    override suspend fun start(versionId: String, requestId: String) = authorized { api.start(it, StartDto(versionId, requestId)) }.domain()
    override suspend fun resume(runId: String) = authorized { api.resume(it, runId) }.domain()
    override suspend fun scenes(versionId: String) = authorized { api.bundle(it, versionId) }.getAsJsonArray("scenes").map {
        PreviewScene(it.asJsonObject.get("scene_key").asString, 0)
    }
    override suspend fun checkpoint(runId: String, sceneKey: String, page: Int) = authorized { api.checkpoint(it, runId, sceneKey, PageDto(page)) }.domain()
    override suspend fun lessonBundle(versionId: String) =
        com.example.chineselearningapp.feature.lesson.data.LessonBundleMapper.map(authorized { api.bundle(it, versionId) }, versionId)
    override suspend fun lessonAsset(versionId: String, assetId: String) = authorized {
        api.asset(it, versionId, assetId).use { body -> body.bytes() }
    }
    private fun RunDto.domain() = PreviewRun(id, versionId, checkpoints.associate { it.key to it.page }, currentSceneKey)
}

class SessionExpired : Exception()
