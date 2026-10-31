package com.example.chineselearningapp

import androidx.lifecycle.SavedStateHandle
import com.example.chineselearningapp.domain.repository.*
import com.example.chineselearningapp.feature.review.*
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.Assert.*
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class ReviewDailyBudgetTest {
    private class Repository : ReviewRepository {
        val beyond = mutableListOf<Boolean>()
        val totals = mutableListOf<Long>()
        var budget = 1195
        var stages = 0
        var finals = 0
        var emptyPlan = false
        val plans = mutableMapOf<String, ReviewTargets>()
        val planKeys = mutableListOf<String>()
        override suspend fun dashboard() = ReviewDashboard(2, 2, 0, true,
            dailyReview = DailyReviewBudget(activeSeconds = budget, overdueCount = 2))
        override suspend fun targets() = error("Daily planner must replace catalog pagination")
        override suspend fun dailyPlan(requestId: String, beyond: Boolean): ReviewTargets {
            this.beyond += beyond
            planKeys += requestId
            return plans.getOrPut(requestId) {
                ReviewTargets(if (emptyPlan) emptyList() else listOf(ReviewTarget("one", true), ReviewTarget("two", true)), emptyList())
            }
        }
        override suspend fun activeTime(attemptId: String, activeMs: Long): Long { totals += activeMs; return activeMs }
        override suspend fun due() = emptyList<ReviewProgress>()
        override suspend fun progress(savedId: String) = error("No per-word progress read")
        override suspend fun start(savedId: String, requestId: String) = ReviewStart(requestId, true)
        override suspend fun question(attemptId: String) = ReviewStage(attemptId,
            listOf("HANZI", "PINYIN").getOrNull(stages), if (stages == 2) "READY_TO_FINALIZE" else "IN_PROGRESS",
            "2099-01-01T00:00:00Z", ReviewQuestion("TEXT", "meaning", null, emptyList(), 1),
            (0 until stages).map { ReviewFeedback(listOf("HANZI", "PINYIN")[it], true, false, emptyList()) }, emptyList())
        override suspend fun submit(attemptId: String, submission: ReviewSubmission) { stages++ }
        override suspend fun finalize(attemptId: String): ReviewResult { finals++; return ReviewResult("PASS", 1, "later", true, 0) }
    }
    @Test fun emptyPlanCanStartAfterSavingWordsWithoutReusingItsKey() = runTest {
        Dispatchers.setMain(StandardTestDispatcher(testScheduler))
        try {
            val repo = Repository().also { it.emptyPlan = true }
            val model = ReviewViewModel(repo, SavedStateHandle(), "owner")
            advanceUntilIdle(); model.start(); advanceUntilIdle()
            assertFalse(model.state.value.sessionOpen)
            assertEquals(ReviewError.EmptyPlan, model.state.value.error)
            repo.emptyPlan = false
            model.start(); advanceUntilIdle()
            assertNotEquals(repo.planKeys[0], repo.planKeys[1])
            assertTrue(model.state.value.sessionOpen)
            assertNotNull(model.state.value.stage)
        } finally { Dispatchers.resetMain() }
    }
    @Test fun refreshClearsRestoredEmptyPlanBeforeStartingNewWords() = runTest {
        Dispatchers.setMain(StandardTestDispatcher(testScheduler))
        try {
            val repo = Repository()
            repo.plans["old-empty-plan"] = ReviewTargets(emptyList(), emptyList())
            val saved = SavedStateHandle(mapOf("owner" to "owner", "planKey" to "old-empty-plan"))
            val model = ReviewViewModel(repo, saved, "owner")
            advanceUntilIdle(); model.onResume(); advanceUntilIdle()
            model.start(); advanceUntilIdle()
            assertNotEquals("old-empty-plan", repo.planKeys.single())
            assertTrue(model.state.value.sessionOpen)
            assertNotNull(model.state.value.stage)
        } finally { Dispatchers.resetMain() }
    }
    @Test fun targetAllowsFinishingBothStagesAndExplicitContinuation() = runTest {
        Dispatchers.setMain(StandardTestDispatcher(testScheduler))
        try {
            val repo = Repository(); val model = ReviewViewModel(repo, SavedStateHandle(), "owner")
            advanceUntilIdle(); model.start(); advanceUntilIdle()
            model.activeTick(5000)
            assertEquals(1200, model.state.value.dashboard!!.dailyReview!!.activeSeconds)
            assertNotNull(model.state.value.stage)
            model.submit("学", emptyList(), sampleReviewInk()); advanceUntilIdle(); model.continueReview()
            model.submit("xue2", emptyList()); advanceUntilIdle(); model.continueReview(); advanceUntilIdle()
            assertEquals(1, repo.finals)
            model.next(); assertTrue(model.state.value.summary)
            assertEquals(listOf(false), repo.beyond)
            repo.stages = 0
            model.continueBeyondTarget(); advanceUntilIdle()
            assertEquals(listOf(false, true), repo.beyond)
        } finally { Dispatchers.resetMain() }
    }
    @Test fun timingExcludesDashboardNetworkWindowsAndPreservesAbsoluteReceiptOnRecovery() = runTest {
        Dispatchers.setMain(StandardTestDispatcher(testScheduler))
        try {
            val repo = Repository(); val saved = SavedStateHandle()
            val model = ReviewViewModel(repo, saved, "owner")
            advanceUntilIdle(); model.activeTick(5000); assertTrue(repo.totals.isEmpty())
            model.start(); advanceUntilIdle()
            val staleWindow = model.timingWindow()
            model.retry(); advanceUntilIdle()
            model.activeTick(5000, staleWindow); assertTrue(repo.totals.isEmpty())
            model.activeTick(5000); assertEquals(listOf(5000L), repo.totals)
            val restored = ReviewViewModel(repo, saved, "owner"); advanceUntilIdle()
            restored.activeTick(5000); assertEquals(listOf(5000L, 10000L), repo.totals)
            restored.leave(); advanceUntilIdle(); restored.activeTick(5000)
            assertEquals(2, repo.totals.size)
        } finally { Dispatchers.resetMain() }
    }
}
