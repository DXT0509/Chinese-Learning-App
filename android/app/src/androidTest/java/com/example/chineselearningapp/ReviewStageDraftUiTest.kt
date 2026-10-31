package com.example.chineselearningapp

import androidx.activity.ComponentActivity
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.width
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.unit.dp
import androidx.lifecycle.SavedStateHandle
import com.example.chineselearningapp.domain.repository.*
import com.example.chineselearningapp.feature.review.*
import com.example.chineselearningapp.ui.theme.ChineseLearningAppTheme
import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test

/** Small-width real Compose interactions; no network, model download or learner data. */
class ReviewStageDraftUiTest {
    @get:Rule val compose = createAndroidComposeRule<ComponentActivity>()
    private class Repository : ReviewRepository {
        var submissions = 0
        override suspend fun dashboard() = ReviewDashboard(1, 1, 0, true)
        override suspend fun due() = emptyList<ReviewProgress>()
        override suspend fun targets() = ReviewTargets(listOf(ReviewTarget("saved", true)), emptyList())
        override suspend fun progress(savedId: String) = error("No progress read")
        override suspend fun start(savedId: String, requestId: String) = ReviewStart(requestId, true)
        override suspend fun question(attemptId: String): ReviewStage {
            val questions = mapOf("HANZI" to ReviewQuestion("TEXT", "Con ngựa", null, emptyList()),
                "PINYIN" to ReviewQuestion("TEXT", "Con ngựa", null, emptyList()),
                "POS" to ReviewQuestion("SINGLE_SELECT", "Con ngựa", null, listOf("noun", "verb")))
            return ReviewStage(attemptId, "HANZI", "IN_PROGRESS", "2099-01-01T00:00:00Z",
                questions["HANZI"], emptyList(), emptyList(), questions)
        }
        override suspend fun submit(attemptId: String, submission: ReviewSubmission) { submissions++ }
        override suspend fun finalize(attemptId: String) = error("No premature finalization")
    }
    @Test fun twoSelectorsPreservePinyinDraftWithoutKeyboardHanziOrPos() {
        val repository = Repository()
        lateinit var model: ReviewViewModel
        compose.runOnUiThread { model = ReviewViewModel(repository, SavedStateHandle(), "fixture") }
        compose.setContent {
            ChineseLearningAppTheme {
                val state by model.state.collectAsState()
                Box(Modifier.width(320.dp)) { ReviewScreen(state, model) }
            }
        }
        compose.onNodeWithText("Ôn tập ngay").performScrollTo().performClick()
        listOf("HANZI", "PINYIN").forEach { compose.onNodeWithTag("review_stage_$it").assertExists() }
        compose.onNodeWithTag("review_stage_PINYIN").performClick()
        compose.onNodeWithTag("review_answer_PINYIN").performScrollTo().performTextInput("ma3")
        compose.onNodeWithTag("review_stage_HANZI").performClick()
        compose.onNodeWithTag("review_stage_HANZI").assertIsSelected()
        compose.onNodeWithTag("review_answer_HANZI").assertDoesNotExist()
        compose.onNodeWithTag("review_stage_POS").assertDoesNotExist()
        compose.runOnIdle { assertEquals(0, repository.submissions) }
        compose.onNodeWithTag("review_stage_PINYIN").performClick()
        compose.onNodeWithTag("review_answer_PINYIN").assertTextContains("ma3")
        compose.onNodeWithText("Hết hạn lượt ôn:", substring = true).assertDoesNotExist()
    }
}
