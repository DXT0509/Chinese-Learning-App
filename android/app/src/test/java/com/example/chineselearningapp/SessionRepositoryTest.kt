package com.example.chineselearningapp

import com.example.chineselearningapp.core.network.*
import com.example.chineselearningapp.feature.auth.data.RemoteSessionRepository
import kotlinx.coroutines.test.runTest
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.junit.Assert.*
import org.junit.Test
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

class SessionRepositoryTest {
    private class Store : SessionTokenStore {
        var value: TokensDto? = TokensDto("old-access", "old-refresh")
        override fun read() = value
        override fun write(tokens: TokensDto) { value = tokens }
        override fun clear() { value = null }
    }
    private fun api(server: MockWebServer) = Retrofit.Builder().baseUrl(server.url("/"))
        .addConverterFactory(GsonConverterFactory.create()).build().create(SessionApi::class.java)
    @Test fun expiredAccessRefreshesAndPersistsRotatedPair() = runTest {
        MockWebServer().use { server ->
            val store = Store()
            server.enqueue(MockResponse().setResponseCode(401))
            server.enqueue(MockResponse().setBody("""{"access_token":"new-access","refresh_token":"new-refresh"}"""))
            server.enqueue(MockResponse().setBody("""{"id":"user-a","email":"a@example.com"}"""))
            val repository = RemoteSessionRepository(api(server), store)
            assertEquals("user-a", repository.account()?.id)
            assertEquals("new-refresh", store.value?.refresh)
            assertEquals("Bearer old-access", server.takeRequest().getHeader("Authorization"))
            assertEquals("/api/v1/auth/refresh", server.takeRequest().path)
            assertEquals("Bearer new-access", server.takeRequest().getHeader("Authorization"))
        }
    }
    @Test fun revokedRefreshClearsIdentity() = runTest {
        MockWebServer().use { server ->
            val store = Store()
            server.enqueue(MockResponse().setResponseCode(401))
            server.enqueue(MockResponse().setResponseCode(401))
            assertNull(RemoteSessionRepository(api(server), store).account())
            assertNull(store.value)
        }
    }
    @Test fun transientRefreshFailureKeepsSessionForRetry() = runTest {
        MockWebServer().use { server ->
            val store = Store()
            server.enqueue(MockResponse().setResponseCode(401))
            server.enqueue(MockResponse().setResponseCode(503))
            try { RemoteSessionRepository(api(server), store).account(); fail("Expected HTTP failure") }
            catch (_: retrofit2.HttpException) { assertEquals("old-refresh", store.value?.refresh) }
        }
    }
    @Test fun logoutRevokesThenClearsLocalSession() = runTest {
        MockWebServer().use { server ->
            val store = Store()
            server.enqueue(MockResponse().setResponseCode(204))
            RemoteSessionRepository(api(server), store).logout()
            assertNull(store.value)
            val request = server.takeRequest()
            assertEquals("/api/v1/auth/logout", request.path)
            assertTrue(request.body.readUtf8().contains("old-refresh"))
        }
    }
    @Test fun sixCharacterRegistrationUsesRealWireContractAndPersistsSession() = runTest {
        MockWebServer().use { server ->
            val store = Store().apply { value = null }
            server.enqueue(MockResponse().setResponseCode(201).setBody("""{"access_token":"new-access","refresh_token":"new-refresh"}"""))
            server.enqueue(MockResponse().setBody("""{"id":"registered-user","email":"user@example.com","display_name":"An"}"""))
            val repository = RemoteSessionRepository(api(server), store)
            repository.authenticate(" USER@example.com ", "123456", true)
            val request = server.takeRequest()
            assertEquals("/api/v1/auth/register", request.path)
            val body = com.google.gson.JsonParser.parseString(request.body.readUtf8()).asJsonObject
            assertEquals("123456", body.get("password").asString)
            assertEquals("user@example.com", body.get("email").asString)
            assertEquals("new-refresh", store.value?.refresh)
            assertEquals("An", repository.account()?.displayName)
        }
    }
    @Test fun rejectedLoginDoesNotReplaceStoredCredentials() = runTest {
        MockWebServer().use { server ->
            val store = Store()
            server.enqueue(MockResponse().setResponseCode(401))
            try { RemoteSessionRepository(api(server), store).authenticate("user@example.com", "123456", false); fail("Expected rejected login") }
            catch (_: retrofit2.HttpException) { assertEquals("old-refresh", store.value?.refresh) }
        }
    }
    @Test fun startResumeBundleAndCheckpointKeepPinnedWireContract() = runTest {
        MockWebServer().use { server ->
            val store = Store()
            val run = """{"id":"run","lesson_version_id":"pinned","current_scene_key":"scene","checkpoints":[{"scene_key":"scene","page":1}]}"""
            server.enqueue(MockResponse().setBody(run))
            server.enqueue(MockResponse().setBody(run))
            server.enqueue(MockResponse().setBody("""{"schema_version":1,"lesson":{"version_id":"pinned","lesson_type":"VOCABULARY","title":"Ni"},"scenes":[]}"""))
            server.enqueue(MockResponse().setBody(run))
            val repo = RemoteSessionRepository(api(server), store)
            assertEquals("scene", repo.start("pinned", "request").currentSceneKey)
            assertEquals("pinned", repo.resume("run").versionId)
            assertTrue(repo.lessonBundle("pinned").scenes.isEmpty())
            assertEquals(1, repo.checkpoint("run", "scene", 1).checkpoints["scene"])
            val start = server.takeRequest()
            assertEquals("/api/v1/learning-runs", start.path)
            val body = com.google.gson.JsonParser.parseString(start.body.readUtf8()).asJsonObject
            assertEquals("pinned", body.get("lesson_version_id").asString)
            assertTrue(body.get("allow_preview").asBoolean)
            assertEquals("/api/v1/learning-runs/run", server.takeRequest().path)
            assertEquals("/api/v1/lesson-versions/pinned/bundle?allow_preview=true", server.takeRequest().path)
            val checkpoint = server.takeRequest()
            assertEquals("PUT", checkpoint.method)
            assertEquals("/api/v1/learning-runs/run/scenes/scene", checkpoint.path)
            assertEquals("{\"page\":1}", checkpoint.body.readUtf8())
        }
    }
}
