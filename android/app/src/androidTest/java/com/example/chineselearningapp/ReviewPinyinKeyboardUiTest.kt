package com.example.chineselearningapp

import androidx.activity.ComponentActivity
import androidx.compose.foundation.layout.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.unit.dp
import com.example.chineselearningapp.feature.review.ReviewPinyinInput
import com.example.chineselearningapp.ui.theme.ChineseLearningAppTheme
import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test

/** Local input only: no model, API, hidden answer or progress writes. */
class ReviewPinyinKeyboardUiTest {
    @get:Rule val compose = createAndroidComposeRule<ComponentActivity>()
    @Test fun umlautAndToneKeysWorkWithoutPinyinKeyboardAtSmallWidth() {
        var value = ""
        compose.setContent {
            var draft by remember { mutableStateOf("") }
            ChineseLearningAppTheme {
                Column(Modifier.width(288.dp)) {
                    ReviewPinyinInput("fixture", draft, { draft = it; value = it }, true)
                }
            }
        }
        compose.onNodeWithTag("review_answer_PINYIN").performTextInput("n")
        compose.onNodeWithTag("pinyin_key_ü").performClick()
        compose.onNodeWithTag("pinyin_key_3").performClick()
        compose.onNodeWithTag("review_answer_PINYIN").assertTextContains("nü3")
        compose.onNodeWithTag("pinyin_key_4").performClick()
        compose.runOnIdle { assertEquals("nü4", value) }
    }
    @Test fun controlsAreDisabledDuringSubmission() {
        compose.setContent {
            ChineseLearningAppTheme {
                Column { ReviewPinyinInput("fixture", "nv3", {}, false) }
            }
        }
        compose.onNodeWithTag("review_answer_PINYIN").assertIsNotEnabled()
        compose.onNodeWithTag("pinyin_key_ü").assertIsNotEnabled()
        compose.onNodeWithTag("pinyin_key_3").assertIsNotEnabled()
    }
}
