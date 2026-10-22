package com.example.chineselearningapp.feature.dictionary.handwriting

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow

enum class HandwritingPhase { Closed, Preparing, Downloading, Ready, Recognizing, Candidates, Empty, ModelError, RecognitionError }
data class HandwritingState(
    val phase: HandwritingPhase = HandwritingPhase.Closed,
    val strokes: List<HandwritingStroke> = emptyList(),
    val candidates: List<String> = emptyList(),
    val drawing: Boolean = false,
) {
    val canRecognize get() = strokes.isNotEmpty() && !drawing && phase in setOf(
        HandwritingPhase.Ready, HandwritingPhase.Candidates, HandwritingPhase.Empty, HandwritingPhase.RecognitionError)
}

class HandwritingViewModel(private val recognizer: HandwritingRecognizer) : ViewModel() {
    private val mutableState = MutableStateFlow(HandwritingState())
    val state = mutableState.asStateFlow()
    private var operation: Job? = null
    private var generation = 0
    private var prepared = false

    fun open() {
        if (state.value.phase != HandwritingPhase.Closed) return
        if (prepared) mutableState.value = state.value.copy(phase = HandwritingPhase.Ready)
        else prepare()
    }
    private fun invalidate() { ++generation; operation?.cancel(); operation = null }
    private fun prepare() {
        invalidate()
        val ticket = generation
        mutableState.value = state.value.copy(phase = HandwritingPhase.Preparing, candidates = emptyList())
        operation = viewModelScope.launch {
            try {
                recognizer.prepareModel {
                    if (ticket == generation) mutableState.value = state.value.copy(phase = HandwritingPhase.Downloading)
                }
                ensureActive()
                if (ticket == generation) {
                    prepared = true
                    mutableState.value = state.value.copy(phase = HandwritingPhase.Ready)
                }
            } catch (cancelled: CancellationException) { throw cancelled }
            catch (_: Exception) {
                if (ticket == generation) mutableState.value = state.value.copy(phase = HandwritingPhase.ModelError)
            }
        }
    }
    fun close() {
        invalidate()
        mutableState.value = HandwritingState()
    }
    fun beginStroke() {
        if (!prepared || state.value.phase == HandwritingPhase.Closed) return
        invalidate()
        mutableState.value = state.value.copy(phase = HandwritingPhase.Ready, candidates = emptyList(), drawing = true)
    }
    fun endStroke(stroke: HandwritingStroke?) {
        if (!state.value.drawing) return
        mutableState.value = state.value.copy(drawing = false,
            strokes = state.value.strokes + listOfNotNull(stroke?.takeIf { it.isValid }))
    }
    fun undo() {
        if (!prepared || state.value.phase == HandwritingPhase.Closed) return
        invalidate()
        mutableState.value = state.value.copy(phase = HandwritingPhase.Ready,
            strokes = state.value.strokes.dropLast(1), candidates = emptyList(), drawing = false)
    }
    fun clear() {
        if (state.value.phase == HandwritingPhase.Closed) return
        if (prepared) {
            invalidate()
            mutableState.value = HandwritingState(HandwritingPhase.Ready)
        } else mutableState.value = state.value.copy(strokes = emptyList(), candidates = emptyList(), drawing = false)
    }
    fun recognize() {
        if (!state.value.canRecognize) return
        invalidate()
        val ticket = generation
        val strokes = state.value.strokes
        mutableState.value = state.value.copy(phase = HandwritingPhase.Recognizing, candidates = emptyList())
        operation = viewModelScope.launch {
            try {
                val candidates = handwritingCandidates(recognizer.recognize(strokes))
                ensureActive()
                if (ticket == generation) mutableState.value = state.value.copy(candidates = candidates,
                    phase = if (candidates.isEmpty()) HandwritingPhase.Empty else HandwritingPhase.Candidates)
            } catch (cancelled: CancellationException) { throw cancelled }
            catch (_: Exception) {
                if (ticket == generation) mutableState.value = state.value.copy(phase = HandwritingPhase.RecognitionError)
            }
        }
    }
    fun retry() { if (state.value.phase == HandwritingPhase.ModelError) prepare() else recognize() }
    fun select(candidate: String, insert: (String) -> Unit) {
        if (state.value.phase != HandwritingPhase.Candidates || candidate !in state.value.candidates) return
        insert(candidate)
        clear()
    }
    override fun onCleared() { invalidate(); recognizer.close() }
}
