package com.example.chineselearningapp

import androidx.lifecycle.SavedStateHandle
import com.example.chineselearningapp.feature.dictionary.handwriting.*
import com.example.chineselearningapp.feature.review.*
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.Assert.*
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class ReviewHandwritingTest {
    private class Recognizer : HandwritingRecognizer {
        var candidates = listOf("学", "字", "学生", "a", "学")
        var preparations = 0
        var modelError = false
        var recognitionError = false
        var gate: CompletableDeferred<Unit>? = null
        var received: List<HandwritingStroke>? = null
        override suspend fun prepareModel(onDownload: () -> Unit) {
            preparations++; onDownload(); gate?.await(); if (modelError) error("download")
        }
        override suspend fun recognize(strokes: List<HandwritingStroke>): List<String> {
            received = strokes; gate?.await(); if (recognitionError) error("recognition")
            return candidates
        }
        override fun close() = Unit
    }
    private val stroke = HandwritingStroke(listOf(HandwritingPoint(1f, 2f, 1), HandwritingPoint(3f, 4f, 2)))
    private fun scenario(block: suspend TestScope.(Recognizer, ReviewHandwritingViewModel, SavedStateHandle) -> Unit) = runTest {
        Dispatchers.setMain(StandardTestDispatcher(testScheduler))
        try {
            val fake = Recognizer(); val saved = SavedStateHandle()
            val model = ReviewHandwritingViewModel(fake, saved, "owner")
            block(fake, model, saved)
        } finally { Dispatchers.resetMain() }
    }
    private fun write(model: ReviewHandwritingViewModel) { model.begin(); model.end(stroke) }
    @Test fun nextWordReusesReadyRecognizerWithoutModelPreparation() = scenario { fake, model, _ ->
        model.open("first", 1); advanceUntilIdle(); assertEquals(1, fake.preparations)
        model.open("second", 2); advanceUntilIdle()
        assertEquals(1, fake.preparations); assertEquals(HandwritingPhase.Ready, model.state.value.phase)
        assertEquals(2, model.state.value.slots.size)
    }
    @Test fun singleCharacterRequiresExplicitCandidateSelection() = scenario { fake, model, _ ->
        model.open("attempt", 1); advanceUntilIdle(); write(model); model.recognize(); advanceUntilIdle()
        assertEquals(listOf("学", "字"), model.state.value.slots.single().candidates)
        assertEquals("", model.state.value.word)
        model.select("字"); assertEquals("字", model.state.value.word)
        assertEquals(listOf(stroke), fake.received)
        model.select("hidden answer"); assertEquals("字", model.state.value.word)
    }
    @Test fun multiCharacterSlotsCombineInOrderAndCorrectIndependently() = scenario { fake, model, _ ->
        model.open("attempt", 3); advanceUntilIdle()
        listOf("图", "书", "馆").forEachIndexed { index, character ->
            model.activate(index); write(model); fake.candidates = listOf(character)
            model.recognize(); advanceUntilIdle(); model.select(character)
        }
        assertEquals("图书馆", model.state.value.word)
        model.activate(1); fake.candidates = listOf("字"); model.recognize(); advanceUntilIdle()
        assertEquals("图书馆", model.state.value.word)
        model.select("字"); assertEquals("图字馆", model.state.value.word)
        assertEquals(1, model.state.value.slots[0].strokes.size)
    }
    @Test fun undoAndClearOnlyAffectActiveSlotAndInvalidateItsAnswer() = scenario { _, model, _ ->
        model.open("attempt", 2); advanceUntilIdle(); write(model); write(model)
        model.recognize(); advanceUntilIdle(); model.select("学")
        model.undo(); assertEquals(1, model.state.value.slots[0].strokes.size)
        assertNull(model.state.value.slots[0].selected)
        model.activate(1); write(model); model.clear()
        assertTrue(model.state.value.slots[1].strokes.isEmpty())
        assertEquals(1, model.state.value.slots[0].strokes.size)
    }
    @Test fun modelDownloadLoadingFailureAndRetry() = scenario { fake, model, _ ->
        fake.gate = CompletableDeferred(); fake.modelError = true
        model.open("attempt", 1); runCurrent()
        assertEquals(HandwritingPhase.Downloading, model.state.value.phase)
        fake.gate!!.complete(Unit); advanceUntilIdle()
        assertEquals(HandwritingPhase.ModelError, model.state.value.phase)
        fake.modelError = false; model.prepare(); advanceUntilIdle()
        assertEquals(HandwritingPhase.Ready, model.state.value.phase)
    }
    @Test fun recognitionLoadingFailureAndEmptyCanvas() = scenario { fake, model, _ ->
        model.open("attempt", 1); advanceUntilIdle(); model.recognize()
        assertEquals(HandwritingPhase.Empty, model.state.value.phase)
        assertNull(fake.received)
        write(model); fake.gate = CompletableDeferred(); fake.recognitionError = true
        model.recognize(); runCurrent(); assertEquals(HandwritingPhase.Recognizing, model.state.value.phase)
        fake.gate!!.complete(Unit); advanceUntilIdle()
        assertEquals(HandwritingPhase.RecognitionError, model.state.value.phase)
        fake.recognitionError = false; model.recognize(); advanceUntilIdle()
        assertEquals(HandwritingPhase.Candidates, model.state.value.phase)
    }
    @Test fun keyboardCannotReplaceHandwrittenAnswer() = scenario { _, model, _ ->
        model.open("attempt", 1); advanceUntilIdle(); write(model); model.recognize(); advanceUntilIdle(); model.select("学")
        model.switchMode(); model.edit("你好"); assertEquals("学", model.state.value.word)
        model.switchMode(); assertEquals("学", model.state.value.word)
        model.switchMode(); assertEquals("学", model.state.value.word)
    }
    @Test fun recreationRetainsStrokesSelectionSlotAndModeButPreparesModelAgain() = scenario { fake, model, saved ->
        model.open("attempt", 2); advanceUntilIdle(); write(model); model.recognize(); advanceUntilIdle(); model.select("学")
        model.activate(1); write(model); model.switchMode(); model.edit("学生")
        val restored = ReviewHandwritingViewModel(fake, SavedStateHandle(saved.keys().associateWith { saved.get<Any?>(it) }), "owner")
        restored.open("attempt", 2); advanceUntilIdle()
        assertEquals(model.state.value.slots, restored.state.value.slots)
        assertEquals(1, restored.state.value.active); assertFalse(restored.state.value.keyboard)
        assertEquals("", restored.state.value.word)
    }
    @Test fun newAttemptAndDifferentOwnerCannotRestorePreviousInk() = scenario { fake, model, saved ->
        model.open("attempt", 1); advanceUntilIdle(); write(model)
        val other = ReviewHandwritingViewModel(fake, saved, "other"); other.open("new", 1); advanceUntilIdle()
        assertTrue(other.state.value.slots.single().strokes.isEmpty())
        model.open("different", 1); advanceUntilIdle(); assertTrue(model.state.value.slots.single().strokes.isEmpty())
    }
    @Test fun lateRecognitionCannotWriteIntoAnotherSlot() = scenario { fake, model, _ ->
        model.open("attempt", 2); advanceUntilIdle(); write(model)
        fake.gate = CompletableDeferred(); model.recognize(); runCurrent(); model.activate(1)
        fake.gate!!.complete(Unit); advanceUntilIdle()
        assertTrue(model.state.value.slots.all { it.candidates.isEmpty() })
    }
    @Test fun missingCountBlocksInputWithoutGuessingFromHiddenAnswers() = scenario { _, model, _ ->
        model.open("attempt", null); advanceUntilIdle()
        assertFalse(model.state.value.keyboard); assertTrue(model.state.value.slots.isEmpty())
    }
    @Test fun noSingleCharacterCandidatesDoesNotInventAnAnswer() = scenario { fake, model, _ ->
        model.open("attempt", 1); advanceUntilIdle(); write(model); fake.candidates = listOf("学生", "")
        model.recognize(); advanceUntilIdle()
        assertEquals(HandwritingPhase.Empty, model.state.value.phase); assertEquals("", model.state.value.word)
    }
    @Test fun savedInkHasBoundedSizeAndOffersRecoveryAtCapacity() = scenario { _, model, _ ->
        model.open("attempt", 1); advanceUntilIdle()
        val longStroke = HandwritingStroke(List(500) { HandwritingPoint(it.toFloat(), 1f, it.toLong()) })
        repeat(60) { model.begin(); model.end(longStroke) }
        assertTrue(model.state.value.capacityReached)
        assertTrue(model.state.value.slots.single().strokes.sumOf { it.points.size } <= 6000)
        model.undo(); assertFalse(model.state.value.capacityReached)
        model.clear(); assertTrue(model.state.value.slots.single().strokes.isEmpty())
    }
}
