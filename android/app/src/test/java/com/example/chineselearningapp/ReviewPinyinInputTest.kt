package com.example.chineselearningapp

import androidx.compose.ui.text.TextRange
import androidx.compose.ui.text.input.TextFieldValue
import com.example.chineselearningapp.feature.review.insertPinyinKey
import org.junit.Assert.*
import org.junit.Test

class ReviewPinyinInputTest {
    @Test fun buildsUmlautAndNumberedToneWithoutSpecialKeyboard() {
        val first = insertPinyinKey(TextFieldValue("n", TextRange(1)), "ü")
        val result = insertPinyinKey(first, "3")
        assertEquals("nü3", result.text); assertEquals(TextRange(3), result.selection)
    }
    @Test fun toneKeyCorrectsPreviousToneInsteadOfAppendingAnotherDigit() {
        assertEquals("nv4", insertPinyinKey(TextFieldValue("nv3", TextRange(3)), "4").text)
        assertEquals("nu:3", insertPinyinKey(TextFieldValue("nu:", TextRange(3)), "3").text)
    }
    @Test fun insertsAtCursorAndReplacesSelectionWithoutChangingOtherSyllables() {
        val result = insertPinyinKey(TextFieldValue("n3 hao3", TextRange(1)), "ü")
        assertEquals("nü3 hao3", result.text)
        assertEquals(TextRange(2), result.selection)
        assertEquals("nü3", insertPinyinKey(TextFieldValue("nu3", TextRange(1, 2)), "ü").text)
    }
}
