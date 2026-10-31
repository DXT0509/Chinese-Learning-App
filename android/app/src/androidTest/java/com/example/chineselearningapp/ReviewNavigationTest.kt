package com.example.chineselearningapp

import androidx.activity.ComponentActivity
import androidx.compose.runtime.mutableStateOf
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import com.example.chineselearningapp.core.navigation.*
import com.example.chineselearningapp.domain.repository.*
import com.example.chineselearningapp.feature.auth.*
import com.example.chineselearningapp.ui.theme.ChineseLearningAppTheme
import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test

/** Entirely fake review data: no learner schedules or live API calls. */
class ReviewNavigationTest {
    @get:Rule val compose = createAndroidComposeRule<ComponentActivity>()
    private class Repository : ReviewRepository {
        var starts = 0
        override suspend fun dashboard() = ReviewDashboard(3, 1, 0, true,
            (0..5).map { ReviewMasteryCount(it, if (it == 4) 3 else 0) })
        override suspend fun due() = listOf(ReviewProgress("saved", 0, "server-time"))
        override suspend fun targets() = ReviewTargets(listOf(ReviewTarget("saved", true)), emptyList())
        override suspend fun progress(savedId: String) = ReviewProgress(savedId, 0, "server-time")
        override suspend fun start(savedId: String, requestId: String): ReviewStart { starts++; return ReviewStart("attempt", true) }
        override suspend fun question(attemptId: String) = ReviewStage(attemptId, "HANZI", "IN_PROGRESS", "expiry",
            ReviewQuestion("TEXT", "Nghĩa: học sinh. Hán-Việt: học sinh. Số chữ: 2.", null, emptyList()), emptyList(), emptyList())
        override suspend fun submit(attemptId: String, submission: ReviewSubmission) = Unit
        override suspend fun finalize(attemptId: String) = ReviewResult("PASS", 0, "server-time", false)
    }
    @Test fun tabNavigationAndBackResumeSameAttemptAndLogoutClearsIt() {
        val repo = Repository()
        val session = mutableStateOf(SessionState(status = SessionStatus.SignedIn, account = Account("owner", "fixture@example.com"), contentLoaded = true))
        compose.setContent {
            ChineseLearningAppTheme {
                SessionNavigation(session.value, SessionActions(), reviewRepository = repo)
            }
        }
        compose.onNodeWithTag("tab_Review").performClick()
        compose.onNodeWithText("Mức 4: 3 từ").assertExists()
        compose.onNodeWithText("Ôn tập ngay").performScrollTo().performClick()
        compose.onNodeWithText("Nghĩa: học sinh. Hán-Việt: học sinh. Số chữ: 2.").assertExists()
        compose.onNodeWithTag("tab_Home").performClick()
        compose.onNodeWithTag("tab_Review").performClick()
        compose.runOnIdle { assertEquals(1, repo.starts) }
        compose.activityRule.scenario.onActivity { it.onBackPressedDispatcher.onBackPressed() }
        compose.onNodeWithTag("tab_Review").performClick()
        compose.runOnIdle { assertEquals(1, repo.starts) }
        compose.onNodeWithText("Nghĩa: học sinh. Hán-Việt: học sinh. Số chữ: 2.").assertExists()
        compose.runOnIdle { session.value = SessionState(status = SessionStatus.SignedOut) }
        compose.onNodeWithText("Nghĩa: học sinh. Hán-Việt: học sinh. Số chữ: 2.").assertDoesNotExist()
        compose.runOnIdle { session.value = SessionState(status = SessionStatus.SignedIn, account = Account("other", "other@example.com"), contentLoaded = true) }
        compose.onNodeWithTag("tab_Review").performClick()
        compose.onNodeWithText("Ôn tập ngay").assertExists()
        compose.onNodeWithText("Tiếp tục lượt ôn").assertDoesNotExist()
    }
    @Test fun resultsRenderAuthoritativeMasteryInsteadOfEarlierProgressRead() {
        lateinit var model: com.example.chineselearningapp.feature.review.ReviewViewModel
        compose.runOnUiThread {
            model = com.example.chineselearningapp.feature.review.ReviewViewModel(Repository(), androidx.lifecycle.SavedStateHandle(), "owner")
        }
        compose.setContent {
            ChineseLearningAppTheme {
                com.example.chineselearningapp.feature.review.ReviewScreen(
                    com.example.chineselearningapp.feature.review.ReviewUiState(sessionOpen = true,
                        previousMastery = 1, result = ReviewResult("FAIL", 3, "server-time", true, previousMastery = 4)), model)
            }
        }
        compose.onNodeWithText("Mức 4 → 3").assertExists()
        compose.onNodeWithText("Lần ôn tiếp theo:", substring = true).assertDoesNotExist()
        compose.onNodeWithText("Mức thành thạo trước: 1").assertDoesNotExist()
    }
}
