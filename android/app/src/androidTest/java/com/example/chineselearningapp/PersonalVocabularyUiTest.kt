package com.example.chineselearningapp

import androidx.activity.ComponentActivity
import androidx.compose.runtime.*
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import com.example.chineselearningapp.domain.repository.SavedWord
import com.example.chineselearningapp.domain.repository.*
import com.example.chineselearningapp.domain.model.*
import com.example.chineselearningapp.core.navigation.*
import com.example.chineselearningapp.feature.auth.*
import com.example.chineselearningapp.feature.vocabulary.*
import com.example.chineselearningapp.ui.theme.ChineseLearningAppTheme
import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test

class PersonalVocabularyUiTest {
    @get:Rule val compose = createAndroidComposeRule<ComponentActivity>()

    @Test fun wordbookDetailAndBackRestoreQueryAndSavedState() {
        val id = "f15eec42-512e-4a48-9c2f-045264b2e119"
        val word = SavedWord("saved", id, "学", "xué", "học", "study", true)
        val wordbook = object : PersonalVocabularyRepository {
            override suspend fun status(entryId: String) = "saved"
            override suspend fun save(entryId: String) = word
            override suspend fun list(query: String, cursor: String?) = WordbookPage(listOf(word), 1, null)
            override suspend fun remove(savedId: String) {}
        }
        val dictionary = object : DictionaryRepository {
            override suspend fun search(query: String, offset: Int) = DictionaryPage(emptyList(), null)
            override suspend fun detail(entryId: String) = DictionaryEntry(
                DictionarySuggestion(entryId, "学", "xué", "học", listOf("vi"), "APP_CURATED"),
                "xué", mapOf("vi" to listOf(DictionarySense(1, "học"))), null, "HUMAN_APPROVED")
        }
        compose.setContent { ChineseLearningAppTheme {
            SessionNavigation(SessionState(status = SessionStatus.SignedIn,
                account = Account("user", "test@example.com"), contentLoaded = true), SessionActions(),
                dictionaryRepository = dictionary, wordbookRepository = wordbook)
        } }
        compose.onNodeWithTag("tab_Learning").performClick()
        compose.onNodeWithText("Từ vựng của tôi").performScrollTo().performClick()
        compose.waitUntil(5_000) { compose.onAllNodesWithText("学").fetchSemanticsNodes().isNotEmpty() }
        compose.onNode(hasSetTextAction()).performTextInput("xué")
        compose.waitUntil(5_000) { compose.onAllNodesWithText("学").fetchSemanticsNodes().isNotEmpty() }
        compose.onNodeWithText("学").performClick()
        compose.waitUntil(5_000) { compose.onAllNodesWithText("Đã lưu").fetchSemanticsNodes().isNotEmpty() }
        compose.onNodeWithText("Đã lưu").assertIsNotEnabled()
        compose.activityRule.scenario.onActivity { it.onBackPressedDispatcher.onBackPressed() }
        compose.onNode(hasSetTextAction()).assertTextContains("xué")
        compose.onNodeWithText("学").assertExists()
    }

    @Test fun emptyCollectionOffersDictionaryNavigation() {
        var explored = false
        compose.setContent { ChineseLearningAppTheme {
            MyVocabularyScreen(WordbookState(loading = false), {}, {}, {}, {},
                { explored = true }, {}, {}, {})
        } }
        compose.onNodeWithText("Bạn chưa lưu từ vựng nào").assertIsDisplayed()
        compose.onNodeWithText("Khám phá từ điển").performClick()
        compose.runOnIdle { assertEquals(true, explored) }
    }

    @Test fun cardsOpenExactEntryAndRemovalNeedsConfirmation() {
        val word = SavedWord("saved", "dictionary-id", "学", "xué", "học", "study", false)
        var opened: String? = null
        var confirmed = 0
        compose.setContent { ChineseLearningAppTheme {
            var state by remember { mutableStateOf(WordbookState(items = listOf(word), total = 1, loading = false)) }
            MyVocabularyScreen(state, { state = state.copy(query = it) }, {}, {}, { opened = it }, {},
                { state = state.copy(pendingRemoval = it) },
                { state = state.copy(pendingRemoval = null) }, { confirmed++ })
        } }
        compose.onNodeWithText("Nghĩa tiếng Anh: study").assertExists()
        compose.onNodeWithText("学").performClick()
        compose.runOnIdle { assertEquals("dictionary-id", opened) }
        compose.onNodeWithText("Bỏ lưu").performClick()
        compose.onNodeWithText("Bỏ lưu “学” khỏi bộ sưu tập?").assertIsDisplayed()
        compose.runOnIdle { assertEquals(0, confirmed) }
        compose.onNodeWithText("Hủy").performClick()
        compose.onNodeWithText("Bỏ lưu").performClick()
        compose.onAllNodesWithText("Bỏ lưu").filter(hasClickAction()).onLast().performClick()
        compose.runOnIdle { assertEquals(1, confirmed) }
    }

    @Test fun savingAndSavedStatesDisableSubmissionAndFailureOffersRetry() {
        var state by mutableStateOf(SavedEntryState())
        compose.setContent { ChineseLearningAppTheme { SavedVocabularyAction(state, {}, {}) } }
        compose.onNodeWithText("Lưu từ vựng").assertIsNotEnabled()
        compose.runOnIdle { state = SavedEntryState(loading = false, statusKnown = true) }
        compose.onNodeWithText("Lưu từ vựng").assertIsEnabled()
        compose.runOnIdle { state = state.copy(savedId = "saved") }
        compose.onNodeWithText("Đã lưu").assertIsNotEnabled()
        compose.runOnIdle { state = SavedEntryState(loading = false, error = true) }
        compose.onNodeWithText("Lưu từ vựng").assertIsNotEnabled()
        compose.onNodeWithText("Thử lại").assertExists()
    }
}
