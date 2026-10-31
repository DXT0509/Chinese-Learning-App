package com.example.chineselearningapp.feature.review

import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.chineselearningapp.feature.dictionary.handwriting.*
import com.google.gson.Gson
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import com.example.chineselearningapp.domain.repository.*

data class CharacterInk(val strokes: List<HandwritingStroke> = emptyList(),
    val candidates: List<String> = emptyList(), val selected: String? = null)
data class ReviewInkState(val attempt: String = "", val slots: List<CharacterInk> = emptyList(),
    val active: Int = 0, val keyboard: Boolean = false, val text: String = "",
    val phase: HandwritingPhase = HandwritingPhase.Closed, val drawing: Boolean = false,
    val capacityReached: Boolean = false) {
    val word: String get() = if (slots.isNotEmpty() && slots.all { it.selected != null && it.selected in it.candidates && it.strokes.isNotEmpty() })
        slots.joinToString("") { checkNotNull(it.selected) } else ""
}

/** Separate flow keeps drawing/recognition updates outside the review screen state. */
class ReviewHandwritingViewModel(private val recognizer: HandwritingRecognizer,
    private val saved: SavedStateHandle, owner: String) : ViewModel() {
    private val gson = Gson()
    private val mutable = MutableStateFlow(ReviewInkState())
    val state = mutable.asStateFlow()
    private var prepared = false
    private var operation: Job? = null
    private var generation = 0
    init {
        if (saved.get<String>("inkOwner") != owner) saved.remove<String>("reviewInk")
        saved["inkOwner"] = owner
        saved.get<String>("reviewInk")?.let {
            runCatching { gson.fromJson(it, ReviewInkState::class.java) }.getOrNull()?.let { restored ->
                mutable.value = restored.copy(keyboard = false, text = "", phase = HandwritingPhase.Closed, drawing = false)
            }
        }
    }
    private fun persist() { saved["reviewInk"] = gson.toJson(state.value.copy(phase = HandwritingPhase.Closed, drawing = false)) }
    private fun cancel() { generation++; operation?.cancel(); operation = null }
    fun open(attempt: String, count: Int?) {
        if (state.value.attempt != attempt) {
            cancel()
            mutable.value = ReviewInkState(attempt, List(count?.coerceIn(1, 64) ?: 0) { CharacterInk() },
                keyboard = false,
                phase = if (prepared) HandwritingPhase.Ready else HandwritingPhase.Closed)
            persist()
        }
        if (state.value.phase == HandwritingPhase.Closed) prepare()
    }
    fun prepare() {
        cancel()
        val ticket = generation
        mutable.value = state.value.copy(phase = HandwritingPhase.Preparing)
        operation = viewModelScope.launch {
            try {
                recognizer.prepareModel { if (ticket == generation) mutable.value = state.value.copy(phase = HandwritingPhase.Downloading) }
                ensureActive()
                if (ticket == generation) { prepared = true; mutable.value = state.value.copy(phase = HandwritingPhase.Ready) }
            } catch (cancelled: CancellationException) { throw cancelled }
            catch (_: Exception) { if (ticket == generation) mutable.value = state.value.copy(phase = HandwritingPhase.ModelError) }
        }
    }
    // Kept as inert compatibility methods for old restored UI/test callers.
    fun switchMode() = Unit
    fun edit(@Suppress("UNUSED_PARAMETER") text: String) = Unit
    fun evidence(): ReviewInkEvidence? {
        if (state.value.word.isBlank()) return null
        return ReviewInkEvidence(characters = state.value.slots.map { slot ->
            ReviewInkCharacter(slot.strokes.map { stroke -> stroke.points.map { ReviewInkPoint(it.x, it.y, it.timeMillis) } },
                slot.candidates, checkNotNull(slot.selected))
        })
    }
    fun activate(index: Int) {
        if (index !in state.value.slots.indices || state.value.drawing) return
        cancel()
        mutable.value = state.value.copy(active = index, phase = if (prepared) HandwritingPhase.Ready else HandwritingPhase.Closed)
        persist()
        if (!prepared) prepare()
    }
    private fun updateSlot(transform: (CharacterInk) -> CharacterInk) {
        val current = state.value
        mutable.value = current.copy(slots = current.slots.mapIndexed { index, slot -> if (index == current.active) transform(slot) else slot })
        persist()
    }
    fun begin() {
        if (!prepared || state.value.slots.isEmpty()) return
        cancel()
        mutable.value = state.value.copy(drawing = true, phase = HandwritingPhase.Ready)
    }
    fun end(stroke: HandwritingStroke?) {
        if (!state.value.drawing) return
        mutable.value = state.value.copy(drawing = false)
        if (stroke?.isValid != true || stroke.points.size < 2 || stroke.points.map { it.x to it.y }.distinct().size < 2) return
        // Bound saved-state size. Keep endpoints and uniformly sample long gestures.
        val points = stroke.points.let { points -> if (points.size <= 128) points else
            List(128) { points[it * (points.size - 1) / 127] } }
        if (state.value.slots.sumOf { slot -> slot.strokes.sumOf { it.points.size } } + points.size > 6000) {
            mutable.value = state.value.copy(capacityReached = true)
            return
        }
        updateSlot { it.copy(strokes = it.strokes + HandwritingStroke(points), candidates = emptyList(), selected = null) }
    }
    fun undo() { cancel(); updateSlot { it.copy(strokes = it.strokes.dropLast(1), candidates = emptyList(), selected = null) }; ready() }
    fun clear() { cancel(); updateSlot { CharacterInk() }; ready() }
    private fun ready() { mutable.value = state.value.copy(phase = if (prepared) HandwritingPhase.Ready else HandwritingPhase.ModelError, drawing = false, capacityReached = false) }
    fun select(candidate: String) {
        if (candidate !in state.value.slots[state.value.active].candidates) return
        updateSlot { it.copy(selected = candidate) }
    }
    fun recognize() {
        val slot = state.value.slots.getOrNull(state.value.active) ?: return
        if (!prepared || state.value.drawing || state.value.phase == HandwritingPhase.Recognizing) return
        if (slot.strokes.isEmpty()) { mutable.value = state.value.copy(phase = HandwritingPhase.Empty); return }
        cancel()
        val ticket = generation
        mutable.value = state.value.copy(phase = HandwritingPhase.Recognizing)
        operation = viewModelScope.launch {
            try {
                val candidates = handwritingCandidates(recognizer.recognize(slot.strokes))
                    .filter { it.codePointCount(0, it.length) == 1 }
                ensureActive()
                if (ticket == generation) {
                    // Re-recognition never silently replaces a learner's confirmed choice.
                    updateSlot { it.copy(candidates = (candidates + listOfNotNull(it.selected)).distinct()) }
                    mutable.value = state.value.copy(phase = if (candidates.isEmpty()) HandwritingPhase.Empty else HandwritingPhase.Candidates)
                }
            } catch (cancelled: CancellationException) { throw cancelled }
            catch (_: Exception) { if (ticket == generation) mutable.value = state.value.copy(phase = HandwritingPhase.RecognitionError) }
        }
    }
    override fun onCleared() { cancel(); recognizer.close() }
}
