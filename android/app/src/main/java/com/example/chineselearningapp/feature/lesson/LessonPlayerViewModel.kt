package com.example.chineselearningapp.feature.lesson

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.chineselearningapp.R
import com.example.chineselearningapp.domain.model.*
import com.example.chineselearningapp.domain.repository.*
import com.example.chineselearningapp.feature.auth.data.SessionExpired
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject
import java.util.UUID
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow

data class InkPoint(val x: Float, val y: Float)
data class LessonPlayerState(
    val loading: Boolean = false, val saving: Boolean = false, val bundle: LessonBundle? = null,
    val run: PreviewRun? = null, val index: Int = 0, val page: Int = 0, val error: Int? = null,
    val expired: Boolean = false, val closed: Boolean = false,
    val ink: Map<String, List<List<InkPoint>>> = emptyMap(),
    val media: Map<String, ByteArray> = emptyMap(), val mediaErrors: Set<String> = emptySet()
) {
    val scene get() = bundle?.scenes?.getOrNull(index)
    val pageCount get() = when (val content = scene?.content) {
        is SceneContent.Analysis -> content.characters.size.coerceAtLeast(1)
        is SceneContent.Stroke -> content.characters.size.coerceAtLeast(1)
        else -> 1
    }
}

@HiltViewModel
class LessonPlayerViewModel @Inject constructor(private val repository: SessionRepository) : ViewModel() {
    private val mutableState = MutableStateFlow(LessonPlayerState())
    val state = mutableState.asStateFlow()
    private var operation: Job? = null
    private var identity: String? = null
    private var generation = 0
    private var version: String? = null
    private var resumeId: String? = null
    private val requests = mutableMapOf<String, String>()

    fun bindIdentity(accountId: String?) {
        if (identity != accountId) { clear(); identity = accountId }
    }

    fun clear() {
        generation++
        operation?.cancel()
        version = null; resumeId = null; requests.clear()
        mutableState.value = LessonPlayerState()
    }

    fun open(versionId: String?, runId: String? = null) {
        generation++
        operation?.cancel()
        version = versionId; resumeId = runId
        mutableState.value = LessonPlayerState(loading = true)
        val requestedGeneration = generation
        operation = viewModelScope.launch {
            try {
                val run = if (runId != null) repository.resume(runId) else {
                    requireNotNull(versionId)
                    repository.start(versionId, requests.getOrPut(versionId) { UUID.randomUUID().toString() })
                }
                val bundle = repository.lessonBundle(run.versionId)
                val index = bundle.scenes.indexOfFirst { it.key == run.currentSceneKey }.coerceAtLeast(0)
                val content = bundle.scenes.getOrNull(index)?.content
                val count = when (content) {
                    is SceneContent.Analysis -> content.characters.size
                    is SceneContent.Stroke -> content.characters.size
                    else -> 1
                }.coerceAtLeast(1)
                val page = (run.checkpoints[run.currentSceneKey] ?: 0).coerceIn(0, count - 1)
                mutableState.value = LessonPlayerState(bundle = bundle, run = run, index = index, page = page, saving = true)
                // Persist the displayed position immediately, including the first scene.
                if (bundle.scenes.isNotEmpty()) save(index, page)
            } catch (cancelled: CancellationException) { throw cancelled }
            catch (error: Exception) { failure(error, if (state.value.bundle == null) R.string.lesson_load_error else R.string.lesson_save_error) }
            finally { if (generation == requestedGeneration) mutableState.value = mutableState.value.copy(loading = false, saving = false) }
        }
    }

    fun retry() {
        if (state.value.bundle == null) open(version, resumeId) else persist()
    }

    private fun failure(error: Exception, message: Int) {
        mutableState.value = mutableState.value.copy(error = message, expired = error is SessionExpired)
    }

    private suspend fun save(index: Int, page: Int) {
        val current = state.value
        val run = current.run ?: return
        val scene = current.bundle?.scenes?.getOrNull(index) ?: return
        val saved = repository.checkpoint(run.id, scene.key, page)
        mutableState.value = state.value.copy(run = saved, index = index, page = page, error = null)
    }

    private fun write(index: Int, page: Int, close: Boolean = false) {
        if (state.value.loading || state.value.saving) return
        mutableState.value = state.value.copy(saving = true, error = null)
        val requestedGeneration = generation
        operation = viewModelScope.launch {
            try {
                save(index, page)
                mutableState.value = state.value.copy(closed = close)
            } catch (cancelled: CancellationException) { throw cancelled }
            catch (error: Exception) { failure(error, R.string.lesson_save_error) }
            finally { if (generation == requestedGeneration) mutableState.value = state.value.copy(saving = false) }
        }
    }
    fun move(forward: Boolean) {
        val current = state.value
        val scenes = current.bundle?.scenes ?: return
        if (scenes.isEmpty()) return
        if (forward && current.page + 1 < current.pageCount) write(current.index, current.page + 1)
        else if (!forward && current.page > 0) write(current.index, current.page - 1)
        else {
            val index = current.index + if (forward) 1 else -1
            if (index in scenes.indices) write(index, 0)
        }
    }
    fun persist() = write(state.value.index, state.value.page)
    fun exit() {
        if (state.value.loading || state.value.saving) return
        if (state.value.bundle == null) mutableState.value = state.value.copy(closed = true)
        else write(state.value.index, state.value.page, close = true)
    }
    fun ink(strokes: List<List<InkPoint>>) {
        val key = state.value.scene?.key ?: return
        mutableState.value = state.value.copy(ink = state.value.ink + (key to strokes))
    }
    fun loadMedia(id: String) {
        val current = state.value
        if (id in current.media || id in current.mediaErrors) return
        val versionId = current.bundle?.versionId ?: return
        val requestedGeneration = generation
        viewModelScope.launch {
            try {
                val bytes = repository.lessonAsset(versionId, id)
                if (generation == requestedGeneration && state.value.bundle?.versionId == versionId) mutableState.value = state.value.copy(media = state.value.media + (id to bytes))
            } catch (cancelled: CancellationException) { throw cancelled }
            catch (error: Exception) {
                if (generation == requestedGeneration && state.value.bundle?.versionId == versionId) mutableState.value = state.value.copy(
                    expired = error is SessionExpired, mediaErrors = state.value.mediaErrors + id)
            }
        }
    }
}
