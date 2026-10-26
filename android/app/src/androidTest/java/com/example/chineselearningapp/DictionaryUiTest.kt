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
    private fun suggestion(id: String) = DictionarySuggestion(id, "家",
        if (id == first) "jiā" else "jie", null, listOf("en"), "CC-CEDICT")
    private fun entry(id: String) = DictionaryEntry(suggestion(id), "jie",
        mapOf("en" to listOf(DictionarySense(1, "family"))), null,
        "HUMAN_APPROVED")
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

    @Test fun detailShowsCuratedContentSource() {
        compose.setContent {
            ChineseLearningAppTheme {
                DictionaryDetailScreen(DictionaryDetailState(DictionaryPhase.Results, entry(second)), {}, {})
            }
        }
        compose.onNodeWithText("Nghĩa tiếng Anh").assertExists()
        compose.onNodeWithText("Nghĩa tiếng Việt").assertDoesNotExist()
        compose.onNodeWithText("Từ vựng giản thể do ứng dụng biên soạn", substring = true)
            .performScrollTo().assertIsDisplayed()
    }
}
