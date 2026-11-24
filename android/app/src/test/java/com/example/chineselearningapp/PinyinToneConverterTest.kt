package com.example.chineselearningapp

import androidx.compose.ui.text.TextRange
import androidx.compose.ui.text.input.TextFieldValue
import com.example.chineselearningapp.feature.roadmap.PinyinToneConverter
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class PinyinToneConverterTest {

    @Test
    fun testBasicConversions() {
        assertEquals("hǎo", PinyinToneConverter.convertPinyinTones("hao3"))
        assertEquals("nǐ", PinyinToneConverter.convertPinyinTones("ni3"))
        assertEquals("lǜ", PinyinToneConverter.convertPinyinTones("lv4"))
        assertEquals("lǜ", PinyinToneConverter.convertPinyinTones("lü4"))
        assertEquals("ma", PinyinToneConverter.convertPinyinTones("ma5"))
        assertEquals("hao", PinyinToneConverter.convertPinyinTones("hao5"))
    }

    @Test
    fun testVowelPlacementRules() {
        // 1. Has 'a' -> mark on 'a'
        assertEquals("zhuāng", PinyinToneConverter.convertPinyinTones("zhuang1"))
        assertEquals("dà", PinyinToneConverter.convertPinyinTones("da4"))
        assertEquals("kuài", PinyinToneConverter.convertPinyinTones("kuai4"))
        assertEquals("huáng", PinyinToneConverter.convertPinyinTones("huang2"))

        // 2. No 'a', has 'e' -> mark on 'e'
        assertEquals("xiè", PinyinToneConverter.convertPinyinTones("xie4"))
        assertEquals("de", PinyinToneConverter.convertPinyinTones("de5"))
        assertEquals("ér", PinyinToneConverter.convertPinyinTones("er2"))
        assertEquals("lěi", PinyinToneConverter.convertPinyinTones("lei3"))
        assertEquals("yuè", PinyinToneConverter.convertPinyinTones("yue4"))

        // 3. No 'a', no 'e', has 'ou' -> mark on 'o'
        assertEquals("zhōu", PinyinToneConverter.convertPinyinTones("zhou1"))
        assertEquals("tóu", PinyinToneConverter.convertPinyinTones("tou2"))
        assertEquals("hòu", PinyinToneConverter.convertPinyinTones("hou4"))
        assertEquals("gǒu", PinyinToneConverter.convertPinyinTones("gou3"))

        // 4. Otherwise -> mark on last vowel
        assertEquals("liú", PinyinToneConverter.convertPinyinTones("liu2"))
        assertEquals("guì", PinyinToneConverter.convertPinyinTones("gui4"))
        assertEquals("qiū", PinyinToneConverter.convertPinyinTones("qiu1"))
        assertEquals("shuǐ", PinyinToneConverter.convertPinyinTones("shui3"))
        assertEquals("lǜ", PinyinToneConverter.convertPinyinTones("lv4"))
        assertEquals("lù", PinyinToneConverter.convertPinyinTones("lu4"))
        assertEquals("yī", PinyinToneConverter.convertPinyinTones("yi1"))
        assertEquals("wǔ", PinyinToneConverter.convertPinyinTones("wu3"))
    }

    @Test
    fun testMultipleSyllablesSeparatedAndConcatenated() {
        // Separated by space
        assertEquals("nǐ hǎo", PinyinToneConverter.convertPinyinTones("ni3 hao3"))
        assertEquals("wǒ shì lǎoshī", PinyinToneConverter.convertPinyinTones("wo3 shi4 lao3shi1"))

        // Concatenated
        assertEquals("nǐhǎo", PinyinToneConverter.convertPinyinTones("ni3hao3"))
        assertEquals("lǜsè", PinyinToneConverter.convertPinyinTones("lv4se4"))
    }

    @Test
    fun testLiveTypingAndCursorTracking() {
        // Typing '3' after "hao"
        val tvHao3 = TextFieldValue(text = "hao3", selection = TextRange(4))
        val processed1 = PinyinToneConverter.processTextFieldValue(tvHao3)
        assertEquals("hǎo", processed1.text)
        assertEquals(3, processed1.selection.end)

        // Typing '3' after "ni3 hao"
        val tvNi3Hao3 = TextFieldValue(text = "ni3 hao3", selection = TextRange(8))
        val processed2 = PinyinToneConverter.processTextFieldValue(tvNi3Hao3)
        assertEquals("nǐ hǎo", processed2.text)
        assertEquals(6, processed2.selection.end)
    }

    @Test
    fun testToneBarKeyInsertion() {
        // Cursor at end of "ni", press tone 3
        val tvNi = TextFieldValue(text = "ni", selection = TextRange(2))
        val resNi3 = PinyinToneConverter.applyToneToCurrentSyllable(tvNi, 3)
        assertEquals("nǐ", resNi3.text)
        assertEquals(2, resNi3.selection.end)

        // Cursor at end of "hao", press tone 3
        val tvHao = TextFieldValue(text = "hao", selection = TextRange(3))
        val resHao3 = PinyinToneConverter.applyToneToCurrentSyllable(tvHao, 3)
        assertEquals("hǎo", resHao3.text)
        assertEquals(3, resHao3.selection.end)

        // Cursor at end of "lv", press tone 4
        val tvLv = TextFieldValue(text = "lv", selection = TextRange(2))
        val resLv4 = PinyinToneConverter.applyToneToCurrentSyllable(tvLv, 4)
        assertEquals("lǜ", resLv4.text)
        assertEquals(2, resLv4.selection.end)

        // Changing tone on already toned syllable: "nǐ" + tone 2 -> "ní"
        val tvNiMarked = TextFieldValue(text = "nǐ", selection = TextRange(2))
        val resNi2 = PinyinToneConverter.applyToneToCurrentSyllable(tvNiMarked, 2)
        assertEquals("ní", resNi2.text)
        assertEquals(2, resNi2.selection.end)

        // Preceding character is not a letter (e.g. space) -> ignored
        val tvSpace = TextFieldValue(text = "ni ", selection = TextRange(3))
        val resSpace = PinyinToneConverter.applyToneToCurrentSyllable(tvSpace, 3)
        assertEquals("ni ", resSpace.text)
        assertEquals(3, resSpace.selection.end)

        // Empty string -> ignored
        val tvEmpty = TextFieldValue(text = "", selection = TextRange(0))
        val resEmpty = PinyinToneConverter.applyToneToCurrentSyllable(tvEmpty, 3)
        assertEquals("", resEmpty.text)
    }

    @Test
    fun testAnswerMatching() {
        // Exact match with correct tone
        assertTrue(PinyinToneConverter.isCorrectAnswer("hǎo", "hǎo"))
        assertTrue(PinyinToneConverter.isCorrectAnswer("Hǎo", "hǎo"))
        assertTrue(PinyinToneConverter.isCorrectAnswer("  hǎo  ", "hǎo"))
        assertTrue(PinyinToneConverter.isCorrectAnswer("hao3", "hǎo"))
        assertTrue(PinyinToneConverter.isCorrectAnswer("lǜ", "lǜ"))
        assertTrue(PinyinToneConverter.isCorrectAnswer("lv4", "lǜ"))
        assertTrue(PinyinToneConverter.isCorrectAnswer("ni3 hao3", "nǐ hǎo"))

        // Missing tone -> false
        assertFalse(PinyinToneConverter.isCorrectAnswer("hao", "hǎo"))
        assertFalse(PinyinToneConverter.isCorrectAnswer("ni", "nǐ"))

        // Wrong tone -> false
        assertFalse(PinyinToneConverter.isCorrectAnswer("háo", "hǎo"))
        assertFalse(PinyinToneConverter.isCorrectAnswer("hào", "hǎo"))
        assertFalse(PinyinToneConverter.isCorrectAnswer("hao1", "hǎo"))
        assertFalse(PinyinToneConverter.isCorrectAnswer("nī", "nǐ"))
    }
}

