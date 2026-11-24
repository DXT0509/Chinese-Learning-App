package com.example.chineselearningapp.feature.roadmap

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.saveable.rememberSaveableStateHolder
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.createSavedStateHandle
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.lifecycle.viewmodel.initializer
import androidx.lifecycle.viewmodel.viewModelFactory
import com.example.chineselearningapp.R
import com.example.chineselearningapp.domain.model.DefaultExerciseSelector
import com.example.chineselearningapp.domain.model.ExerciseSelector
import com.example.chineselearningapp.domain.model.LearnedWord
import com.example.chineselearningapp.domain.model.LearnerContext
import com.example.chineselearningapp.domain.model.Lesson
import com.example.chineselearningapp.domain.model.ListeningQuestion
import com.example.chineselearningapp.domain.model.Word

/** A stable flow cursor owns navigation; server receipts own required completion and XP. */
@Composable
internal fun RoadmapLessonFlow(server: RoadmapState, model: RoadmapViewModel, lessonModel: LessonViewModel? = null) {
    val content = checkNotNull(server.lesson)
    if (content.type == "REVIEW") {
        val session = remember(content.nodeVersionId) { content.toReviewSession() }
        ReviewSessionFlow(
            session = session,
            lessonModel = lessonModel,
            recognizer = model.handwritingRecognizer,
            onBack = { model.leave() },
            onFinish = {
                if (server.ready && server.completion == null) {
                    model.complete()
                }
                model.continuePath()
            }
        )
        return
    }
    val word = content.words.getOrNull(server.wordIndex) ?: return
    val flowKey = "lesson:${content.nodeVersionId}:${server.flowRunId}"
    val lesson: LessonViewModel = lessonModel ?: viewModel(key = flowKey, factory = viewModelFactory {
        initializer { LessonViewModel(createSavedStateHandle()) }
    })
    val state by lesson.state.collectAsStateWithLifecycle()
    val screenState = rememberSaveableStateHolder()
    val step = state.step
    val enabled = !server.busy && !server.deliveryPending && !server.recognizing && !state.waiting
    var confirmSkip by rememberSaveable(flowKey) { mutableStateOf(false) }
    val sentence = word.examples.firstOrNull().takeIf { content.examples.available }
    fun pending(kind: String) = content.activities.firstOrNull {
        it.kind == kind && (server.accepted[it.id]?.size ?: 0) < it.repetitions
    }
    fun selectPending(kind: String): Boolean {
        val activity = pending(kind) ?: return false
        model.chooseActivity(content.activities.indexOf(activity)); return true
    }
    fun canAct() = lesson.state.value.step == step && !lesson.state.value.waiting &&
        !model.state.value.busy && !model.state.value.deliveryPending && !model.state.value.recognizing
    fun next() { if (canAct()) lesson.next() }
    fun back() {
        if (!server.drawing && !server.deliveryPending) {
            if (state.waiting) lesson.releaseWait()
            lesson.back()
        }
    }
    fun acknowledge(kind: String) {
        if (!canAct()) return
        if (server.completion != null || !selectPending(kind)) lesson.next()
        else { lesson.waitForEvidence(); model.acknowledge() }
    }
    fun submitWriting() {
        if (!canAct()) return
        if (server.completion != null || !selectPending("HANDWRITING")) lesson.next()
        else { lesson.waitForEvidence(); model.handwriting() }
    }
    fun nextQuiz() {
        if (!canAct()) return
        if (server.completion != null || !selectPending("QUIZ")) lesson.next()
        else lesson.clearFeedback()
    }
    fun submitSpeech() {
        if (!canAct()) return
        if (server.completion != null || !selectPending("PRONUNCIATION")) lesson.next()
        else { lesson.waitForEvidence(); model.speaking(state.speechDuration) }
    }
    fun skipSpeech() {
        lesson.skipSpeech()
        if (server.completion != null || !selectPending("PRONUNCIATION")) lesson.next()
        else {
            lesson.next()
            model.speaking(state.speechDuration.coerceAtLeast(1000))
        }
    }
    DisposableEffect(model) { model.useSequentialFlow(); onDispose {} }
    BackHandler { back() }
    LaunchedEffect(flowKey) {
        // An interrupted local recognition has no durable delivery to wait for.
        if (state.waiting && !server.deliveryPending && server.lastSubmission == null) lesson.releaseWait()
    }
    LaunchedEffect(step, word.id) {
        if (step == LessonStep.Summary) lesson.finish()
        step.activityKind?.let { kind ->
            val activity = pending(kind) ?: content.activities.firstOrNull { it.kind == kind }
            activity?.let { model.chooseActivity(content.activities.indexOf(it)) }
        }
    }
    LaunchedEffect(server.completion) {
        if (server.completion != null) { lesson.releaseWait(); lesson.goTo(LessonStep.Summary); lesson.finish() }
    }
    LaunchedEffect(server.flowRunId) {
        if (server.completion == null && state.step == LessonStep.Summary) {
            lesson.goTo(LessonStep.Introduction)
        }
    }
    LaunchedEffect(step, server.ready) {
        if (step == LessonStep.Summary && server.wordIndex == content.words.lastIndex && server.ready && server.completion == null)
            model.complete()
    }
    LaunchedEffect(server.lastSubmission?.evidence?.requestId) {
        val receipt = server.lastSubmission ?: return@LaunchedEffect
        if (content.activities.firstOrNull { it.id == receipt.evidence.activityId }?.kind != step.activityKind) return@LaunchedEffect
        if (!state.waiting || !lesson.consumeEvent(receipt.evidence.requestId)) return@LaunchedEffect
        lesson.releaseWait()
        if (step == LessonStep.MultipleChoice) {
            lesson.recordAnswer(receipt.accepted) // Show feedback before the next authored question.
        } else if (receipt.accepted) {
            if (step == LessonStep.IndependentWriting) lesson.recordAnswer(true)
            if (step == LessonStep.Pronunciation || step.activityKind?.let { pending(it) } == null) lesson.next()
            else if (step == LessonStep.Speaking) lesson.resetSpeech()
        }
    }
    LaunchedEffect(server.writingFeedbackToken) {
        val token = server.writingFeedbackToken ?: return@LaunchedEffect
        if ((step == LessonStep.IndependentWriting || step == LessonStep.GuidedWriting) &&
            server.writingResult == false && lesson.consumeEvent(token)) {
            lesson.recordWritingAnswer(false, step.name)
        }
    }
    LaunchedEffect(server.writingSuccessToken) {
        val token = server.writingSuccessToken ?: return@LaunchedEffect
        if ((step == LessonStep.IndependentWriting || step == LessonStep.GuidedWriting) &&
            lesson.consumeEvent(token)) {
            lesson.recordWritingAnswer(true, step.name)
        }
    }
    LaunchedEffect(server.error, server.recognizing, server.busy) {
        if (server.error != null && !server.deliveryPending && !server.recognizing && !server.busy) lesson.releaseWait()
    }
    if (confirmSkip) AlertDialog(onDismissRequest = { confirmSkip = false },
        title = { Text(stringResource(R.string.roadmap_skip_question)) },
        confirmButton = { TextButton(onClick = { confirmSkip = false; model.skip() }) { Text(stringResource(R.string.roadmap_skip)) } },
        dismissButton = { TextButton(onClick = { confirmSkip = false }) { Text(stringResource(R.string.roadmap_keep_learning)) } })
    val status: @Composable () -> Unit = {
        RoadmapError(server.error, model::retry)
        if (server.busy || state.waiting) LinearProgressIndicator(Modifier.fillMaxWidth())
    }
    screenState.SaveableStateProvider("$flowKey:${word.id}:$step") {
        when (step) {
            LessonStep.Introduction -> WordIntroductionScreen(
                word = word,
                enabled = enabled,
                acknowledge = { acknowledge("INTRODUCTION") },
                onKnownWord = { model.markWordKnown() },
                onLeaveLesson = { model.leaveLesson() },
                onPauseLesson = { lesson.pause() },
                onResumeLesson = { lesson.resume() },
                progress = 0f / 9f,
                header = { status() }
            )
            LessonStep.Structure -> CharacterStructureScreen(
                word = word,
                lesson = content,
                enabled = enabled,
                onBack = ::back,
                onContinue = { acknowledge("COMPONENTS") },
                onSkip = { confirmSkip = true },
                canSkip = content.type == "NEW_WORD" && server.completion == null,
                status = status,
                progress = 1f / 9f,
                onKnownWord = { model.markWordKnown() },
                onLeaveLesson = { model.leaveLesson() },
                onPauseLesson = { lesson.pause() },
                onResumeLesson = { lesson.resume() },
            )
            LessonStep.GuidedWriting, LessonStep.IndependentWriting -> WritingScreen(
                state = server,
                model = model,
                onSkip = { confirmSkip = true },
                writingMode = if (step == LessonStep.GuidedWriting) WritingMode.Guided else WritingMode.Independent,
                onBack = ::back,
                onContinue = {
                    if (step == LessonStep.GuidedWriting) acknowledge("STROKE_ORDER")
                    else submitWriting()
                },
                onCheck = {
                    if (canAct()) {
                        model.checkWriting(submitEvidence = false)
                    }
                },
                allowMissingGuide = content.activities.none { it.kind == "STROKE_ORDER" }
            )
            LessonStep.Pinyin -> PinyinInputScreen(
                word = word,
                state = state,
                enabled = enabled,
                edit = lesson::editPinyin,
                check = { lesson.checkPinyin(word.pinyin) },
                next = ::next,
                back = ::back,
                progress = 4f / 9f,
                onKnownWord = { model.markWordKnown() },
                onLeaveLesson = { model.leaveLesson() },
                onPauseLesson = { lesson.pause() },
                onResumeLesson = { lesson.resume() },
                status = status
            )
            LessonStep.Pronunciation -> PronunciationScreen(
                target = word.simplified,
                meaning = shortenMeaning(word.meanings),
                pinyin = word.pinyin,
                mode = PronunciationMode.WORD,
                state = state,
                enabled = enabled,
                result = { candidates, duration -> lesson.speechResult(candidates, duration, word.simplified) },
                next = ::submitSpeech,
                back = ::back,
                onSkip = ::skipSpeech,
                progress = 5f / 9f,
                onKnownWord = { model.markWordKnown() },
                onLeaveLesson = { model.leaveLesson() },
                onPauseLesson = { lesson.pause() },
                onResumeLesson = { lesson.resume() },
                status = status
            )
            LessonStep.MultipleChoice -> {
                var localQIndex by rememberSaveable(server.flowRunId, word.id) { mutableIntStateOf(0) }
                val selector: ExerciseSelector = remember { DefaultExerciseSelector() }
                val questions = remember(server.flowRunId, word.id, content.nodeVersionId) {
                    val currentWord = Word(
                        hanzi = word.simplified,
                        pinyin = word.pinyin,
                        reading = word.sinoVietnamese,
                        meaning = shortenMeaning(word.meanings),
                        partOfSpeech = null,
                        notes = null,
                        audioId = content.audio.assetId.takeIf { content.audio.available } ?: "audio_${word.simplified}",
                        audio = content.audio.assetId.takeIf { content.audio.available } ?: "audio_${word.simplified}"
                    )
                    val otherWords = content.words.filter { it.id != word.id }.map {
                        LearnedWord(
                            word = Word(
                                hanzi = it.simplified,
                                pinyin = it.pinyin,
                                reading = it.sinoVietnamese,
                                meaning = shortenMeaning(it.meanings),
                                partOfSpeech = null,
                                notes = null,
                                audioId = "audio_${it.simplified}",
                                audio = "audio_${it.simplified}"
                            ),
                            masteryLevel = 1,
                            isDueForReview = false
                        )
                    }
                    val lessonData = Lesson(
                        id = content.nodeVersionId,
                        targetWord = currentWord,
                        words = listOf(currentWord),
                        exercises = content.exercises,
                        attemptIndex = server.flowRunId.hashCode()
                    )
                    val learnerContext = LearnerContext(
                        learnedRoadmapWords = otherWords,
                        savedWords = emptyList()
                    )
                    selector.selectListening(lessonData, learnerContext)
                }
                val questionCount = questions.size
                val question = questions.getOrElse(localQIndex) { questions.first() }
                ListeningChoiceScreen(
                    question = question,
                    onAnswerChecked = { isCorrect ->
                        lesson.recordAnswer(isCorrect)
                        if (selectPending("QUIZ")) {
                            model.choice(if (isCorrect) 0 else 1)
                        }
                    },
                    onContinue = {
                        if (localQIndex < questionCount - 1) {
                            localQIndex++
                            if (selectPending("QUIZ")) {
                                model.choice(0)
                            }
                        } else {
                            if (state.waiting) lesson.releaseWait()
                            if (selectPending("QUIZ")) {
                                model.choice(0)
                            }
                            lesson.next()
                        }
                    },
                    onBack = {
                        if (localQIndex > 0) {
                            localQIndex--
                        } else {
                            back()
                        }
                    },
                    progress = 6f / 9f,
                    onKnownWord = { model.markWordKnown() },
                    onLeaveLesson = { model.leaveLesson() },
                    onPauseLesson = { lesson.pause() },
                    onResumeLesson = { lesson.resume() },
                    status = status
                )
            }
            LessonStep.Translation -> TranslationScreen(sentence, state, lesson, enabled, model::recognizeCharacter, ::next, ::back)
            LessonStep.Speaking -> SpeakingScreen(
                sentence = sentence,
                fallbackTarget = word.simplified,
                state = state,
                enabled = enabled,
                result = { candidates, duration -> lesson.speechResult(candidates, duration, sentence?.simplified ?: word.simplified) },
                next = ::submitSpeech,
                back = ::back,
                onSkip = ::skipSpeech,
                progress = 8f / 9f,
                onKnownWord = { model.markWordKnown() },
                onLeaveLesson = { model.leaveLesson() },
                onPauseLesson = { lesson.pause() },
                onResumeLesson = { lesson.resume() },
                status = status
            )
            LessonStep.Summary -> LessonSummaryScreen(state, server.completion, enabled, server.ready, ::back,
                model::complete, {
                    if (server.wordIndex < content.words.lastIndex) { lesson.nextWord(); model.word(server.wordIndex + 1) } else model.continuePath()
                }, {
                    val missing = content.activities.firstOrNull { (server.accepted[it.id]?.size ?: 0) < it.repetitions }
                    val target = when (missing?.kind) {
                        "INTRODUCTION" -> LessonStep.Introduction
                        "COMPONENTS" -> LessonStep.Structure
                        "STROKE_ORDER" -> LessonStep.GuidedWriting
                        "HANDWRITING" -> LessonStep.IndependentWriting
                        "QUIZ" -> LessonStep.MultipleChoice
                        else -> LessonStep.Pronunciation
                    }
                    lesson.goTo(target)
                }, hasNextWord = server.wordIndex < content.words.lastIndex, replay = model::replay, status = status)
        }
    }
}
