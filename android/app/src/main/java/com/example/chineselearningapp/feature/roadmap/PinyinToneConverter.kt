package com.example.chineselearningapp.feature.roadmap

import androidx.compose.ui.text.TextRange
import androidx.compose.ui.text.input.TextFieldValue
import java.text.Normalizer
import java.util.Locale

/**
 * Pure Kotlin utility for Pinyin tone mark conversion and answer matching.
 */
object PinyinToneConverter {

    private val TONE_MAP = mapOf(
        'a' to charArrayOf('ā', 'á', 'ǎ', 'à', 'a'),
        'o' to charArrayOf('ō', 'ó', 'ǒ', 'ò', 'o'),
        'e' to charArrayOf('ē', 'é', 'ě', 'è', 'e'),
        'i' to charArrayOf('ī', 'í', 'ǐ', 'ì', 'i'),
        'u' to charArrayOf('ū', 'ú', 'ǔ', 'ù', 'u'),
        'ü' to charArrayOf('ǖ', 'ǘ', 'ǚ', 'ǜ', 'ü'),
        'A' to charArrayOf('Ā', 'Á', 'Ǎ', 'À', 'A'),
        'O' to charArrayOf('Ō', 'Ó', 'Ǒ', 'Ò', 'O'),
        'E' to charArrayOf('Ē', 'É', 'Ě', 'È', 'E'),
        'I' to charArrayOf('Ī', 'Í', 'Ǐ', 'Ì', 'I'),
        'U' to charArrayOf('Ū', 'Ú', 'Ǔ', 'Ù', 'U'),
        'Ü' to charArrayOf('Ǖ', 'Ǘ', 'Ǚ', 'Ǜ', 'Ü')
    )

    private val ACCENT_TO_BASE = mapOf(
        'ā' to 'a', 'á' to 'a', 'ǎ' to 'a', 'à' to 'a',
        'ō' to 'o', 'ó' to 'o', 'ǒ' to 'o', 'ò' to 'o',
        'ē' to 'e', 'é' to 'e', 'ě' to 'e', 'è' to 'e',
        'ī' to 'i', 'í' to 'i', 'ǐ' to 'i', 'ì' to 'i',
        'ū' to 'u', 'ú' to 'u', 'ǔ' to 'u', 'ù' to 'u',
        'ǖ' to 'ü', 'ǘ' to 'ü', 'ǚ' to 'ü', 'ǜ' to 'ü',
        'v' to 'ü',
        'Ā' to 'A', 'Á' to 'A', 'Ǎ' to 'A', 'À' to 'A',
        'Ō' to 'O', 'Ó' to 'O', 'Ǒ' to 'O', 'Ò' to 'O',
        'Ē' to 'E', 'É' to 'E', 'Ě' to 'E', 'È' to 'E',
        'Ī' to 'I', 'Í' to 'I', 'Ǐ' to 'I', 'Ì' to 'I',
        'Ū' to 'U', 'Ú' to 'U', 'Ǔ' to 'U', 'Ù' to 'U',
        'Ǖ' to 'Ü', 'Ǘ' to 'Ü', 'Ǚ' to 'Ü', 'Ǜ' to 'Ü',
        'V' to 'Ü'
    )

    fun isPinyinLetter(c: Char): Boolean {
        return c in 'a'..'z' || c in 'A'..'Z' || c == 'ü' || c == 'Ü' || ACCENT_TO_BASE.containsKey(c)
    }

    private fun isVowel(c: Char): Boolean {
        val b = ACCENT_TO_BASE[c] ?: c
        return b in "aoeiuüAOEIUÜ"
    }

    /**
     * Vowel priority rule:
     * 1. có "a" → dấu trên a
     * 2. nếu không có a mà có "e" → trên e
     * 3. nếu có "ou" → trên o
     * 4. còn lại → trên nguyên âm cuối cùng (a o e i u ü)
     */
    fun findToneVowelIndex(syllable: String): Int {
        val aIdx = syllable.indexOfFirst { it == 'a' || it == 'A' }
        if (aIdx >= 0) return aIdx

        val eIdx = syllable.indexOfFirst { it == 'e' || it == 'E' }
        if (eIdx >= 0) return eIdx

        val ouIdx = syllable.indexOf("ou", ignoreCase = true)
        if (ouIdx >= 0) return ouIdx // position of 'o' in "ou"

        return syllable.indexOfLast { isVowel(it) }
    }

    /**
     * Converts a single syllable with a tone number 1-5.
     * Tone 5 = neutral tone (only removes number, no mark).
     */
    fun convertSyllable(syllable: String, tone: Int): String {
        if (tone !in 1..5) return syllable
        val base = syllable.map { ACCENT_TO_BASE[it] ?: it }.joinToString("")
        if (tone == 5) return base
        val idx = findToneVowelIndex(base)
        if (idx < 0) return base
        val targetChar = base[idx]
        val markedChar = TONE_MAP[targetChar]?.getOrNull(tone - 1) ?: targetChar
        return base.substring(0, idx) + markedChar + base.substring(idx + 1)
    }

    /**
     * Converts any occurrences of pinyin letters followed by 1-5 to tone-marked syllables.
     * Supports multiple syllables separated by spaces or concatenated ("ni3 hao3", "ni3hao3").
     */
    fun convertPinyinTones(text: String): String {
        val regex = Regex("([a-zA-ZüÜvV\u0100-\u024F]+)([1-5])")
        return regex.replace(text) { matchResult ->
            val syllable = matchResult.groupValues[1]
            val tone = matchResult.groupValues[2].toInt()
            convertSyllable(syllable, tone)
        }
    }

    /**
     * Live typing conversion: converts numbered tones and adjusts cursor position correctly.
     */
    fun processTextFieldValue(value: TextFieldValue): TextFieldValue {
        val text = value.text
        val cursor = value.selection.end
        val regex = Regex("([a-zA-ZüÜvV\u0100-\u024F]+)([1-5])")
        val matches = regex.findAll(text).toList()
        if (matches.isEmpty()) return value

        val sb = StringBuilder()
        var lastIdx = 0
        var newCursor = cursor

        for (match in matches) {
            val matchStart = match.range.first
            val matchEnd = match.range.last + 1
            val syllable = match.groupValues[1]
            val tone = match.groupValues[2].toInt()

            val converted = convertSyllable(syllable, tone)

            sb.append(text.substring(lastIdx, matchStart))
            val currentReplacementStart = sb.length
            sb.append(converted)
            lastIdx = matchEnd

            val lenDiff = (matchEnd - matchStart) - converted.length
            if (cursor >= matchEnd) {
                newCursor -= lenDiff
            } else if (cursor > matchStart) {
                val offsetInMatch = cursor - matchStart
                val newOffset = offsetInMatch.coerceAtMost(converted.length)
                newCursor = currentReplacementStart + newOffset
            }
        }
        sb.append(text.substring(lastIdx))
        val newText = sb.toString()
        val clampedCursor = newCursor.coerceIn(0, newText.length)
        return TextFieldValue(text = newText, selection = TextRange(clampedCursor))
    }

    /**
     * ToneBar button click handler:
     * Takes the syllable currently being typed (continuous letters immediately preceding cursor),
     * appends tone 1-5, and converts it. If char preceding cursor is not a letter, ignores.
     */
    fun applyToneToCurrentSyllable(value: TextFieldValue, tone: Int): TextFieldValue {
        val text = value.text
        val cursor = value.selection.end
        if (cursor <= 0 || cursor > text.length) return value

        val beforeCursor = text.substring(0, cursor)
        if (beforeCursor.isEmpty() || !isPinyinLetter(beforeCursor.last())) {
            return value
        }

        var wordStart = cursor
        while (wordStart > 0 && isPinyinLetter(text[wordStart - 1])) {
            wordStart--
        }

        val syllable = text.substring(wordStart, cursor)
        val converted = convertSyllable(syllable, tone)

        val afterCursor = text.substring(cursor)
        val newText = text.substring(0, wordStart) + converted + afterCursor
        val newCursor = wordStart + converted.length
        return TextFieldValue(text = newText, selection = TextRange(newCursor))
    }

    /**
     * Normalizes pinyin for comparison:
     * - lowercase
     * - extra whitespace trimmed/collapsed
     * - Unicode NFC normalized
     * - "v" -> "ü", "u:" -> "ü"
     */
    fun normalizeForComparison(value: String): String {
        val converted = convertPinyinTones(value)
        return Normalizer.normalize(converted, Normalizer.Form.NFC)
            .lowercase(Locale.ROOT)
            .replace('v', 'ü')
            .replace("u:", "ü")
            .trim()
            .replace(Regex("\\s+"), " ")
    }

    /**
     * Compares user input against target pinyin.
     * Must have correct tone mark. Missing or wrong tone mark = false.
     */
    fun isCorrectAnswer(userInput: String, targetPinyin: String): Boolean {
        return normalizeForComparison(userInput) == normalizeForComparison(targetPinyin)
    }
}

