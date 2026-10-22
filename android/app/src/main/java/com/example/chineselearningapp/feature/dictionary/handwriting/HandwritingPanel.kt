package com.example.chineselearningapp.feature.dictionary.handwriting

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.awaitEachGesture
import androidx.compose.foundation.gestures.awaitFirstDown
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.horizontalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.StrokeJoin
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import com.example.chineselearningapp.R
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.compose.LifecycleEventEffect

@Composable
fun HandwritingPanel(state: HandwritingState, model: HandwritingViewModel, insert: (String) -> Unit) {
    Surface(shape = MaterialTheme.shapes.large, color = MaterialTheme.colorScheme.surface) {
        Column(Modifier.fillMaxWidth().padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text(stringResource(R.string.ink_title), style = MaterialTheme.typography.titleMedium)
                TextButton(onClick = model::close) { Text(stringResource(R.string.ink_close)) }
            }
            Text(stringResource(R.string.ink_instruction), style = MaterialTheme.typography.bodySmall)
            HandwritingStatus(state.phase, model::retry)
            HandwritingCanvas(state.strokes, state.phase !in setOf(HandwritingPhase.Preparing,
                HandwritingPhase.Downloading, HandwritingPhase.ModelError), model::beginStroke, model::endStroke)
            FlowRow(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                TextButton(onClick = model::undo, enabled = state.strokes.isNotEmpty() && !state.drawing) {
                    Text(stringResource(R.string.ink_undo))
                }
                TextButton(onClick = model::clear, enabled = state.strokes.isNotEmpty() && !state.drawing) {
                    Text(stringResource(R.string.ink_clear))
                }
                Button(onClick = model::recognize, enabled = state.canRecognize) {
                    Text(stringResource(R.string.ink_recognize))
                }
            }
            if (state.candidates.isNotEmpty()) {
                Text(stringResource(R.string.ink_choose), style = MaterialTheme.typography.bodySmall)
                Row(Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    state.candidates.forEach { candidate ->
                        SuggestionChip(onClick = { model.select(candidate, insert) }, label = {
                            Text(candidate, style = MaterialTheme.typography.headlineMedium)
                        })
                    }
                }
                if (state.candidates.any { it.codePointCount(0, it.length) > 1 })
                    Text(stringResource(R.string.ink_multiple), style = MaterialTheme.typography.bodySmall)
            }
        }
    }
}

@Composable
private fun HandwritingStatus(phase: HandwritingPhase, retry: () -> Unit) {
    val message = when (phase) {
        HandwritingPhase.Preparing -> R.string.ink_preparing
        HandwritingPhase.Downloading -> R.string.ink_downloading
        HandwritingPhase.Recognizing -> R.string.ink_recognizing
        HandwritingPhase.ModelError -> R.string.ink_model_error
        HandwritingPhase.RecognitionError -> R.string.ink_recognition_error
        HandwritingPhase.Empty -> R.string.ink_empty
        else -> null
    }
    if (phase in setOf(HandwritingPhase.Preparing, HandwritingPhase.Downloading, HandwritingPhase.Recognizing))
        LinearProgressIndicator(Modifier.fillMaxWidth())
    message?.let { Text(stringResource(it), style = MaterialTheme.typography.bodySmall) }
    if (phase in setOf(HandwritingPhase.ModelError, HandwritingPhase.RecognitionError)) {
        TextButton(onClick = retry) { Text(stringResource(R.string.dictionary_retry)) }
    }
}

@Composable
fun HandwritingCanvas(strokes: List<HandwritingStroke>, enabled: Boolean,
    begin: () -> Unit, complete: (HandwritingStroke?) -> Unit) {
    val active = remember { mutableStateListOf<HandwritingPoint>() }
    var gestureEpoch by remember { mutableIntStateOf(0) }
    LifecycleEventEffect(Lifecycle.Event.ON_STOP) { gestureEpoch++ }
    val currentBegin by rememberUpdatedState(begin)
    val currentComplete by rememberUpdatedState(complete)
    val ink = MaterialTheme.colorScheme.onSurface
    val guide = MaterialTheme.colorScheme.outlineVariant
    val description = stringResource(R.string.ink_canvas)
    Canvas(Modifier.fillMaxWidth().heightIn(max = 260.dp).aspectRatio(1f)
        .background(MaterialTheme.colorScheme.surfaceContainerLow, MaterialTheme.shapes.large)
        .testTag("handwriting_canvas").semantics { contentDescription = description }
        .pointerInput(enabled, gestureEpoch) {
            if (!enabled) return@pointerInput
            val collector = StrokeCollector()
            try {
                awaitEachGesture {
                    val down = awaitFirstDown(requireUnconsumed = false)
                    fun point(position: Offset, time: Long) = HandwritingPoint(
                        (position.x / size.width * 1000f).coerceIn(0f, 1000f),
                        (position.y / size.height * 1000f).coerceIn(0f, 1000f), time)
                    down.consume()
                    val first = point(down.position, down.uptimeMillis)
                    collector.start(first); active.clear(); active.add(first); currentBegin()
                    var finished = false
                    try {
                        while (true) {
                            val event = awaitPointerEvent()
                            val change = event.changes.firstOrNull { it.id == down.id } ?: break
                            if (change.isConsumed) break
                            change.historical.forEach { sample ->
                                val historical = point(sample.position, sample.uptimeMillis)
                                collector.move(historical); active.add(historical)
                            }
                            val next = point(change.position, change.uptimeMillis)
                            change.consume()
                            if (!change.pressed) {
                                currentComplete(collector.finish(next)); finished = true; break
                            }
                            collector.move(next); active.add(next)
                        }
                    } finally {
                        collector.cancel(); active.clear()
                        if (!finished) currentComplete(null)
                    }
                }
            } finally { collector.cancel(); active.clear(); currentComplete(null) }
        }) {
        drawLine(guide, Offset(size.width / 2, 0f), Offset(size.width / 2, size.height))
        drawLine(guide, Offset(0f, size.height / 2), Offset(size.width, size.height / 2))
        fun render(points: List<HandwritingPoint>) {
            if (points.isEmpty()) return
            fun offset(p: HandwritingPoint) = Offset(p.x / 1000 * size.width, p.y / 1000 * size.height)
            val first = offset(points.first())
            if (points.size == 1 || points.all { it.x == points.first().x && it.y == points.first().y }) {
                drawCircle(ink, 2.dp.toPx(), first); return
            }
            val path = Path().apply {
                moveTo(first.x, first.y)
                points.drop(1).forEach { val p = offset(it); lineTo(p.x, p.y) }
            }
            drawPath(path, ink, style = Stroke(4.dp.toPx(), cap = StrokeCap.Round, join = StrokeJoin.Round))
        }
        strokes.forEach { render(it.points) }
        render(active)
    }
}
