package com.example.chineselearningapp.feature.dictionary.handwriting

import androidx.compose.ui.text.TextRange
import androidx.compose.ui.text.input.TextFieldValue

/** Expand a selection crossing a surrogate pair; move a split caret after the whole code point. */
fun insertHandwriting(field: TextFieldValue, candidate: String): TextFieldValue {
    fun split(index: Int) = index > 0 && index < field.text.length &&
        field.text[index - 1].isHighSurrogate() && field.text[index].isLowSurrogate()
    var start = field.selection.min
    var end = field.selection.max
    if (start == end && split(start)) { start++; end++ }
    else {
        if (split(start)) start--
        if (split(end)) end++
    }
    return TextFieldValue(field.text.replaceRange(start, end, candidate), TextRange(start + candidate.length))
}
