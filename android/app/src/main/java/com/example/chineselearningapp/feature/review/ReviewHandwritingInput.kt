package com.example.chineselearningapp.feature.review

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.example.chineselearningapp.R
import com.example.chineselearningapp.core.designsystem.*
import com.example.chineselearningapp.feature.dictionary.handwriting.HandwritingPhase

@Composable
internal fun ReviewHandwritingInput(
    model: ReviewHandwritingViewModel,
    attempt: String,
    count: Int?,
    enabled: Boolean,
    placeholder: String? = null,
    submitLabel: Int = R.string.srs_submit,
    submit: (String) -> Unit
) {
    val ink by model.state.collectAsStateWithLifecycle()
    LaunchedEffect(attempt, count) { model.open(attempt, count) }
    if (ink.attempt != attempt) {
        MiniProgressBar(progress = 0.5f, fillColor = Primary)
        return
    }
    val busy = ink.phase in setOf(HandwritingPhase.Preparing, HandwritingPhase.Downloading, HandwritingPhase.Recognizing)

    Column(verticalArrangement = Arrangement.spacedBy(SpaceMD)) {
        if (ink.capacityReached) {
            Text(
                text = stringResource(R.string.srs_ink_capacity),
                style = FontCaption.copy(color = MaterialTheme.colorScheme.error)
            )
        }

        // Multi-slot selector if more than 1 character
        if (ink.slots.size > 1) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(SpaceSM)
            ) {
                ink.slots.forEachIndexed { index, slot ->
                    val isActive = index == ink.active
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(RadiusMedium))
                            .background(if (isActive) PrimaryLight else Surface1)
                            .border(1.dp, if (isActive) Primary else Border, RoundedCornerShape(RadiusMedium))
                            .clickable(enabled = enabled && !ink.drawing) { model.activate(index) }
                            .padding(horizontal = 14.dp, vertical = 8.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = "Ô ${index + 1}: ${slot.selected ?: "□"}",
                            fontSize = 16.sp,
                            fontWeight = FontWeight.Medium,
                            color = if (isActive) Primary else TextSecondary
                        )
                    }
                }
            }
        }

        if (busy) {
            MiniProgressBar(progress = 0.8f, fillColor = Primary)
        }

        val statusText = when (ink.phase) {
            HandwritingPhase.Preparing -> stringResource(R.string.ink_preparing)
            HandwritingPhase.Downloading -> stringResource(R.string.ink_downloading)
            HandwritingPhase.Recognizing -> stringResource(R.string.ink_recognizing)
            HandwritingPhase.ModelError -> stringResource(R.string.ink_model_error)
            HandwritingPhase.RecognitionError -> stringResource(R.string.ink_recognition_error)
            HandwritingPhase.Empty -> stringResource(R.string.ink_empty)
            else -> null
        }
        statusText?.let {
            Text(
                text = it,
                style = FontCaption.copy(color = TextSecondary)
            )
        }

        if (ink.phase == HandwritingPhase.ModelError) {
            SecondaryButton(
                text = stringResource(R.string.srs_retry),
                onClick = model::prepare,
                enabled = enabled
            )
        }

        ink.slots.getOrNull(ink.active)?.let { slot ->
            key(attempt, ink.active) {
                CanvasArea(
                    strokes = slot.strokes,
                    enabled = enabled && !busy && ink.phase != HandwritingPhase.ModelError,
                    onBeginStroke = model::begin,
                    onCompleteStroke = model::end,
                    onUndo = model::undo,
                    onClear = model::clear,
                    placeholder = placeholder,
                    preserveInterrupted = true,
                    undoEnabled = enabled && !busy && !ink.drawing && slot.strokes.isNotEmpty(),
                    clearEnabled = enabled && !busy && !ink.drawing && slot.strokes.isNotEmpty()
                )
            }

            // PrimaryButton "Nhận diện" full width
            PrimaryButton(
                text = "Nhận diện",
                onClick = model::recognize,
                enabled = enabled && !busy && !ink.drawing && ink.phase != HandwritingPhase.ModelError && slot.strokes.isNotEmpty()
            )

            // ChipRow (hiện ra sau khi nhận diện): các chip chữ Hán được suggest, tap để chọn
            if (slot.candidates.isNotEmpty()) {
                ChipRow(
                    candidates = slot.candidates,
                    selected = slot.selected,
                    onSelect = model::select,
                    enabled = enabled && !busy
                )
            }
        }

        // Selected word summary & Submit action
        if (ink.word.isNotBlank()) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(RadiusMedium))
                    .background(Surface1)
                    .border(1.dp, Border, RoundedCornerShape(RadiusMedium))
                    .padding(horizontal = SpaceMD, vertical = SpaceSM),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = "Chữ đã chọn:",
                    style = FontLabel.copy(color = TextSecondary)
                )
                Text(
                    text = ink.word,
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Medium,
                    color = Primary
                )
            }

            PrimaryButton(
                text = stringResource(submitLabel),
                onClick = { submit(ink.word) },
                enabled = enabled && !ink.drawing && !busy && ink.word.isNotBlank()
            )
        }
    }
}
