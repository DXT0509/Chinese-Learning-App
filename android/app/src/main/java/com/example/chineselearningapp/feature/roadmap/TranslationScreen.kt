package com.example.chineselearningapp.feature.roadmap

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.example.chineselearningapp.R
import com.example.chineselearningapp.core.designsystem.*
import com.example.chineselearningapp.domain.model.RoadmapExample
import com.example.chineselearningapp.feature.dictionary.handwriting.HandwritingStroke
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.launch

@Composable
internal fun TranslationScreen(sentence: RoadmapExample?, state: LessonState, model: LessonViewModel,
    enabled: Boolean, recognize: suspend (List<HandwritingStroke>) -> String?, next: () -> Unit, back: () -> Unit) {
    var handwriting by rememberSaveable { mutableStateOf(false) }
    var recognizing by remember { mutableStateOf(false) }
    var drawing by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()
    val target = sentence?.simplified.orEmpty()
    val characters = normalizeChinese(target).codePoints().toArray().map { String(Character.toChars(it)) }
    val slot = normalizeChinese(state.translation).codePointCount(0, normalizeChinese(state.translation).length)
    LessonFrame(stringResource(R.string.lesson_flow_translation), LessonStep.Translation, enabled && !recognizing && !drawing, back,
        stringResource(R.string.lesson_flow_translation_hint),
        stringResource(if (state.feedback == true || sentence == null) R.string.roadmap_continue else R.string.writing_check),
        sentence == null || state.translation.isNotBlank(), {
            if (state.feedback == true || sentence == null) next() else model.checkTranslation(target)
        }) {
        if (sentence == null) Text(stringResource(R.string.lesson_flow_no_sentence)) else {
            Text(sentence.vietnamese, style = FontTitle)
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                FilterChip(!handwriting, { handwriting = false }, enabled = !recognizing && !drawing,
                    label = { Text(stringResource(R.string.lesson_flow_type)) })
                FilterChip(handwriting, { handwriting = true }, enabled = !recognizing && !drawing,
                    label = { Text(stringResource(R.string.lesson_flow_draw)) })
            }
            OutlinedTextField(state.translation, model::editTranslation, Modifier.fillMaxWidth().testTag("lesson_translation"),
                enabled = enabled && !recognizing && !drawing && state.feedback != true,
                label = { Text(stringResource(R.string.lesson_flow_chinese)) })
            if (handwriting && state.feedback != true && slot < characters.size) {
                Text(stringResource(R.string.lesson_flow_character, slot + 1, characters.size))
                DrawingCanvas(state.translationInk, enabled && !recognizing, { drawing = true }, {
                    drawing = false; model.addTranslationStroke(it)
                }, guideCharacter = null, showGrid = true, modifier = Modifier.fillMaxWidth().height(240.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    TextButton(model::undoTranslationInk, enabled = !recognizing && !drawing && state.translationInk.isNotEmpty()) {
                        Text(stringResource(R.string.ink_undo))
                    }
                    TextButton(model::clearTranslationInk, enabled = !recognizing && !drawing && state.translationInk.isNotEmpty()) {
                        Text(stringResource(R.string.writing_clear))
                    }
                }
                OutlinedButton(onClick = {
                    if (recognizing || drawing) return@OutlinedButton
                    recognizing = true; error = false
                    val ink = state.translationInk
                    scope.launch {
                        try {
                            val candidate = recognize(ink)
                            if (candidate != null && candidate == characters.getOrNull(slot)) model.appendCharacter(candidate)
                            else model.recordAnswer(false)
                        } catch (cancelled: CancellationException) { throw cancelled }
                        catch (_: Exception) { error = true }
                        finally { recognizing = false }
                    }
                }, enabled = enabled && !recognizing && !drawing && state.translationInk.isNotEmpty()) {
                    Text(stringResource(R.string.lesson_flow_recognize_character))
                }
                if (recognizing) LinearProgressIndicator(Modifier.fillMaxWidth())
                if (error) Text(stringResource(R.string.roadmap_recognition_error), color = MaterialTheme.colorScheme.error)
            }
            LessonFeedback(state.feedback)
        }
    }
}
