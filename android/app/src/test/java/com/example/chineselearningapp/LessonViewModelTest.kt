package com.example.chineselearningapp

import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModelStore
import com.example.chineselearningapp.feature.roadmap.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.*
import org.junit.Assert.*
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class LessonViewModelTest {
    private fun check(block: suspend TestScope.(MutableList<ViewModelStore>) -> Unit) = runTest {
        Dispatchers.setMain(StandardTestDispatcher(testScheduler))
        val stores = mutableListOf<ViewModelStore>()
        try { block(stores) } finally { stores.forEach(ViewModelStore::clear); Dispatchers.resetMain() }
    }
    private fun MutableList<ViewModelStore>.model(saved: SavedStateHandle = SavedStateHandle(), now: () -> Long = { 1000L }): LessonViewModel {
        val model = LessonViewModel(saved, now)
        add(ViewModelStore().also { it.put("lesson", model) })
        return model
    }
    @Test fun followsEveryStepAndBackPreservesScore() = check { stores ->
        val model = stores.model()
        assertEquals(100, model.lessonScore)
        model.recordAnswer(false)
        LessonStep.entries.forEach { expected ->
            assertEquals(expected, model.state.value.step)
            assertEquals(90, model.lessonScore)
            model.next()
        }
        LessonStep.entries.reversed().drop(1).forEach { expected ->
            assertTrue(model.back()); assertEquals(expected, model.state.value.step)
        }
        assertFalse(model.back()); assertEquals(1, model.mistakeCount)
    }
    @Test fun wrongAnswersDeductTenWithMinimumTenAndCorrectAnswersDoNotRestorePoints() = check { stores ->
        val model = stores.model()
        repeat(12) { model.recordAnswer(false) }
        model.recordAnswer(true)
        assertEquals(10, model.lessonScore)
        assertEquals(12, model.mistakeCount)
        assertEquals(7, model.state.value.accuracy)
    }
    @Test fun pinyinShowsAnswerAfterTwoMistakesAndAcceptsNumberedTones() = check { stores ->
        val model = stores.model()
        model.editPinyin("ni1"); model.checkPinyin("nǐ")
        model.editPinyin("ni2"); model.checkPinyin("nǐ")
        assertEquals(2, model.state.value.pinyinMistakes)
        assertEquals(80, model.lessonScore)
        model.editPinyin("NI3"); model.checkPinyin("nǐ")
        assertEquals(true, model.state.value.feedback)
        assertEquals(normalizePinyin("Nǐ hǎo"), normalizePinyin("ni3 hao3"))
        assertNotEquals(normalizePinyin("nī"), normalizePinyin("nǐ"))
    }
    @Test fun restorationKeepsCursorDraftsScoreAndElapsedTimeAndFreezesAtFinish() = check { stores ->
        var time = 1000L
        val saved = SavedStateHandle()
        val model = stores.model(saved) { time }
        model.goTo(LessonStep.Pinyin); model.editPinyin("ni2"); model.checkPinyin("nǐ")
        time = 62000L; runCurrent()
        assertEquals(61L, model.elapsedTime)
        val restored = stores.model(saved) { time }
        assertEquals(LessonStep.Pinyin, restored.state.value.step)
        assertEquals("ni2", restored.state.value.pinyin)
        assertEquals(90, restored.lessonScore)
        restored.finish(); time = 92000L; advanceTimeBy(2000); runCurrent()
        assertEquals(61L, restored.elapsedTime)
        assertEquals(1, restored.mistakeCount)
    }
    @Test fun waitingBlocksBackAndNextAndReceiptEventsAreConsumedOnce() = check { stores ->
        val model = stores.model()
        model.goTo(LessonStep.MultipleChoice); model.waitForEvidence()
        assertFalse(model.back()); model.next()
        assertEquals(LessonStep.MultipleChoice, model.state.value.step)
        assertTrue(model.consumeEvent("receipt-1")); assertFalse(model.consumeEvent("receipt-1"))
        model.releaseWait(); assertTrue(model.back())
    }
    @Test fun speechAllowsUnlimitedAttemptsWithoutMistakesUntilSkipAndMatchesTopThree() = check { stores ->
        val model = stores.model()
        model.goTo(LessonStep.Pronunciation)
        model.speechResult("错", 0, "你")
        assertEquals(0, model.mistakeCount)
        assertEquals(0, model.state.value.speechAttempts)
        // 4 failed attempts: no hard cap of 3, no mistake added, score remains 100
        repeat(4) { model.speechResult("错", 1200, "你") }
        assertEquals(4, model.state.value.speechAttempts)
        assertEquals(0, model.mistakeCount)
        assertEquals(100, model.lessonScore)
        assertEquals(false, model.state.value.feedback)
        // Preserves across back & next
        model.next(); model.back()
        assertEquals(4, model.state.value.speechAttempts)
        // Top 3 matching: candidate 2 matches target "你"
        model.speechResult(listOf("错1", "你", "错3"), 1200, "你")
        assertEquals(true, model.state.value.feedback)
        assertEquals(0, model.mistakeCount) // No mistake added on success!
        assertEquals(100, model.lessonScore)
        assertEquals(5, model.state.value.speechAttempts)
    }

    @Test fun speechNormalizesPunctuationAndWhitespaceAndSkipIncrementsMistakes() = check { stores ->
        val model = stores.model()
        model.goTo(LessonStep.Speaking)
        // 4th candidate does not match because only top 3 are taken
        model.speechResult(listOf("错1", "错2", "错3", "你好"), 1200, "你好！")
        assertEquals(false, model.state.value.feedback)
        assertEquals(0, model.mistakeCount)
        // Top 3 candidate with punctuation & whitespace difference matches
        model.speechResult(listOf("  nǐ hǎo  "), 1200, "Nǐ, hǎo!?")
        assertEquals(true, model.state.value.feedback)
        assertEquals(0, model.mistakeCount)
        assertEquals(100, model.lessonScore)

        // Reset and test skip
        model.resetSpeech()
        model.speechResult("错", 1200, "你好")
        assertEquals(0, model.mistakeCount)
        model.skipSpeech()
        assertEquals(1, model.mistakeCount)
        assertEquals(90, model.lessonScore)
    }
    @Test fun translationIgnoresPunctuationButNotWrongCharactersAndNextWordKeepsTotalScore() = check { stores ->
        val model = stores.model()
        model.editTranslation("你喝茶吗"); model.checkTranslation("你喝茶吗？")
        assertEquals(true, model.state.value.feedback)
        model.editTranslation("他喝茶吗"); model.checkTranslation("你喝茶吗？")
        assertEquals(false, model.state.value.feedback)
        model.nextWord()
        assertEquals(90, model.lessonScore)
        assertEquals(LessonStep.Introduction, model.state.value.step)
        assertEquals("", model.state.value.translation)
    }
    @Test fun pauseExcludesTimeFromElapsedTimeAndResumesCorrectly() = check { stores ->
        var time = 1000L
        val saved = SavedStateHandle()
        val model = stores.model(saved) { time }
        time = 15000L; advanceTimeBy(14000); runCurrent()
        assertEquals(14L, model.elapsedTime)
        model.pause()
        time = 25000L; advanceTimeBy(10000); runCurrent()
        assertEquals(14L, model.elapsedTime)
        model.resume()
        time = 26000L; advanceTimeBy(1000); runCurrent()
        assertEquals(15L, model.elapsedTime)
    }
}
