package com.example.chineselearningapp

import androidx.activity.ComponentActivity
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import com.example.chineselearningapp.core.navigation.*
import com.example.chineselearningapp.domain.model.*
import com.example.chineselearningapp.domain.repository.*
import com.example.chineselearningapp.feature.auth.*
import com.example.chineselearningapp.feature.dictionary.*
import com.example.chineselearningapp.ui.theme.ChineseLearningAppTheme
import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test

class DictionaryUiTest {
    @get:Rule val compose = createAndroidComposeRule<ComponentActivity>()
    private val first = "f15eec42-512e-4a48-9c2f-045264b2e119"
    private val second = "f15eec42-512e-4a48-9c2f-045264b2e120"
    private val source = DictionarySource("CC-CEDICT", "https://cc-cedict.org/", "CC BY-SA 4.0",
        "https://creativecommons.org/licenses/by-sa/4.0/", "CC-CEDICT contributors", "")
    private fun suggestion(id: String) = DictionarySuggestion(id, "家", if (id == first) "傢" else "家",
        if (id == first) "jiā" else "jie", null, listOf("en"), "CC-CEDICT")
    private fun entry(id: String) = DictionaryEntry(suggestion(id), "jie",
        mapOf("en" to listOf(DictionarySense(1, "family"))), null,
        listOf(CharacterEnrichment("character", "家", listOf(0), listOf(0), "jià", "giá",
            "chú giải chữ", false, source)), source)
    private fun back() {
        compose.activityRule.scenario.onActivity { it.onBackPressedDispatcher.onBackPressed() }
        compose.waitForIdle()
    }

    @Test fun selectsStableUuidAndBackKeepsSearchThenReturnsToLearning() {
        val requests = mutableListOf<String>()
        var searches = 0
        val repository = object : DictionaryRepository {
            override suspend fun search(query: String, offset: Int): DictionaryPage {
                searches++
                return DictionaryPage(listOf(suggestion(first), suggestion(second)), null)
            }
            override suspend fun detail(entryId: String): DictionaryEntry {
                requests += entryId
                return entry(entryId)
            }
        }
        compose.setContent {
            ChineseLearningAppTheme {
                SessionNavigation(SessionState(status = SessionStatus.SignedIn,
                    account = Account("account", "learner@example.com", "An"), contentLoaded = true),
                    SessionActions(), dictionaryRepository = repository)
            }
        }
        compose.onNodeWithTag("tab_Learning").performClick()
        compose.onNodeWithText("Tra từ điển").performScrollTo().performClick()
        compose.onNodeWithTag("main_navigation").assertDoesNotExist()
        compose.onNode(hasSetTextAction()).performTextInput("家")
        compose.waitUntil(5_000) { compose.onAllNodesWithText("jie").fetchSemanticsNodes().isNotEmpty() }
        compose.onNodeWithText("jie").performClick()
        compose.waitUntil(5_000) { requests.isNotEmpty() }
        compose.runOnIdle { assertEquals(listOf(second), requests) }
        compose.onNodeWithText("Nghĩa tiếng Anh").assertExists()
        compose.onNodeWithText("Nghĩa tiếng Việt").assertDoesNotExist()
        back()
        compose.onNode(hasSetTextAction()).assertTextContains("家")
        compose.onNodeWithText("jiā").assertExists()
        compose.onNodeWithText("jie").assertExists()
        compose.runOnIdle { assertEquals(1, searches) }
        back()
        compose.onNodeWithTag("tab_Learning").assertIsSelected()
    }

    @Test fun characterNotesHaveSeparateSectionAndMismatchWarning() {
        compose.setContent {
            ChineseLearningAppTheme {
                DictionaryDetailScreen(DictionaryDetailState(DictionaryPhase.Results, entry(second)), {}, {})
            }
        }
        compose.onNodeWithText("Nghĩa tiếng Anh").assertExists()
        compose.onNodeWithText("Nghĩa tiếng Việt").assertDoesNotExist()
        compose.onNodeWithText("Khám phá từng chữ Hán").performScrollTo().assertIsDisplayed()
        compose.onNodeWithText("chú giải chữ").performScrollTo().assertIsDisplayed()
        compose.onNodeWithText("Chú giải này có cách đọc khác với mục từ đang xem.").performScrollTo().assertIsDisplayed()
        compose.onNodeWithText("Nguồn và giấy phép").performScrollTo().performClick()
        compose.onNodeWithText("CC-CEDICT contributors").performScrollTo().assertIsDisplayed()
    }
}
