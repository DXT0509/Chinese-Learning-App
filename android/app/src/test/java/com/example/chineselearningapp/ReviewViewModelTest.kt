package com.example.chineselearningapp

import androidx.lifecycle.SavedStateHandle
import com.example.chineselearningapp.domain.repository.*
import com.example.chineselearningapp.feature.review.*
import com.example.chineselearningapp.feature.auth.data.SessionExpired
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.Assert.*
import org.junit.Test
import retrofit2.HttpException
import retrofit2.Response
import okhttp3.ResponseBody.Companion.toResponseBody
import java.io.IOException

@OptIn(ExperimentalCoroutinesApi::class)
class ReviewViewModelTest {
    private class Repository : ReviewRepository {
        var dashboardCalls = 0
        var dueCalls = 0
        var starts = 0
        var creations = 0
        var loseCreationResponse = false
        val startKeys = mutableListOf<String>()
        private val created = mutableMapOf<String, ReviewStart>()
        var finalizations = 0
        var stageIndex = 0
        var failStage: Int? = null
        var error: Exception? = null
        var startError: Exception? = null
        var submitError: Exception? = null
        var finalizeError: Exception? = null
        var gate: CompletableDeferred<Unit>? = null
        var skipPos = false
        var sessionItems: List<ReviewTarget>? = null
        val startedIds = mutableListOf<String>()
        var submitted = mutableListOf<ReviewSubmission>()
        private val feedback = mutableListOf<ReviewFeedback>()
        override suspend fun dashboard(): ReviewDashboard {
            dashboardCalls++; error?.let { throw it }
            return ReviewDashboard(5, 2, 0, true, listOf(1, 0, 2, 0, 0, 2).mapIndexed { level, count -> ReviewMasteryCount(level, count) })
        }
        override suspend fun due(): List<ReviewProgress> { dueCalls++; return listOf(ReviewProgress("saved", 2, "server-time")) }
        override suspend fun targets() = ReviewTargets(if (finalizations == 0) listOf(ReviewTarget("saved", true), ReviewTarget("later", false)) else emptyList(),
            listOf(ReviewExclusion("excluded", "REVIEWED_POLICY_REQUIRED")))
        override suspend fun progress(savedId: String) = ReviewProgress(savedId, 2, "server-time")
        override suspend fun sessionTargets() = sessionItems?.let { ReviewTargets(it, emptyList()) } ?: targets()
        override suspend fun start(savedId: String, requestId: String): ReviewStart {
            startedIds += savedId
            starts++; startKeys += requestId; startError?.let { throw it }
            val result = created.getOrPut(requestId) { creations++; ReviewStart("attempt", true) }
            if (loseCreationResponse) { loseCreationResponse = false; throw IOException() }
            return result
        }
        override suspend fun question(attemptId: String): ReviewStage {
            error?.let { throw it }
            val stage = listOf("HANZI", "PINYIN").getOrNull(stageIndex)
            val ready = stage == null || skipPos && stage == "POS"
            return ReviewStage(attemptId, if (ready) null else stage, if (finalizations > 0) "COMPLETED" else if (ready) "READY_TO_FINALIZE" else "IN_PROGRESS", "expiry",
                if (ready) null else ReviewQuestion(if (stage == "POS") "MULTI_SELECT" else "TEXT", "Complete prompt with all cues", null, listOf("noun", "verb")),
                feedback.toList(), if (skipPos) listOf("not applicable") else emptyList())
        }
        override suspend fun submit(attemptId: String, submission: ReviewSubmission) {
            submitted += submission; gate?.await(); submitError?.let { throw it }
            if (feedback.none { it.stage == submission.stage }) {
                feedback += ReviewFeedback(submission.stage, stageIndex != failStage, false, listOf("answered-stage-only")); stageIndex++
            }
        }
        override suspend fun finalize(attemptId: String): ReviewResult {
            finalizeError?.let { throw it }
            finalizations++
            return ReviewResult(if (failStage == null) "PASS" else "FAIL", if (failStage == null) 3 else 0, "server-next-time", true, previousMastery = 5)
        }
    }
    private fun scenario(test: suspend TestScope.(Repository) -> Unit) = runTest {
        Dispatchers.setMain(StandardTestDispatcher(testScheduler))
        try { test(Repository()) } finally { Dispatchers.resetMain() }
    }
    private fun http(code: Int) = HttpException(Response.error<Any>(code, "{}".toResponseBody()))
    @Test fun transportTimeoutAndServerErrorsAreDistinguished() {
        assertEquals(ReviewError.Network, reviewFailure(IOException("secret")))
        assertEquals(ReviewError.Timeout, reviewFailure(java.net.SocketTimeoutException("secret")))
        assertEquals(ReviewError.Server, reviewFailure(http(500)))
        assertEquals(ReviewError.Response, reviewFailure(IllegalStateException("secret")))
        assertEquals(ReviewError.Response, reviewFailure(com.google.gson.stream.MalformedJsonException("secret")))
    }
    @Test fun dashboardUsesServerCountsAndOnlyDueAuthorizedTargets() = scenario { repo ->
        val model = ReviewViewModel(repo, SavedStateHandle(), "owner"); advanceUntilIdle()
        assertEquals(2, model.state.value.dashboard!!.due)
        assertEquals(listOf("saved"), model.state.value.targets.map { it.savedId })
        assertEquals("excluded", model.state.value.exclusions.single().savedId)
        assertEquals(0, repo.dueCalls)
        model.start(); advanceUntilIdle()
        assertEquals("Complete prompt with all cues", model.state.value.stage!!.question!!.prompt)
        assertNull(model.state.value.previousMastery)
        assertEquals(listOf(1, 0, 2, 0, 0, 2), model.state.value.dashboard!!.masteryDistribution!!.map { it.count })
    }
    @Test fun allStagesContinueAfterEachPossibleMistakeWithoutDashboardReload() = scenario { repo ->
        for (wrongStage in listOf(null, 0, 1)) {
            repo.stageIndex = 0; repo.failStage = wrongStage; repo.finalizations = 0
            // Each independent attempt uses a fresh fake to avoid sharing feedback.
            val fake = Repository().also { it.failStage = wrongStage }
            val model = ReviewViewModel(fake, SavedStateHandle(), "owner"); advanceUntilIdle()
            model.start(); advanceUntilIdle()
            model.submit("汉", emptyList(), sampleReviewInk()); advanceUntilIdle()
            assertTrue(model.state.value.feedbackVisible)
            model.submit("duplicate", emptyList(), sampleReviewInk()); assertEquals(1, fake.submitted.size)
            model.continueReview(); model.submit("han4", emptyList(), sampleReviewInk()); advanceUntilIdle()
            model.continueReview(); advanceUntilIdle()
            assertEquals(if (wrongStage == null) "PASS" else "FAIL", model.state.value.result!!.outcome)
            assertEquals("server-next-time", model.state.value.result!!.nextReviewAt)
            assertEquals(5, model.state.value.previousMastery)
            assertEquals(1, fake.dashboardCalls)
            assertEquals(1, fake.dashboardCalls); assertEquals(1, model.state.value.completed)
            assertEquals(if (wrongStage == null) 1 else 0, model.state.value.passed)
            assertEquals(if (wrongStage == null) 0 else 1, model.state.value.failed)
        }
    }
    @Test fun doubleTapAndNetworkRetryKeepExactSubmissionAfterRecreation() = scenario { repo ->
        val handle = SavedStateHandle()
        val model = ReviewViewModel(repo, handle, "owner"); advanceUntilIdle(); model.start(); advanceUntilIdle()
        repo.gate = CompletableDeferred(); repo.submitError = IOException()
        model.submit("汉", emptyList(), sampleReviewInk()); model.submit("different", emptyList(), sampleReviewInk()); runCurrent()
        assertEquals(1, repo.submitted.size)
        repo.gate!!.complete(Unit); advanceUntilIdle()
        assertEquals(ReviewError.Network, model.state.value.error)
        repo.submitError = null
        val restored = ReviewViewModel(repo, handle, "owner"); advanceUntilIdle()
        assertEquals(repo.submitted.first(), repo.submitted.last()); assertEquals(1, repo.starts)
        assertTrue(restored.state.value.feedbackVisible)
        restored.onResume(); advanceUntilIdle(); assertEquals(1, repo.starts)
        restored.leave(); advanceUntilIdle(); restored.resume(); advanceUntilIdle()
        assertEquals(1, repo.starts)
    }
    @Test fun skippingAndReadyStateAfterRecreationCanFinalize() = scenario { repo ->
        repo.skipPos = true
        val handle = SavedStateHandle(); val model = ReviewViewModel(repo, handle, "owner")
        advanceUntilIdle(); model.start(); advanceUntilIdle()
        model.submit("汉", emptyList(), sampleReviewInk()); advanceUntilIdle(); model.continueReview()
        model.submit("han4", emptyList(), sampleReviewInk()); advanceUntilIdle()
        val restored = ReviewViewModel(repo, handle, "owner"); advanceUntilIdle()
        assertNull(restored.state.value.stage!!.stage); assertEquals(2, repo.submitted.size)
        restored.continueReview(); advanceUntilIdle(); assertNotNull(restored.state.value.result)
        assertEquals(2, repo.submitted.size)
    }
    @Test fun expiryAuthenticationAndCreationRetryKeepSameIdentity() = scenario { repo ->
        val model = ReviewViewModel(repo, SavedStateHandle(), "owner"); advanceUntilIdle()
        repo.startError = IOException(); model.start(); advanceUntilIdle()
        assertEquals(ReviewError.Network, model.state.value.error)
        model.retry(); model.onResume(); advanceUntilIdle(); assertEquals(2, repo.starts)
        assertEquals(1, repo.startKeys.distinct().size)
        repo.startError = null; model.retry(); advanceUntilIdle(); assertEquals(1, repo.creations)
        repo.error = http(410); model.retry(); advanceUntilIdle()
        assertEquals(ReviewError.Expired, model.state.value.error); assertEquals(0, repo.finalizations)
        repo.error = SessionExpired(); model.retry(); advanceUntilIdle(); assertTrue(model.state.value.signedOut)
    }
    @Test fun identityChangeDiscardsAttemptAndPendingAnswer() = scenario { repo ->
        val handle = SavedStateHandle(mapOf("owner" to "other", "attempt" to "foreign", "key" to "secret"))
        val model = ReviewViewModel(repo, handle, "owner"); advanceUntilIdle()
        assertFalse(model.hasAttempt()); assertNull(handle.get<String>("key")); assertFalse(model.state.value.sessionOpen)
    }
    @Test fun conflictReconcilesWithoutResubmittingAndInvalidAnswerCanBeEdited() = scenario { repo ->
        val model = ReviewViewModel(repo, SavedStateHandle(), "owner"); advanceUntilIdle(); model.start(); advanceUntilIdle()
        repo.submitError = http(409); model.submit("汉", emptyList(), sampleReviewInk()); advanceUntilIdle()
        assertNull(model.state.value.error); assertEquals(1, repo.starts)
        repo.submitError = http(422); model.submit("汉", emptyList(), sampleReviewInk()); advanceUntilIdle()
        assertEquals(ReviewError.Invalid, model.state.value.error)
        repo.submitError = null; model.retry(); advanceUntilIdle(); model.submit("字", emptyList(), sampleReviewInk()); advanceUntilIdle()
        assertEquals("字", repo.submitted.last().text)
    }
    @Test fun finalizationRetryAndCompletedRestorationDoNotCountTwice() = scenario { repo ->
        repo.skipPos = true
        val saved = SavedStateHandle()
        val model = ReviewViewModel(repo, saved, "owner"); advanceUntilIdle(); model.start(); advanceUntilIdle()
        model.submit("汉", emptyList(), sampleReviewInk()); advanceUntilIdle(); model.continueReview()
        model.submit("han4", emptyList(), sampleReviewInk()); advanceUntilIdle()
        repo.finalizeError = IOException(); model.continueReview(); advanceUntilIdle()
        assertEquals(ReviewError.Network, model.state.value.error); assertNull(model.state.value.result)
        repo.finalizeError = null; model.retry(); advanceUntilIdle(); model.continueReview(); advanceUntilIdle()
        assertEquals(1, model.state.value.completed)
        val restored = ReviewViewModel(repo, saved, "owner"); advanceUntilIdle()
        restored.continueReview(); advanceUntilIdle()
        assertEquals(1, restored.state.value.completed); assertEquals(1, repo.starts)
    }
    @Test fun dashboardFailureIsRetryableAndInitialLoadingBlocksStart() = scenario { repo ->
        repo.error = IOException()
        val model = ReviewViewModel(repo, SavedStateHandle(), "owner")
        assertTrue(model.state.value.loading); model.start(); advanceUntilIdle()
        assertEquals(0, repo.starts); assertEquals(ReviewError.Network, model.state.value.error)
        repo.error = null; model.retry(); advanceUntilIdle()
        assertNull(model.state.value.error); assertNotNull(model.state.value.dashboard)
    }
    @Test fun lostQuestionAfterAcceptedAnswerReplaysKeyWithoutReplacingFirstResult() = scenario { repo ->
        val model = ReviewViewModel(repo, SavedStateHandle(), "owner"); advanceUntilIdle(); model.start(); advanceUntilIdle()
        repo.failStage = 0; repo.error = IOException()
        model.submit("wrong", emptyList(), sampleReviewInk()); advanceUntilIdle()
        assertEquals(ReviewError.Network, model.state.value.error)
        repo.error = null; model.retry(); advanceUntilIdle()
        assertEquals(repo.submitted.first(), repo.submitted.last())
        assertEquals(1, model.state.value.stage!!.feedback.size)
        assertEquals(false, model.state.value.stage!!.feedback.single().firstCorrect)
        assertEquals("PINYIN", model.state.value.stage!!.stage)
    }
    @Test fun serverErrorDuringCreationRetriesSameKey() = scenario { repo ->
        val model = ReviewViewModel(repo, SavedStateHandle(), "owner"); advanceUntilIdle()
        repo.startError = http(503); model.start(); advanceUntilIdle()
        assertEquals(ReviewError.Server, model.state.value.error)
        model.retry(); advanceUntilIdle(); assertEquals(2, repo.starts)
        assertEquals(1, repo.startKeys.distinct().size)
        repo.startError = null; model.retry(); advanceUntilIdle(); assertEquals(1, repo.creations)
    }
    @Test fun lostCreationResponseResumesAfterRecreationWithoutSecondAttempt() = scenario { repo ->
        val saved = SavedStateHandle()
        val model = ReviewViewModel(repo, saved, "owner"); advanceUntilIdle()
        repo.loseCreationResponse = true; model.start(); model.start(); advanceUntilIdle()
        assertEquals(1, repo.creations); assertEquals(ReviewError.Network, model.state.value.error)
        val restoredState = SavedStateHandle(saved.keys().associateWith { saved.get<Any?>(it) })
        val restored = ReviewViewModel(repo, restoredState, "owner"); advanceUntilIdle()
        assertEquals(1, repo.creations); assertEquals(2, repo.starts)
        assertEquals(1, repo.startKeys.distinct().size)
        assertEquals("attempt", restored.state.value.stage!!.attemptId)
        assertNull(restored.state.value.error)
    }
    @Test fun legacyAmbiguousCreationStillRequiresAbandonment() = scenario { repo ->
        val model = ReviewViewModel(repo, SavedStateHandle(mapOf("owner" to "owner", "starting" to true)), "owner")
        advanceUntilIdle()
        assertEquals(ReviewError.StartUnknown, model.state.value.error)
        model.retry(); advanceUntilIdle(); assertEquals(0, repo.starts)
    }
    @Test fun randomizedQueueIsUniqueAndRestoredWithoutReselection() = scenario { repo ->
        repo.sessionItems = (1..20).map { ReviewTarget("word-$it", true) } + ReviewTarget("word-1", true) + ReviewTarget("later", false)
        val saved = SavedStateHandle()
        val model = ReviewViewModel(repo, saved, "owner"); advanceUntilIdle(); model.start(); advanceUntilIdle()
        val queue = saved.get<ArrayList<String>>("queue")!!.toList()
        assertEquals(20, queue.size); assertEquals(20, queue.distinct().size)
        assertEquals((1..20).map { "word-$it" }.toSet(), queue.toSet())
        val restoredHandle = SavedStateHandle(saved.keys().associateWith { saved.get<Any?>(it) })
        val restored = ReviewViewModel(repo, restoredHandle, "owner")
        advanceUntilIdle(); restored.onResume(); advanceUntilIdle()
        assertEquals(1, repo.starts); assertEquals(queue.first(), repo.startedIds.single())
        assertEquals(queue, restoredHandle.get<ArrayList<String>>("queue"))
        assertEquals(20, restored.state.value.sessionSize)
    }
    @Test fun independentSessionsCanHaveDifferentOrders() = scenario { repo ->
        repo.sessionItems = (1..20).map { ReviewTarget("word-$it", true) }
        val orders = (1..5).map {
            val saved = SavedStateHandle(); val model = ReviewViewModel(repo, saved, "owner", kotlin.random.Random(it))
            advanceUntilIdle(); model.start(); advanceUntilIdle()
            saved.get<ArrayList<String>>("queue")!!.toList()
        }
        assertTrue(orders.distinct().size > 1)
    }
    @Test fun summaryUsesAuthoritativeResultsAndRestoresWithoutCountingAgain() = scenario { repo ->
        repo.skipPos = true
        val saved = SavedStateHandle(); val model = ReviewViewModel(repo, saved, "owner")
        advanceUntilIdle(); model.start(); advanceUntilIdle()
        model.submit("学", emptyList(), sampleReviewInk()); advanceUntilIdle(); model.continueReview()
        model.submit("xue2", emptyList(), sampleReviewInk()); advanceUntilIdle(); model.continueReview(); advanceUntilIdle()
        assertEquals(1, model.state.value.passed); assertEquals(0, model.state.value.failed)
        assertEquals(-2, model.state.value.masteryChange)
        model.next(); advanceUntilIdle(); assertTrue(model.state.value.summary)
        val restored = ReviewViewModel(repo, SavedStateHandle(saved.keys().associateWith { saved.get<Any?>(it) }), "owner")
        advanceUntilIdle(); assertTrue(restored.state.value.summary); assertEquals(1, restored.state.value.completed)
        assertEquals(1, repo.finalizations)
        restored.leave(); advanceUntilIdle(); assertFalse(restored.state.value.sessionOpen)
    }
    @Test fun unavailableWordCanBeSkippedWithoutReorderingRemainder() = scenario { repo ->
        repo.sessionItems = (1..3).map { ReviewTarget("word-$it", true) }
        val saved = SavedStateHandle(); val model = ReviewViewModel(repo, saved, "owner")
        advanceUntilIdle(); repo.startError = http(409); model.start(); advanceUntilIdle()
        val queue = saved.get<ArrayList<String>>("queue")!!.toList()
        repo.startError = null; model.restart(); advanceUntilIdle()
        assertEquals(queue.take(2), repo.startedIds)
        assertEquals(queue.drop(1), saved.get<ArrayList<String>>("queue"))
        assertEquals(1, model.state.value.skippedCount); assertEquals(0, repo.finalizations)
    }
}
