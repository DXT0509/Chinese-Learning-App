package com.example.chineselearningapp.feature.review

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.TextRange
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.*
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.chineselearningapp.R
import com.example.chineselearningapp.core.designsystem.*

/** Local editing only; accepted spelling and tone remain server-authoritative. */
internal fun insertPinyinKey(value: TextFieldValue, key: String): TextFieldValue {
    var start = value.selection.min.coerceIn(0, value.text.length)
    val end = value.selection.max.coerceIn(start, value.text.length)
    if (value.selection.collapsed && key in listOf("1", "2", "3", "4", "5") &&
        start > 0 && value.text[start - 1] in '1'..'5') start--
    val text = value.text.replaceRange(start, end, key).take(500)
    return TextFieldValue(text, TextRange((start + key.length).coerceAtMost(text.length)))
}

@Composable
internal fun ReviewPinyinInput(draftKey: String, value: String, onValueChange: (String) -> Unit, enabled: Boolean) {
    var field by rememberSaveable(draftKey, stateSaver = TextFieldValue.Saver) {
        mutableStateOf(TextFieldValue(value, TextRange(value.length)))
    }
    // The VM owns the draft. Keep the cursor locally, including ordinary recreation.
    LaunchedEffect(value) {
        if (field.text != value) field = TextFieldValue(value, TextRange(value.length))
    }
    val focus = LocalFocusManager.current
    Column(verticalArrangement = Arrangement.spacedBy(SpaceSM)) {
        OutlinedTextField(
            value = field,
            onValueChange = { next ->
                field = next.copy(text = next.text.take(500), selection = TextRange(
                    next.selection.start.coerceAtMost(500), next.selection.end.coerceAtMost(500)))
                if (field.text != value) onValueChange(field.text)
            },
            modifier = Modifier
                .fillMaxWidth()
                .testTag("review_answer_PINYIN"),
            enabled = enabled,
            shape = RoundedCornerShape(RadiusMedium),
            colors = OutlinedTextFieldDefaults.colors(
                focusedContainerColor = Surface1,
                unfocusedContainerColor = Surface1,
                disabledContainerColor = Surface1,
                focusedBorderColor = Primary,
                unfocusedBorderColor = Border,
                focusedTextColor = TextPrimary,
                unfocusedTextColor = TextPrimary,
                focusedLabelColor = Primary,
                unfocusedLabelColor = TextSecondary
            ),
            label = { Text(stringResource(R.string.srs_pinyin_input), fontSize = 13.sp) },
            textStyle = LocalTextStyle.current.copy(fontSize = 20.sp, fontWeight = FontWeight.Medium),
            keyboardOptions = KeyboardOptions(capitalization = KeyboardCapitalization.None,
                autoCorrectEnabled = false, keyboardType = KeyboardType.Ascii, imeAction = ImeAction.Done),
            keyboardActions = KeyboardActions(onDone = { focus.clearFocus() })
        )
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(SpaceXS)) {
            listOf("ü", "1", "2", "3", "4", "5").forEach { key ->
                val label = if (key == "ü") stringResource(R.string.srs_insert_umlaut)
                    else stringResource(R.string.srs_insert_tone, key)
                OutlinedButton(
                    onClick = {
                        field = insertPinyinKey(field, key)
                        onValueChange(field.text)
                    },
                    modifier = Modifier
                        .weight(1f)
                        .height(44.dp)
                        .testTag("pinyin_key_$key")
                        .semantics { contentDescription = label },
                    enabled = enabled,
                    shape = RoundedCornerShape(RadiusSmall),
                    border = BorderStroke(1.dp, Border),
                    colors = ButtonDefaults.outlinedButtonColors(
                        containerColor = Surface1,
                        contentColor = Primary
                    ),
                    contentPadding = PaddingValues(0.dp)
                ) {
                    Text(
                        text = if (key == "ü") stringResource(R.string.srs_umlaut) else key,
                        fontSize = 15.sp,
                        fontWeight = FontWeight.Medium,
                        color = Primary
                    )
                }
            }
        }
        Text(
            text = stringResource(R.string.srs_pinyin_keyboard_tip),
            style = FontCaption.copy(color = TextMuted)
        )
    }
}
