package com.example.chineselearningapp

import androidx.activity.ComponentActivity
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.StateRestorationTester
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import com.example.chineselearningapp.domain.model.*
import com.example.chineselearningapp.feature.roadmap.CharacterStructureScreen
import com.example.chineselearningapp.ui.theme.ChineseLearningAppTheme
import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test

class CharacterStructureUiTest {
    @get:Rule val compose = createAndroidComposeRule<ComponentActivity>()
    private val word = RoadmapWord("ni", 1, "你", "nǐ", listOf("bạn"), "nhĩ")
    private val unavailable = LessonEnrichment("UNAVAILABLE", null, null)
    private val longNotes = LessonEnrichment("AVAILABLE", "Ghi công tư liệu: không hiển thị ở đây", null)
    private val components = listOf(
        LessonComponent(0, "亻", "SEMANTIC_RADICAL", longNotes),
        LessonComponent(0, "尔", "STRUCTURAL", longNotes))
    private fun lesson(parts: List<LessonComponent> = components) = RoadmapLesson("nv", "lv", "NEW_WORD", "你",
        listOf(word), emptyList(), unavailable, longNotes, longNotes, unavailable, parts)

    @Test fun revealOneComponentPerTapThenOptionalMnemonicBeforeAcknowledgement() {
        var acknowledgements = 0
        compose.setContent { ChineseLearningAppTheme {
            CharacterStructureScreen(word, lesson(), true, {}, { acknowledgements++ }, {}, false)
        } }
        compose.onNodeWithText("Bộ nhân đứng").assertDoesNotExist()
        compose.onNodeWithText("Thành phần cấu tạo").assertDoesNotExist()
        compose.onNodeWithText("💡 Mẹo nhớ").assertDoesNotExist()
        compose.onNodeWithText("Tiếp tục").performClick()
        compose.onNodeWithText("Bộ nhân đứng").assertIsDisplayed()
        compose.onNodeWithText("Thành phần cấu tạo").assertDoesNotExist()
        compose.onNodeWithText("Tiếp tục").performClick()
        compose.onNodeWithText("Thành phần cấu tạo").assertIsDisplayed()
        compose.onNodeWithText("💡 Mẹo nhớ").assertDoesNotExist()
        compose.onNodeWithText("Tiếp tục").performClick()
        compose.onNodeWithText("💡 Mẹo nhớ").assertIsDisplayed()
        compose.onNodeWithText(longNotes.text!!).assertDoesNotExist()
        compose.onNodeWithText("Thu gọn").assertDoesNotExist()
        compose.runOnIdle { assertEquals(0, acknowledgements) }
        compose.onNodeWithText("Hiểu rồi, tiếp tục →").performClick()
        compose.runOnIdle { assertEquals(1, acknowledgements) }
    }

    @Test fun lessonWithoutMnemonicFinishesAfterItsLastReviewedComponent() {
        var acknowledgements = 0
        val single = word.copy(id = "ren", simplified = "人")
        compose.setContent { ChineseLearningAppTheme {
            CharacterStructureScreen(single, lesson(components.take(1)), true, {}, { acknowledgements++ }, {}, false)
        } }
        compose.onNodeWithText("Tiếp tục").performClick()
        compose.onNodeWithText("💡 Mẹo nhớ").assertDoesNotExist()
        compose.onNodeWithText("Hiểu rồi, tiếp tục →").performClick()
        compose.runOnIdle { assertEquals(1, acknowledgements) }
    }

    @Test fun revealProgressSurvivesRestorationWithoutSubmittingEvidence() {
        var acknowledgements = 0
        val restoration = StateRestorationTester(compose)
        restoration.setContent { ChineseLearningAppTheme {
            CharacterStructureScreen(word, lesson(), true, {}, { acknowledgements++ }, {}, false)
        } }
        compose.onNodeWithText("Tiếp tục").performClick()
        restoration.emulateSavedInstanceStateRestore()
        compose.onNodeWithText("Bộ nhân đứng").assertIsDisplayed()
        compose.onNodeWithText("Thành phần cấu tạo").assertDoesNotExist()
        compose.runOnIdle { assertEquals(0, acknowledgements) }
    }
}
