package com.example.chineselearningapp.feature.review

import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.example.chineselearningapp.R
import com.example.chineselearningapp.feature.dictionary.handwriting.HandwritingCanvas
import com.example.chineselearningapp.feature.dictionary.handwriting.HandwritingPhase

@Composable
internal fun ReviewHandwritingInput(model: ReviewHandwritingViewModel, attempt: String,
    count: Int?, enabled: Boolean, submitLabel: Int = R.string.srs_submit, submit: (String) -> Unit) {
    val ink by model.state.collectAsStateWithLifecycle()
    LaunchedEffect(attempt, count) { model.open(attempt, count) }
    if (ink.attempt != attempt) { LinearProgressIndicator(Modifier.fillMaxWidth()); return }
    val busy = ink.phase in setOf(HandwritingPhase.Preparing, HandwritingPhase.Downloading, HandwritingPhase.Recognizing)
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            if (ink.capacityReached) Text(stringResource(R.string.srs_ink_capacity), color = MaterialTheme.colorScheme.error)
            Row(Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                ink.slots.forEachIndexed { index, slot ->
                    FilterChip(index == ink.active, { model.activate(index) }, enabled = enabled && !ink.drawing,
                        label = { Text(stringResource(R.string.srs_slot, index + 1, slot.selected ?: "□"), style = MaterialTheme.typography.titleLarge) })
                }
            }
            if (busy) LinearProgressIndicator(Modifier.fillMaxWidth())
            val status = when (ink.phase) {
                HandwritingPhase.Preparing -> R.string.ink_preparing
                HandwritingPhase.Downloading -> R.string.ink_downloading
                HandwritingPhase.Recognizing -> R.string.ink_recognizing
                HandwritingPhase.ModelError -> R.string.ink_model_error
                HandwritingPhase.RecognitionError -> R.string.ink_recognition_error
                HandwritingPhase.Empty -> R.string.ink_empty
                else -> null
            }
            status?.let { Text(stringResource(it)) }
            if (ink.phase == HandwritingPhase.ModelError)
                OutlinedButton(model::prepare, enabled = enabled) { Text(stringResource(R.string.srs_retry)) }
            ink.slots.getOrNull(ink.active)?.let { slot ->
                key(attempt, ink.active) {
                    HandwritingCanvas(slot.strokes, enabled && !busy && ink.phase != HandwritingPhase.ModelError,
                        model::begin, model::end, preserveInterrupted = true)
                }
                FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedButton(model::undo, enabled = enabled && !busy && !ink.drawing && slot.strokes.isNotEmpty()) { Text(stringResource(R.string.ink_undo)) }
                    OutlinedButton(model::clear, enabled = enabled && !busy && !ink.drawing && slot.strokes.isNotEmpty()) { Text(stringResource(R.string.ink_clear)) }
                    Button(model::recognize, enabled = enabled && !busy && !ink.drawing && ink.phase != HandwritingPhase.ModelError && slot.strokes.isNotEmpty()) { Text(stringResource(R.string.ink_recognize)) }
                }
                if (slot.strokes.isEmpty()) Text(stringResource(R.string.srs_canvas_empty), style = MaterialTheme.typography.bodySmall)
                if (slot.candidates.isNotEmpty()) Text(stringResource(R.string.ink_choose))
                Row(Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    slot.candidates.forEach { candidate ->
                        FilterChip(slot.selected == candidate, { model.select(candidate) }, enabled = enabled && !busy,
                            label = { Text(candidate, style = MaterialTheme.typography.headlineMedium) })
                    }
                }
            }
            Text(stringResource(R.string.srs_selected_word, ink.word.ifEmpty { "…" }), style = MaterialTheme.typography.headlineSmall)
        Button({ submit(ink.word) }, Modifier.fillMaxWidth(), enabled = enabled && !ink.drawing && !busy && ink.word.isNotBlank()) {
            Text(stringResource(submitLabel))
        }
    }
}
