package com.example.chineselearningapp.feature.roadmap

import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.text.Normalizer
import java.util.Locale
import com.example.chineselearningapp.feature.dictionary.handwriting.HandwritingStroke
import com.google.gson.Gson

enum class LessonStep {
    Introduction, Structure, GuidedWriting, IndependentWriting, Pinyin,
    Pronunciation, MultipleChoice, Translation, Speaking, Summary;

    val activityKind: String? get() = when (this) {
        Introduction -> "INTRODUCTION"
        Structure -> "COMPONENTS"
        GuidedWriting -> "STROKE_ORDER"
        IndependentWriting -> "HANDWRITING"
        Pronunciation, Speaking -> "PRONUNCIATION"
        MultipleChoice -> "QUIZ"
        else -> null
    }
}

data class LessonState(
    val step: LessonStep = LessonStep.Introduction,
    val lessonScore: Int = 100,
    val mistakeCount: Int = 0,
    val answerCount: Int = 0,
    val correctCount: Int = 0,
    val elapsedTime: Long = 0,
    val waiting: Boolean = false,
    val feedback: Boolean? = null,
    val pinyin: String = "",
    val pinyinMistakes: Int = 0,
    val speechAttempts: Int = 0,
    val speechText: String = "",
    val speechDuration: Int = 0,
    val translation: String = "",
    val translationSlot: Int = 0,
    val translationInk: List<HandwritingStroke> = emptyList(),
) {
    val accuracy: Int get() = if (answerCount == 0) 100 else correctCount * 100 / answerCount
}

/** One identity/run/word-scoped instance owns the whole flow, including revisits and restoration. */
class LessonViewModel(
    private val saved: SavedStateHandle,
    private val now: () -> Long = System::currentTimeMillis,
) : ViewModel() {
    private val started = saved.get<Long>("started") ?: now().also { saved["started"] = it }
    private val mutable = MutableStateFlow(LessonState(
        step = saved.get<String>("step")?.let(LessonStep::valueOf) ?: LessonStep.Introduction,
        lessonScore = saved["score"] ?: 100, mistakeCount = saved["mistakes"] ?: 0,
        answerCount = saved["answers"] ?: 0, correctCount = saved["correct"] ?: 0,
        elapsedTime = saved["elapsed"] ?: 0, pinyin = saved["pinyin"] ?: "",
        pinyinMistakes = saved["pinyinMistakes"] ?: 0,
        translation = saved["translation"] ?: "", translationSlot = saved["slot"] ?: 0,
        speechAttempts = saved["speechAttempts"] ?: 0,
        speechDuration = saved["speechDuration"] ?: 0, speechText = saved["speechText"] ?: "",
        waiting = saved["waiting"] ?: false, feedback = saved["feedback"],
        translationInk = saved.get<String>("translationInk")?.let {
            Gson().fromJson(it, Array<HandwritingStroke>::class.java).toList()
        }.orEmpty(),
    ))
    val state = mutable.asStateFlow()
    val lessonScore get() = state.value.lessonScore
    val elapsedTime get() = state.value.elapsedTime
    val mistakeCount get() = state.value.mistakeCount

    init {
        viewModelScope.launch {
            while (true) {
                tick()
                delay(1000)
            }
        }
    }
    private fun update(block: (LessonState) -> LessonState) {
        val value = block(mutable.value)
        mutable.value = value
        saved["step"] = value.step.name; saved["score"] = value.lessonScore
        saved["mistakes"] = value.mistakeCount; saved["answers"] = value.answerCount
        saved["correct"] = value.correctCount; saved["elapsed"] = value.elapsedTime
        saved["pinyin"] = value.pinyin; saved["pinyinMistakes"] = value.pinyinMistakes
        saved["translation"] = value.translation; saved["slot"] = value.translationSlot
        saved["speechAttempts"] = value.speechAttempts; saved["speechDuration"] = value.speechDuration
        saved["speechText"] = value.speechText; saved["waiting"] = value.waiting
        saved["feedback"] = value.feedback
    }
    private fun tick() {
        val pausedAt = saved.get<Long>("pausedAt")
        val totalPaused = saved.get<Long>("totalPaused") ?: 0L
        val end = saved.get<Long>("finished") ?: pausedAt ?: now()
        val elapsed = ((end - started - totalPaused) / 1000).coerceAtLeast(0)
        update { it.copy(elapsedTime = elapsed) }
    }
    fun pause() {
        if (!saved.contains("pausedAt")) {
            saved["pausedAt"] = now()
            tick()
        }
    }
    fun resume() {
        val pausedAt = saved.get<Long>("pausedAt")
        if (pausedAt != null) {
            val pausedDuration = (now() - pausedAt).coerceAtLeast(0)
            val totalPaused = (saved.get<Long>("totalPaused") ?: 0L) + pausedDuration
            saved["totalPaused"] = totalPaused
            saved.remove<Long>("pausedAt")
            tick()
        }
    }
    fun finish() {
        if (!saved.contains("finished")) {
            val pausedAt = saved.get<Long>("pausedAt")
            saved["finished"] = pausedAt ?: now()
        }
        tick()
    }
    fun next() {
        if (state.value.waiting || state.value.step == LessonStep.Summary) return
        move(LessonStep.entries[state.value.step.ordinal + 1])
    }
    fun back(): Boolean {
        if (state.value.waiting || state.value.step == LessonStep.Introduction) return false
        move(LessonStep.entries[state.value.step.ordinal - 1]); return true
    }
    private fun move(step: LessonStep) {
        val old = state.value
        if (old.step == LessonStep.Summary && step != LessonStep.Summary) saved.remove<Long>("finished")
        saved["feedback.${old.step}"] = old.feedback
        saved["speechAttempts.${old.step}"] = old.speechAttempts
        saved["speechDuration.${old.step}"] = old.speechDuration
        saved["speechText.${old.step}"] = old.speechText
        update { it.copy(step = step, feedback = saved["feedback.$step"],
            speechAttempts = saved["speechAttempts.$step"] ?: 0,
            speechDuration = saved["speechDuration.$step"] ?: 0, speechText = saved["speechText.$step"] ?: "") }
    }
    fun waitForEvidence() { update { it.copy(waiting = true, feedback = null) } }
    fun releaseWait() { update { it.copy(waiting = false) } }
    fun clearFeedback() { update { it.copy(feedback = null) } }
    fun goTo(step: LessonStep) { if (!state.value.waiting) move(step) }
    fun markWordKnown(onKnown: () -> Unit = {}) = onKnown()
    fun leaveLesson(onLeave: () -> Unit = {}) = onLeave()
    fun resetSpeech() { update { it.copy(speechAttempts = 0, speechDuration = 0, speechText = "", feedback = null) } }
    fun nextWord() {
        saved.remove<Long>("finished")
        saved.remove<Long>("pausedAt")
        saved.remove<Long>("totalPaused")
        LessonStep.entries.forEach { step ->
            listOf("feedback", "speechAttempts", "speechDuration", "speechText").forEach { saved.remove<Any>("$it.$step") }
        }
        clearTranslationInk()
        update { it.copy(step = LessonStep.Introduction, feedback = null, pinyin = "", pinyinMistakes = 0,
            translation = "", translationSlot = 0, speechAttempts = 0, speechDuration = 0, speechText = "") }
    }
    fun resetReviewSession() {
        saved.remove<Long>("finished")
        saved.remove<Long>("pausedAt")
        saved.remove<Long>("totalPaused")
        saved["started"] = now()
        saved["score"] = 100
        saved["mistakes"] = 0
        saved["answers"] = 0
        saved["correct"] = 0
        LessonStep.entries.forEach { step ->
            listOf("feedback", "speechAttempts", "speechDuration", "speechText").forEach { saved.remove<Any>("$it.$step") }
        }
        clearTranslationInk()
        update {
            it.copy(
                step = LessonStep.MultipleChoice,
                lessonScore = 100,
                mistakeCount = 0,
                answerCount = 0,
                correctCount = 0,
                feedback = null,
                pinyin = "",
                pinyinMistakes = 0,
                translation = "",
                translationSlot = 0,
                speechAttempts = 0,
                speechDuration = 0,
                speechText = "",
                waiting = false
            )
        }
    }
    fun nextReviewWord() {
        saved.remove<Long>("finished")
        saved.remove<Long>("pausedAt")
        saved.remove<Long>("totalPaused")
        LessonStep.entries.forEach { step ->
            listOf("feedback", "speechAttempts", "speechDuration", "speechText").forEach { saved.remove<Any>("$it.$step") }
        }
        clearTranslationInk()
        update {
            it.copy(
                step = LessonStep.MultipleChoice,
                feedback = null,
                pinyin = "",
                pinyinMistakes = 0,
                translation = "",
                translationSlot = 0,
                speechAttempts = 0,
                speechDuration = 0,
                speechText = "",
                waiting = false
            )
        }
    }
    fun calculateReviewXp(baseXP: Int = 50): Int =
        com.example.chineselearningapp.domain.model.calculateReviewXp(state.value.mistakeCount, baseXP)
    fun recordAnswer(correct: Boolean) {
        update { it.copy(feedback = correct, waiting = false, answerCount = it.answerCount + 1,
            correctCount = it.correctCount + if (correct) 1 else 0,
            lessonScore = if (correct) it.lessonScore else (it.lessonScore - 10).coerceAtLeast(10),
            mistakeCount = it.mistakeCount + if (correct) 0 else 1) }
    }
    fun recordWritingAnswer(correct: Boolean, stepName: String) {
        val sceneKey = "writing_mistake_$stepName"
        val alreadyCounted = saved.get<Boolean>(sceneKey) ?: false
        if (!correct) {
            if (!alreadyCounted) {
                saved[sceneKey] = true
                update { it.copy(feedback = false, waiting = false, answerCount = it.answerCount + 1,
                    lessonScore = (it.lessonScore - 10).coerceAtLeast(10),
                    mistakeCount = it.mistakeCount + 1) }
            } else {
                update { it.copy(feedback = false, waiting = false) }
            }
        } else {
            update { it.copy(feedback = true, waiting = false,
                answerCount = if (!alreadyCounted) it.answerCount + 1 else it.answerCount,
                correctCount = it.correctCount + 1) }
        }
    }
    fun consumeEvent(id: String): Boolean {
        val events = saved.get<ArrayList<String>>("events").orEmpty()
        if (id in events) return false
        saved["events"] = ArrayList((events + id).takeLast(500)); return true
    }
    fun editPinyin(value: String) { update { it.copy(pinyin = value.take(200), feedback = null) } }
    fun checkPinyin(target: String) {
        if (state.value.pinyin.isBlank() || state.value.feedback == true) return
        val correct = normalizePinyin(state.value.pinyin) == normalizePinyin(target)
        recordAnswer(correct)
        if (!correct) update { it.copy(pinyinMistakes = it.pinyinMistakes + 1) }
    }
    fun editTranslation(value: String) { update { it.copy(translation = value.take(500), feedback = null) } }
    fun checkTranslation(target: String) {
        if (state.value.translation.isNotBlank() && state.value.feedback != true)
            recordAnswer(normalizeChinese(state.value.translation) == normalizeChinese(target))
    }
    fun appendCharacter(character: String) {
        update { it.copy(translation = it.translation + character, translationSlot = it.translationSlot + 1, feedback = null) }
        clearTranslationInk()
    }
    fun addTranslationStroke(stroke: HandwritingStroke?) {
        if (stroke == null || !stroke.isValid || state.value.translationInk.sumOf { it.points.size } + stroke.points.size > 3000) return
        setTranslationInk(state.value.translationInk + stroke)
    }
    fun undoTranslationInk() = setTranslationInk(state.value.translationInk.dropLast(1))
    fun clearTranslationInk() = setTranslationInk(emptyList())
    private fun setTranslationInk(ink: List<HandwritingStroke>) {
        saved["translationInk"] = Gson().toJson(ink)
        update { it.copy(translationInk = ink) }
    }
    fun speechResult(candidates: List<String>, durationMs: Int, target: String) {
        if (durationMs < 1000 || state.value.feedback == true) return
        val topCandidates = candidates.take(3)
        val normalizedTarget = normalize(target)
        val isCorrect = topCandidates.any { normalize(it) == normalizedTarget }
        val recognizedText = topCandidates.firstOrNull().orEmpty()
        update {
            it.copy(
                feedback = isCorrect,
                answerCount = if (isCorrect) it.answerCount + 1 else it.answerCount,
                correctCount = if (isCorrect) it.correctCount + 1 else it.correctCount,
                speechAttempts = it.speechAttempts + 1,
                speechText = recognizedText,
                speechDuration = durationMs
            )
        }
    }

    fun speechResult(text: String, durationMs: Int, target: String) {
        speechResult(if (text.isBlank()) emptyList() else listOf(text), durationMs, target)
    }

    fun skipSpeech() {
        update {
            it.copy(
                mistakeCount = it.mistakeCount + 1,
                lessonScore = (it.lessonScore - 10).coerceAtLeast(10),
                answerCount = it.answerCount + 1,
                feedback = false
            )
        }
    }
}

internal fun normalize(s: String): String = s.trim().lowercase(Locale.ROOT)
    .replace(Regex("[.,!?;:\"'，。！？“”‘’、；：\\p{P}]"), "")
    .replace(Regex("\\s+"), " ")
    .trim()

internal fun normalizeChinese(value: String): String = Normalizer.normalize(value, Normalizer.Form.NFKC)
    .filter { it.isLetterOrDigit() }.lowercase(Locale.ROOT)

/** Tone-marked Pinyin is compared with tone intact; spaces/apostrophes and case are insignificant. */
internal fun normalizePinyin(value: String): String {
    val marked = "āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ"
    val bases = "aaaaeeeeiiiioooouuuuüüüü"
    return Normalizer.normalize(value, Normalizer.Form.NFC).lowercase(Locale.ROOT)
        .replace("u:", "ü").replace('v', 'ü').split(Regex("[\\s'’]+"))
        .joinToString("") { syllable ->
            var tone = 0
            val base = buildString {
                syllable.forEach { character ->
                    val index = marked.indexOf(character)
                    if (index >= 0) { append(bases[index]); tone = index % 4 + 1 }
                    else if (character.isLetterOrDigit()) append(character)
                }
            }
            (if (tone == 0) base else base + tone).replace("5", "")
        }
}
