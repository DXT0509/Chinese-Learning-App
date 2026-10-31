package com.example.chineselearningapp

import androidx.lifecycle.SavedStateHandle
import com.example.chineselearningapp.domain.repository.*
import com.example.chineselearningapp.feature.review.*
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.Assert.*
import org.junit.Test
import java.io.IOException

@OptIn(ExperimentalCoroutinesApi::class)
class ReviewFlowOptimizationTest {
    private class Repository : ReviewRepository {
        var dashboards = 0; var dues = 0; var selections = 0; var starts = 0; var finals = 0
        val attempts = mutableMapOf<String, MutableList<ReviewFeedback>>()
        val requests = mutableListOf<ReviewSubmission>()
        val keys = mutableListOf<String>()
        var nextGate: CompletableDeferred<Unit>? = null
        var loseNext = false
        var loseSubmission = false
        override suspend fun dashboard(): ReviewDashboard { dashboards++; return ReviewDashboard(3, 3, 0, true) }
        override suspend fun due(): List<ReviewProgress> { dues++; return emptyList() }
        override suspend fun targets() = ReviewTargets((1..3).map { ReviewTarget("word-$it", true) }, emptyList())
        override suspend fun sessionTargets(): ReviewTargets { selections++; return targets() }
        override suspend fun progress(savedId: String) = error("Unnecessary progress request")
        override suspend fun start(savedId: String, requestId: String): ReviewStart {
            starts++; keys += requestId
            attempts.getOrPut(requestId) { mutableListOf() }
            if (starts > 1) { nextGate?.await(); if (loseNext) { loseNext = false; throw IOException() } }
            return ReviewStart(requestId, true)
        }
        override suspend fun question(attemptId: String): ReviewStage {
            val feedback = attempts.getValue(attemptId)
            val stage = listOf("HANZI", "PINYIN").firstOrNull { code -> feedback.none { it.stage == code } }
            val questions = mapOf("HANZI" to ReviewQuestion("TEXT", "con ngựa", null, emptyList(), 1),
                "PINYIN" to ReviewQuestion("TEXT", "con ngựa", null, emptyList()),
                "POS" to ReviewQuestion("SINGLE_SELECT", "Chọn từ loại", null, listOf("noun", "verb")))
            return ReviewStage(attemptId, stage, if (stage == null) "READY_TO_FINALIZE" else "IN_PROGRESS", "2099-01-01T00:00:00Z",
                questions[stage], feedback.toList(), emptyList(), questions)
        }
        override suspend fun submit(attemptId: String, submission: ReviewSubmission) {
            requests += submission
            val feedback = attempts.getValue(attemptId)
            if (feedback.none { it.stage == submission.stage }) feedback += ReviewFeedback(submission.stage,
                submission.text != "wrong", false, listOf("sealed-stage-answer"))
            if (loseSubmission) { loseSubmission = false; throw IOException() }
        }
        override suspend fun finalize(attemptId: String): ReviewResult {
            check(attempts.getValue(attemptId).size == 2)
            finals++
            return ReviewResult("PASS", 1, "later", true, 0)
        }
    }
    private fun scenario(block: suspend TestScope.(Repository) -> Unit) = runTest {
        Dispatchers.setMain(StandardTestDispatcher(testScheduler))
        try { block(Repository()) } finally { Dispatchers.resetMain() }
    }
    private fun copy(handle: SavedStateHandle) = SavedStateHandle(handle.keys().associateWith { handle.get<Any?>(it) })
    private suspend fun TestScope.complete(model: ReviewViewModel) {
        model.submit("马", emptyList(), sampleReviewInk()); advanceUntilIdle(); model.continueReview()
        model.submit("ma3", emptyList(), sampleReviewInk()); advanceUntilIdle(); model.continueReview()
        advanceUntilIdle()
    }
    @Test fun navigateSkipReturnAndRestoreAllDraftsWithoutGrading() = scenario { repo ->
        val saved = SavedStateHandle(); val model = ReviewViewModel(repo, saved, "owner")
        advanceUntilIdle(); model.start(); advanceUntilIdle()
        model.editDraft("马", emptyList()); model.selectStage("PINYIN"); model.editDraft("ma3", emptyList())
        model.selectStage("POS"); assertEquals("PINYIN", model.state.value.selectedStage)
        model.selectStage("HANZI"); assertEquals("马", model.state.value.draftText)
        model.selectStage("PINYIN"); assertEquals("ma3", model.state.value.draftText)
        val restored = ReviewViewModel(repo, copy(saved), "owner"); advanceUntilIdle()
        assertEquals("ma3", restored.state.value.draftText)
        restored.selectStage("POS"); assertEquals("PINYIN", restored.state.value.selectedStage)
        assertTrue(repo.requests.isEmpty()); assertEquals(0, repo.finals)
    }
    @Test fun draftsQueueFreelyButSubmitInCanonicalOrderAndFirstResultIsSealed() = scenario { repo ->
        val model = ReviewViewModel(repo, SavedStateHandle(), "owner"); advanceUntilIdle(); model.start(); advanceUntilIdle()
        model.selectStage("PINYIN"); model.submit("ma3", emptyList(), sampleReviewInk())
        assertEquals(setOf("PINYIN"), model.state.value.queuedStages); assertTrue(repo.requests.isEmpty())
        model.selectStage("HANZI"); model.submit("wrong", emptyList(), sampleReviewInk()); advanceUntilIdle()
        assertEquals(listOf("HANZI", "PINYIN"), repo.requests.map { it.stage })
        assertFalse(model.state.value.stage!!.feedback.first().firstCorrect!!)
        model.submit("马", emptyList(), sampleReviewInk()); advanceUntilIdle(); assertEquals(2, repo.requests.size)
        assertEquals("READY_TO_FINALIZE", model.state.value.stage!!.status)
    }
    @Test fun prefetchedContinueHasNoNetworkAndNoQueueReloadOrDuplicateFinalization() = scenario { repo ->
        val saved = SavedStateHandle(); val model = ReviewViewModel(repo, saved, "owner")
        advanceUntilIdle(); model.start(); advanceUntilIdle(); complete(model)
        assertEquals(2, repo.starts); assertEquals(1, repo.finals)
        val order = saved.get<ArrayList<String>>("queue")!!.toList()
        val starts = repo.starts
        val before = System.nanoTime(); model.next(); advanceUntilIdle()
        println("PHASE44 isolated ViewModel ready-prefetch Continue ms=" + (System.nanoTime() - before) / 1_000_000.0)
        assertEquals(starts, repo.starts); assertFalse(model.state.value.loading)
        assertNotNull(model.state.value.stage); assertEquals(order, saved.get<ArrayList<String>>("queue"))
        assertEquals(1, repo.dashboards); assertEquals(0, repo.dues); assertEquals(1, repo.selections)
        assertEquals(1, repo.finals)
    }
    @Test fun continueWhilePrefetchRunsAwaitsSameAttempt() = scenario { repo ->
        val model = ReviewViewModel(repo, SavedStateHandle(), "owner"); advanceUntilIdle(); model.start(); advanceUntilIdle()
        repo.nextGate = CompletableDeferred(); complete(model)
        model.next(); runCurrent(); assertTrue(model.state.value.loading); assertEquals(2, repo.starts)
        model.submit("马", emptyList(), sampleReviewInk()); assertEquals(2, repo.requests.size)
        repo.nextGate!!.complete(Unit); advanceUntilIdle(); assertEquals(2, repo.starts)
        assertNotNull(model.state.value.stage)
    }
    @Test fun lostPrefetchResponseReusesCreationKeyAndRestoresFinishedResult() = scenario { repo ->
        val saved = SavedStateHandle(); val model = ReviewViewModel(repo, saved, "owner")
        advanceUntilIdle(); model.start(); advanceUntilIdle(); repo.loseNext = true; complete(model)
        assertNull(model.state.value.error)
        val restored = ReviewViewModel(repo, copy(saved), "owner"); advanceUntilIdle()
        assertNotNull(restored.state.value.result); assertEquals(1, repo.finals)
        restored.next(); advanceUntilIdle()
        assertEquals(2, repo.attempts.size); assertEquals(1, repo.keys.drop(1).distinct().size)
        assertEquals(1, repo.finals); assertNotNull(restored.state.value.stage)
    }
    @Test fun interruptedCanonicalFlushKeepsPendingKeyAndQueuedLaterDrafts() = scenario { repo ->
        val saved = SavedStateHandle(); val model = ReviewViewModel(repo, saved, "owner")
        advanceUntilIdle(); model.start(); advanceUntilIdle()
        model.selectStage("PINYIN"); model.submit("ma3", emptyList(), sampleReviewInk())
        model.selectStage("HANZI"); repo.loseSubmission = true; model.submit("马", emptyList(), sampleReviewInk()); advanceUntilIdle()
        val restored = ReviewViewModel(repo, copy(saved), "owner"); advanceUntilIdle()
        assertEquals(repo.requests[0], repo.requests[1])
        assertEquals(listOf("HANZI", "HANZI", "PINYIN"), repo.requests.map { it.stage })
        assertEquals(2, restored.state.value.stage!!.feedback.size)
        assertEquals(1, repo.attempts.size)
    }
}
