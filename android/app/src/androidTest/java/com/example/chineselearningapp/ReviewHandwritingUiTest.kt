package com.example.chineselearningapp

import androidx.activity.ComponentActivity
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.lifecycle.SavedStateHandle
import com.example.chineselearningapp.feature.dictionary.handwriting.*
import com.example.chineselearningapp.feature.review.*
import com.example.chineselearningapp.ui.theme.ChineseLearningAppTheme
import org.junit.Assert.*
import org.junit.Rule
import org.junit.Test

/** Fake native inference only; UI uses real touch strokes and production slot state. */
class ReviewHandwritingUiTest {
    @get:Rule val compose = createAndroidComposeRule<ComponentActivity>()
    private class Recognizer : HandwritingRecognizer {
        override suspend fun prepareModel(onDownload: () -> Unit) = Unit
        override suspend fun recognize(strokes: List<HandwritingStroke>) = listOf("学", "生")
        override fun close() = Unit
    }
    @Test fun handwritingCandidatesNeverSubmitUntilLearnerConfirmsWholeWord() {
        lateinit var model: ReviewHandwritingViewModel
        val submitted = mutableListOf<String>()
        compose.runOnUiThread { model = ReviewHandwritingViewModel(Recognizer(), SavedStateHandle(), "fixture") }
        compose.setContent {
            ChineseLearningAppTheme {
                ReviewHandwritingInput(model, "attempt", 2, true, submit = submitted::add)
            }
        }
        compose.onNodeWithText("Gửi câu trả lời").assertIsNotEnabled()
        compose.onNodeWithTag("handwriting_canvas").performTouchInput { swipe(Offset(50f, 50f), Offset(180f, 180f)) }
        compose.onNodeWithText("Nhận diện").performClick()
        compose.onNodeWithText("学", useUnmergedTree = true).performClick()
        compose.onNodeWithText("2 · □").performClick()
        compose.onNodeWithTag("handwriting_canvas").performTouchInput { swipe(Offset(60f, 50f), Offset(180f, 170f)) }
        compose.onNodeWithText("Nhận diện").performClick()
        compose.onNodeWithText("生", useUnmergedTree = true).performClick()
        compose.runOnIdle { assertTrue(submitted.isEmpty()) }
        compose.onNodeWithText("Câu trả lời: 学生").assertExists()
        compose.onNodeWithText("Gửi câu trả lời").performClick()
        compose.runOnIdle { assertEquals(listOf("学生"), submitted) }
    }
    @Test fun mandatoryInkHasNoKeyboardAndUndoDoesNotSubmit() {
        lateinit var model: ReviewHandwritingViewModel
        var submissions = 0
        compose.runOnUiThread { model = ReviewHandwritingViewModel(Recognizer(), SavedStateHandle(), "fixture") }
        compose.setContent { ChineseLearningAppTheme { ReviewHandwritingInput(model, "attempt", 2, true) { submissions++ } } }
        compose.onNodeWithTag("handwriting_canvas").performTouchInput { swipe(Offset(50f, 50f), Offset(150f, 150f)) }
        compose.onNodeWithText("Hoàn tác").performClick()
        compose.runOnIdle { assertTrue(model.state.value.slots[0].strokes.isEmpty()) }
        compose.onNodeWithText("Bàn phím").assertDoesNotExist()
        compose.onNodeWithText("Nhập chữ Hán bằng bàn phím tiếng Trung").assertDoesNotExist()
        compose.onNodeWithText("Nhận diện").assertIsNotEnabled()
        compose.runOnIdle { assertEquals(0, submissions) }
    }
    @Test fun backgroundingCheckpointsAnUnfinishedFingerStroke() {
        lateinit var model: ReviewHandwritingViewModel
        val saved = SavedStateHandle()
        compose.runOnUiThread { model = ReviewHandwritingViewModel(Recognizer(), saved, "fixture") }
        compose.setContent { ChineseLearningAppTheme { ReviewHandwritingInput(model, "attempt", 1, true) {} } }
        compose.onNodeWithTag("handwriting_canvas").performTouchInput {
            down(Offset(50f, 50f)); moveTo(Offset(140f, 140f))
        }
        compose.activityRule.scenario.moveToState(androidx.lifecycle.Lifecycle.State.CREATED)
        compose.activityRule.scenario.onActivity {
            assertFalse(model.state.value.drawing)
            assertTrue(model.state.value.slots.single().strokes.isNotEmpty())
            val restored = ReviewHandwritingViewModel(Recognizer(), saved, "fixture")
            assertEquals(model.state.value.slots, restored.state.value.slots)
        }
        compose.activityRule.scenario.moveToState(androidx.lifecycle.Lifecycle.State.RESUMED)
    }
}

