package com.example.chineselearningapp

import androidx.compose.ui.text.TextRange
import androidx.compose.ui.text.input.TextFieldValue
import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.ViewModelStore
import com.example.chineselearningapp.domain.model.DictionaryPage
import com.example.chineselearningapp.domain.model.DictionaryEntry
import com.example.chineselearningapp.domain.repository.DictionaryRepository
import com.example.chineselearningapp.feature.dictionary.DictionarySearchViewModel
import com.example.chineselearningapp.feature.dictionary.handwriting.*
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.Assert.*
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class HandwritingTest {
    private fun point(x: Float = 1f, time: Long = 1) = HandwritingPoint(x, 2f, time)
    private fun stroke(x: Float = 1f) = HandwritingStroke(listOf(point(x), point(x + 1, 2)))
    private class Recognizer : HandwritingRecognizer {
        var preparations = 0
        var calls = 0
        var closed = false
        var failPrepare = false
        var failRecognize = false
        var prepareGate: CompletableDeferred<Unit>? = null
        var gate: CompletableDeferred<Unit>? = null
        var received = emptyList<HandwritingStroke>()
        var results = listOf("你", "好", "你好", "𠀀", "not Han", "你")
        override suspend fun prepareModel(onDownload: () -> Unit) {
            preparations++; onDownload(); prepareGate?.await()
            if (failPrepare) error("offline")
        }
        override suspend fun recognize(strokes: List<HandwritingStroke>): List<String> {
            calls++; received = strokes
            val snapshot = results
            gate?.let { withContext(NonCancellable) { it.await() } }
            if (failRecognize) error("inference failed")
            return snapshot
        }
        override fun close() { closed = true }
    }
    private fun scenario(test: suspend TestScope.(Recognizer, HandwritingViewModel) -> Unit) = runTest {
        Dispatchers.setMain(StandardTestDispatcher(testScheduler))
        try { val adapter = Recognizer(); test(adapter, HandwritingViewModel(adapter)) }
        finally { Dispatchers.resetMain() }
    }
    private fun HandwritingViewModel.draw(stroke: HandwritingStroke = stroke()) { beginStroke(); endStroke(stroke) }

    @Test fun collectorPreservesPointsTimesAndBoundariesAndDiscardsCancelledGestures() {
        val collector = StrokeCollector()
        collector.move(point())
        assertNull(collector.finish(point()))
        collector.start(point()); collector.move(point(3f, 2))
        assertEquals(listOf(point(), point(3f, 2), point(4f, 3)), collector.finish(point(4f, 3))!!.points)
        collector.start(point()); collector.cancel(); assertNull(collector.finish(point()))
        collector.start(point(Float.NaN)); assertNull(collector.finish(point()))
        collector.start(point(time = 5)); assertNull(collector.finish(point(time = 2)))
    }
    @Test fun preparationReportsDownloadRetriesAndReusesPreparedModel() = scenario { fake, vm ->
        assertEquals(HandwritingPhase.Closed, vm.state.value.phase)
        fake.prepareGate = CompletableDeferred(); fake.failPrepare = true
        vm.open(); assertEquals(HandwritingPhase.Preparing, vm.state.value.phase)
        runCurrent(); assertEquals(HandwritingPhase.Downloading, vm.state.value.phase)
        vm.open(); assertEquals(1, fake.preparations)
        fake.prepareGate!!.complete(Unit); advanceUntilIdle()
        assertEquals(HandwritingPhase.ModelError, vm.state.value.phase)
        fake.failPrepare = false; vm.retry(); advanceUntilIdle()
        assertEquals(HandwritingPhase.Ready, vm.state.value.phase)
        vm.close(); vm.open(); advanceUntilIdle(); assertEquals(2, fake.preparations)
    }
    @Test fun orderedStrokesUndoClearAndEmptyValidation() = scenario { fake, vm ->
        vm.open(); advanceUntilIdle(); vm.recognize(); assertEquals(0, fake.calls)
        vm.draw(stroke(1f)); vm.draw(stroke(4f)); vm.undo()
        assertEquals(listOf(stroke(1f)), vm.state.value.strokes)
        vm.beginStroke(); assertFalse(vm.state.value.canRecognize); vm.endStroke(null)
        assertEquals(1, vm.state.value.strokes.size)
        vm.draw(stroke(7f)); vm.recognize(); advanceUntilIdle()
        assertEquals(listOf(stroke(1f), stroke(7f)), fake.received)
        vm.clear(); assertTrue(vm.state.value.strokes.isEmpty())
        assertTrue(vm.state.value.candidates.isEmpty()); assertFalse(vm.state.value.canRecognize)
    }
    @Test fun candidatesStayRankedAndCompleteAndOnlyExplicitSelectionInserts() = scenario { _, vm ->
        vm.open(); advanceUntilIdle(); vm.draw(); vm.recognize(); advanceUntilIdle()
        assertEquals(listOf("你", "好", "你好", "𠀀"), vm.state.value.candidates)
        var query = "学"
        vm.select("bogus") { query += it }; assertEquals("学", query)
        vm.select("你好") { query += it }; assertEquals("学你好", query)
        assertEquals(HandwritingPhase.Ready, vm.state.value.phase)
        assertTrue(vm.state.value.strokes.isEmpty()); assertTrue(vm.state.value.candidates.isEmpty())
    }
    @Test fun insertionUsesCaretAndReplacesForwardOrReversedSelection() {
        assertEquals("你", insertHandwriting(TextFieldValue(""), "你").text)
        assertEquals("你好", insertHandwriting(TextFieldValue("你", TextRange(1)), "好").text)
        val value = insertHandwriting(TextFieldValue("学生", TextRange(1)), "的")
        assertEquals("学的生", value.text); assertEquals(TextRange(2), value.selection)
        for (range in listOf(TextRange(0, 2), TextRange(2, 0)))
            assertEquals("你好", insertHandwriting(TextFieldValue("学生", range), "你好").text)
    }
    @Test fun supplementaryCharactersNeverSplitAndCompositionIsCommitted() {
        val value = insertHandwriting(TextFieldValue("𠀀生", TextRange(1), TextRange(0, 2)), "𠀁")
        assertEquals("𠀀𠀁生", value.text); assertEquals(TextRange(4), value.selection); assertNull(value.composition)
        assertEquals("你生", insertHandwriting(TextFieldValue("𠀀生", TextRange(1, 2)), "你").text)
        assertEquals("你生", insertHandwriting(TextFieldValue("𠀀生", TextRange(0, 1)), "你").text)
    }
    @Test fun cancelledNonCooperativeInferenceCannotRestoreCandidatesAfterAnyEdit() = scenario { fake, vm ->
        vm.open(); advanceUntilIdle()
        for (change in listOf<() -> Unit>({ vm.clear() }, { vm.undo() }, { vm.close() }, { vm.beginStroke(); vm.endStroke(null) })) {
            vm.open(); vm.draw(); fake.gate = CompletableDeferred()
            vm.recognize(); runCurrent(); val calls = fake.calls
            vm.recognize(); runCurrent(); assertEquals(calls, fake.calls)
            change(); fake.gate!!.complete(Unit); advanceUntilIdle()
            assertTrue(vm.state.value.candidates.isEmpty())
            assertNotEquals(HandwritingPhase.Candidates, vm.state.value.phase)
        }
    }
    @Test fun noCandidatesAndInferenceErrorsCanRetry() = scenario { fake, vm ->
        vm.open(); advanceUntilIdle(); vm.draw(); fake.results = emptyList()
        vm.recognize(); advanceUntilIdle(); assertEquals(HandwritingPhase.Empty, vm.state.value.phase)
        fake.failRecognize = true; vm.recognize(); advanceUntilIdle()
        assertEquals(HandwritingPhase.RecognitionError, vm.state.value.phase)
        fake.failRecognize = false; fake.results = listOf("你"); vm.retry(); advanceUntilIdle()
        assertEquals(listOf("你"), vm.state.value.candidates)
    }
    @Test fun supersededInferenceCannotReplaceNewerCandidates() = scenario { fake, vm ->
        vm.open(); advanceUntilIdle(); vm.draw()
        val old = CompletableDeferred<Unit>(); fake.gate = old; fake.results = listOf("你")
        vm.recognize(); runCurrent()
        vm.draw(); fake.gate = null; fake.results = listOf("好")
        vm.recognize(); runCurrent()
        assertEquals(listOf("好"), vm.state.value.candidates)
        old.complete(Unit); advanceUntilIdle(); assertEquals(listOf("好"), vm.state.value.candidates)
    }
    @Test fun viewModelStoreOwnsAndClosesRecognizer() = scenario { fake, _ ->
        val store = ViewModelStore()
        val provider = ViewModelProvider.create(store, object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : androidx.lifecycle.ViewModel> create(modelClass: Class<T>): T = HandwritingViewModel(fake) as T
        })
        provider[HandwritingViewModel::class].open(); advanceUntilIdle()
        assertFalse(fake.closed); store.clear(); assertTrue(fake.closed)
    }
    @Test fun selectedCandidateAndKeyboardShareTheExistingDebouncePipeline() = scenario { _, vm ->
        val queries = mutableListOf<String>()
        val repository = object : DictionaryRepository {
            override suspend fun search(query: String, offset: Int): DictionaryPage {
                queries += query; return DictionaryPage(emptyList(), null)
            }
            override suspend fun detail(entryId: String): DictionaryEntry = error("unused")
        }
        val search = DictionarySearchViewModel(repository, SavedStateHandle())
        var field = TextFieldValue("学", TextRange(1))
        search.edit(field.text); advanceUntilIdle()
        vm.open(); advanceUntilIdle(); vm.draw(); vm.recognize(); advanceUntilIdle()
        vm.select("你") { field = insertHandwriting(field, it); search.edit(field.text) }
        runCurrent(); advanceTimeBy(299); runCurrent(); assertEquals(listOf("学"), queries)
        advanceTimeBy(1); runCurrent(); assertEquals(listOf("学", "学你"), queries)
        search.edit("学生", true); advanceUntilIdle(); assertEquals(2, queries.size)
        search.edit("学生", false); advanceUntilIdle(); assertEquals("学生", queries.last())
    }
}
