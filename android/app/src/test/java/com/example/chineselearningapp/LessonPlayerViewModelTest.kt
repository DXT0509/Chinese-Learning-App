package com.example.chineselearningapp

import com.example.chineselearningapp.domain.model.*
import com.example.chineselearningapp.domain.repository.*
import com.example.chineselearningapp.feature.lesson.LessonPlayerViewModel
import com.example.chineselearningapp.feature.lesson.InkPoint
import com.example.chineselearningapp.feature.auth.data.SessionExpired
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.Assert.*
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class LessonPlayerViewModelTest {
    private class Repository : SessionRepository {
        var run = PreviewRun("run", "pinned", emptyMap())
        var saves = mutableListOf<Pair<String, Int>>()
        var failSave = false
        var expired = false
        var gate: CompletableDeferred<Unit>? = null
        var starts = 0
        var resumes = 0
        var requestedVersion: String? = null
        var failBundle = false
        var bundle = LessonBundle("pinned", "Ni", listOf(
            LessonScene("intro", SceneContent.Handwriting("ni")),
            LessonScene("analysis", SceneContent.Analysis(listOf(
                CharacterPage("a", null, emptyList(), null), CharacterPage("b", null, emptyList(), null)))),
            LessonScene("future", SceneContent.Unsupported)))
        override suspend fun authenticate(email: String, password: String, register: Boolean) = Unit
        override suspend fun account(): Account? = null
        override suspend fun logout() = Unit
        override suspend fun catalog() = emptyList<CatalogLesson>()
        override suspend fun runs() = listOf(run)
        override suspend fun start(versionId: String, requestId: String): PreviewRun {
            starts++; gate?.await(); if (expired) throw SessionExpired(); return run
        }
        override suspend fun resume(runId: String): PreviewRun { resumes++; return run }
        override suspend fun scenes(versionId: String) = emptyList<PreviewScene>()
        override suspend fun lessonBundle(versionId: String): LessonBundle {
            if (failBundle) throw java.io.IOException()
            requestedVersion = versionId; return bundle
        }
        override suspend fun checkpoint(runId: String, sceneKey: String, page: Int): PreviewRun {
            if (failSave) throw java.io.IOException()
            saves += sceneKey to page
            run = run.copy(checkpoints = run.checkpoints + (sceneKey to page), currentSceneKey = sceneKey)
            return run
        }
    }
    private fun scenario(block: suspend TestScope.(Repository, LessonPlayerViewModel) -> Unit) = runTest {
        Dispatchers.setMain(StandardTestDispatcher(testScheduler))
        try { val repo = Repository(); block(repo, LessonPlayerViewModel(repo)) }
        finally { Dispatchers.resetMain() }
    }
    @Test fun startsLoadsPinnedBundleAndSavesFirstScene() = scenario { repo, model ->
        repo.gate = CompletableDeferred()
        model.open("catalog-version")
        runCurrent()
        assertTrue(model.state.value.loading)
        repo.gate!!.complete(Unit)
        advanceUntilIdle()
        assertEquals(1, repo.starts)
        assertEquals("pinned", repo.requestedVersion)
        assertEquals("intro" to 0, repo.saves.single())
        assertFalse(model.state.value.loading)
    }
    @Test fun resumesLatestSceneAndSubpageInsteadOfHighestVisitedScene() = scenario { repo, model ->
        repo.run = repo.run.copy(currentSceneKey = "analysis", checkpoints = mapOf("analysis" to 1, "future" to 0))
        model.open(null, "run"); advanceUntilIdle()
        assertEquals(1, repo.resumes)
        assertEquals(1, model.state.value.index)
        assertEquals(1, model.state.value.page)
        model.move(false); advanceUntilIdle()
        assertEquals(0, model.state.value.page)
        model.move(false); advanceUntilIdle()
        assertEquals(0, model.state.value.index)
        model.exit(); advanceUntilIdle()
        assertTrue(model.state.value.closed)
        assertEquals("intro", repo.run.currentSceneKey)
    }
    @Test fun checkpointFailureKeepsCurrentPositionAndCanRetry() = scenario { repo, model ->
        model.open("pinned"); advanceUntilIdle()
        repo.failSave = true
        model.move(true); advanceUntilIdle()
        assertEquals(0, model.state.value.index)
        assertEquals(R.string.lesson_save_error, model.state.value.error)
        assertFalse(model.state.value.saving)
        repo.failSave = false
        model.move(true); advanceUntilIdle()
        assertEquals(1, model.state.value.index)
        assertNull(model.state.value.error)
    }
    @Test fun failedExitDoesNotCloseOrLoseInk() = scenario { repo, model ->
        model.open("pinned"); advanceUntilIdle()
        val strokes = listOf(listOf(InkPoint(.1f, .2f), InkPoint(.3f, .4f)))
        model.ink(strokes)
        repo.failSave = true
        model.exit(); advanceUntilIdle()
        assertFalse(model.state.value.closed)
        assertEquals(strokes, model.state.value.ink["intro"])
        model.clear()
        assertTrue(model.state.value.ink.isEmpty())
        assertNull(model.state.value.run)
    }
    @Test fun cancellationIsNotShownAsNetworkFailure() = scenario { repo, model ->
        repo.gate = CompletableDeferred()
        model.open("pinned"); runCurrent()
        model.clear(); advanceUntilIdle()
        assertNull(model.state.value.error)
        assertNull(model.state.value.bundle)
    }
    @Test fun unauthorizedIsExplicitAndUnsupportedContentRemainsNavigable() = scenario { repo, model ->
        repo.expired = true
        model.open("pinned"); advanceUntilIdle()
        assertTrue(model.state.value.expired)
        repo.expired = false
        model.open("pinned"); advanceUntilIdle()
        repeat(3) { model.move(true); advanceUntilIdle() }
        assertEquals(SceneContent.Unsupported, model.state.value.scene?.content)
    }
    @Test fun sameIdentitySurvivesRecreationAndDifferentIdentityClearsInk() = scenario { _, model ->
        model.bindIdentity("owner")
        model.open("pinned"); advanceUntilIdle()
        model.ink(listOf(listOf(InkPoint(.2f, .3f))))
        model.bindIdentity("owner")
        assertNotNull(model.state.value.bundle)
        assertFalse(model.state.value.ink.isEmpty())
        model.bindIdentity("other")
        assertNull(model.state.value.bundle)
        assertTrue(model.state.value.ink.isEmpty())
    }
    @Test fun missingBundleCanRetryAndEmptyBundleIsSafe() = scenario { repo, model ->
        repo.failBundle = true
        model.open("pinned"); advanceUntilIdle()
        assertNull(model.state.value.bundle)
        assertEquals(R.string.lesson_load_error, model.state.value.error)
        repo.failBundle = false
        repo.bundle = repo.bundle.copy(scenes = emptyList())
        model.retry(); advanceUntilIdle()
        assertTrue(model.state.value.bundle!!.scenes.isEmpty())
        assertTrue(repo.saves.isEmpty())
        assertFalse(model.state.value.saving)
        model.move(true); advanceUntilIdle()
        model.exit(); advanceUntilIdle()
        assertTrue(model.state.value.closed)
    }
}
