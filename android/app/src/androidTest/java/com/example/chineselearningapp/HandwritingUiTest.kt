package com.example.chineselearningapp

import androidx.activity.ComponentActivity
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import com.example.chineselearningapp.feature.dictionary.*
import com.example.chineselearningapp.feature.dictionary.handwriting.*
import com.example.chineselearningapp.ui.theme.ChineseLearningAppTheme
import com.example.chineselearningapp.core.navigation.SessionActions
import com.example.chineselearningapp.core.navigation.SessionNavigation
import com.example.chineselearningapp.domain.model.*
import com.example.chineselearningapp.domain.repository.DictionaryRepository
import com.example.chineselearningapp.domain.repository.Account
import com.example.chineselearningapp.feature.auth.SessionState
import com.example.chineselearningapp.feature.auth.SessionStatus
import org.junit.Assert.*
import org.junit.Rule
import org.junit.Test

class HandwritingUiTest {
    @get:Rule val compose = createAndroidComposeRule<ComponentActivity>()
    private class Recognizer : HandwritingRecognizer {
        override suspend fun prepareModel(onDownload: () -> Unit) {}
        override suspend fun recognize(strokes: List<HandwritingStroke>) = listOf("你", "好")
        override fun close() {}
    }

    @Test fun realPointerStrokesCandidatesInsertionUndoClearAndKeyboard() {
        val model = HandwritingViewModel(Recognizer())
        var query = ""
        compose.setContent {
            ChineseLearningAppTheme {
                DictionarySearchScreen(DictionarySearchState(), { text, _ -> query = text }, {}, {}, {}, {}, model)
            }
        }
        compose.onNodeWithContentDescription("Viết chữ Hán").performClick()
        compose.onNodeWithText("Nhận diện").performScrollTo().assertIsNotEnabled()
        fun draw() {
            compose.onNodeWithTag("handwriting_canvas").performScrollTo().performTouchInput {
                swipe(Offset(width * .2f, height * .2f), Offset(width * .7f, height * .8f), 300)
            }
        }
        draw()
        compose.runOnIdle { assertEquals(1, model.state.value.strokes.size) }
        compose.onNodeWithText("Nhận diện").performScrollTo().performClick()
        compose.onNodeWithText("你").performScrollTo().performClick()
        compose.runOnIdle { assertEquals("你", query); assertTrue(model.state.value.strokes.isEmpty()) }
        draw()
        compose.onNodeWithText("Nhận diện").performScrollTo().performClick()
        compose.onNodeWithText("好").performScrollTo().performClick()
        compose.onNode(hasSetTextAction()).assertTextContains("你好")
        draw(); draw()
        compose.onNodeWithText("Hoàn tác").performScrollTo().performClick()
        compose.runOnIdle { assertEquals(1, model.state.value.strokes.size) }
        compose.onNodeWithText("Xóa nét").performScrollTo().performClick()
        compose.onNodeWithText("Nhận diện").assertIsNotEnabled()
        compose.onNodeWithText("Đóng").performScrollTo().performClick()
        compose.onNode(hasSetTextAction()).performTextInput("学生")
        compose.onNode(hasSetTextAction()).assertTextContains("你好学生")
    }

    @Test fun cancelledTouchDoesNotCommitPartialStroke() {
        var completed: HandwritingStroke? = null
        compose.setContent {
            ChineseLearningAppTheme { HandwritingCanvas(emptyList(), true, {}, { completed = it }) }
        }
        compose.onNodeWithTag("handwriting_canvas").performTouchInput {
            down(center); moveTo(center + Offset(10f, 20f)); cancel()
        }
        compose.runOnIdle { assertNull(completed) }
    }

    @Test fun handwritingUsesDictionarySearchAndExistingDetailNavigation() {
        val id = "f15eec42-512e-4a48-9c2f-045264b2e119"
        val suggestion = DictionarySuggestion(id, "你", null, "nǐ", null, listOf("en"), "source")
        val origin = DictionarySource("source", "https://example.com", "license", "https://example.com", "credit", "")
        val requested = mutableListOf<String>()
        val queries = mutableListOf<String>()
        val repository = object : DictionaryRepository {
            override suspend fun search(query: String, offset: Int): DictionaryPage {
                queries += query
                return DictionaryPage(listOf(suggestion), null)
            }
            override suspend fun detail(entryId: String): DictionaryEntry {
                requested += entryId
                return DictionaryEntry(suggestion, "nǐ", mapOf("en" to listOf(DictionarySense(1, "you"))),
                    null, emptyList(), origin)
            }
        }
        compose.setContent {
            ChineseLearningAppTheme {
                SessionNavigation(SessionState(status = SessionStatus.SignedIn,
                    account = Account("account", "learner@example.com", "An"), contentLoaded = true),
                    SessionActions(), dictionaryRepository = repository, handwritingFactory = { Recognizer() })
            }
        }
        compose.onNodeWithTag("tab_Learning").performClick()
        compose.onNodeWithText("Tra từ điển").performScrollTo().performClick()
        compose.onNodeWithContentDescription("Viết chữ Hán").performClick()
        compose.onNodeWithTag("handwriting_canvas").performScrollTo().performTouchInput {
            swipe(center, center + Offset(30f, 40f), 200)
        }
        compose.onNodeWithText("Nhận diện").performScrollTo().performClick()
        compose.onNodeWithText("你").performScrollTo().performClick()
        compose.onNodeWithText("Đóng").performScrollTo().performClick()
        compose.waitUntil(5_000) { compose.onAllNodesWithText("nǐ").fetchSemanticsNodes().isNotEmpty() }
        compose.onNodeWithText("nǐ").performScrollTo().performClick()
        compose.waitUntil(5_000) { requested.isNotEmpty() }
        compose.runOnIdle { assertEquals(listOf(id), requested); assertEquals(listOf("你"), queries) }
        compose.activityRule.scenario.onActivity { it.onBackPressedDispatcher.onBackPressed() }
        compose.onNode(hasSetTextAction()).assertTextContains("你")
    }

    @Test fun officialMainlandModelIdentifierCanInitializeClientWithoutDownloading() {
        val id = com.google.mlkit.vision.digitalink.recognition.DigitalInkRecognitionModelIdentifier.fromLanguageTag("zh-Hani-CN")
        assertNotNull(id)
        val model = com.google.mlkit.vision.digitalink.recognition.DigitalInkRecognitionModel.builder(id!!).build()
        val client = com.google.mlkit.vision.digitalink.recognition.DigitalInkRecognition.getClient(
            com.google.mlkit.vision.digitalink.recognition.DigitalInkRecognizerOptions.builder(model).build())
        client.close()
    }
}
