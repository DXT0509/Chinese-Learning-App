package com.example.chineselearningapp.feature.review

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.selection.toggleable
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.stateDescription
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.input.pointer.pointerInput
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.compose.LocalLifecycleOwner
import androidx.lifecycle.repeatOnLifecycle
import kotlinx.coroutines.delay
import com.example.chineselearningapp.feature.dictionary.handwriting.HandwritingPhase
import com.example.chineselearningapp.R
import com.example.chineselearningapp.domain.repository.*

@Composable
fun ReviewScreen(state: ReviewUiState, model: ReviewViewModel, ink: ReviewHandwritingViewModel? = null) {
    val lifecycle = LocalLifecycleOwner.current.lifecycle
    val latest by rememberUpdatedState(state)
    LaunchedEffect(model, lifecycle) {
        fun inkReady(): Boolean = latest.selectedStage != "HANZI" || ink?.state?.value?.phase !in setOf(
            HandwritingPhase.Preparing, HandwritingPhase.Downloading, HandwritingPhase.Recognizing, HandwritingPhase.ModelError)
        lifecycle.repeatOnLifecycle(Lifecycle.State.RESUMED) {
            while (true) {
                val startedAt = System.nanoTime()
                val window = model.timingWindow()
                val eligible = !latest.loading && latest.stage != null && latest.sessionOpen && inkReady()
                delay(5000)
                if (eligible && inkReady()) model.activeTick((System.nanoTime() - startedAt) / 1_000_000, window)
            }
        }
    }
    Column(Modifier.fillMaxSize().background(MaterialTheme.colorScheme.surface)
        .pointerInput(model) { awaitPointerEventScope { while (true) { awaitPointerEvent(); model.interaction() } } }
        .imePadding().padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text(stringResource(R.string.review), style = MaterialTheme.typography.headlineMedium)
        state.dashboard?.dailyReview?.let { budget ->
            Text(stringResource(R.string.srs_daily_budget, budget.activeSeconds / 60, budget.targetSeconds / 60),
                style = MaterialTheme.typography.labelLarge)
            LinearProgressIndicator(progress = { (budget.activeSeconds.toFloat() / budget.targetSeconds).coerceIn(0f, 1f) }, Modifier.fillMaxWidth())
            Text(stringResource(R.string.srs_daily_backlog, budget.overdueCount, budget.estimatedBacklogSeconds / 60, budget.pendingCount),
                style = MaterialTheme.typography.bodySmall)
            if (state.summary || !state.sessionOpen && budget.activeSeconds >= budget.targetSeconds)
                OutlinedButton(model::continueBeyondTarget, enabled = !state.loading) { Text(stringResource(R.string.srs_continue_beyond)) }
        }
        if (state.sessionOpen) state.stage?.let { ReviewStageSelectors(state, model, it) }
        Column(Modifier.weight(1f).fillMaxWidth().verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(12.dp)) {
        state.error?.let { error ->
            Text(stringResource(when (error) {
                ReviewError.Network -> R.string.srs_network
                ReviewError.Timeout -> R.string.srs_timeout
                ReviewError.Server -> R.string.srs_server
                ReviewError.Response -> R.string.srs_response
                ReviewError.Expired -> R.string.srs_expired
                ReviewError.Invalid -> R.string.srs_invalid
                ReviewError.Unavailable -> R.string.srs_unavailable
                ReviewError.StartUnknown -> R.string.srs_start_unknown
                ReviewError.EmptyPlan -> R.string.srs_empty_plan
            }), color = MaterialTheme.colorScheme.error)
            if (error in listOf(ReviewError.Network, ReviewError.Timeout, ReviewError.Server, ReviewError.Response, ReviewError.Invalid, ReviewError.Unavailable))
                OutlinedButton(model::retry, enabled = !state.loading) { Text(stringResource(R.string.srs_retry)) }
            if (error in listOf(ReviewError.Expired, ReviewError.StartUnknown, ReviewError.Unavailable))
                OutlinedButton(model::restart, enabled = !state.loading) { Text(stringResource(R.string.srs_abandon)) }
        }
        if (!state.sessionOpen) {
            if (state.loading) LinearProgressIndicator(Modifier.fillMaxWidth())
            state.dashboard?.let { dashboard ->
                Text(stringResource(R.string.srs_due, dashboard.due), style = MaterialTheme.typography.headlineLarge)
                Text(stringResource(R.string.srs_later, dashboard.available - dashboard.due))
                dashboard.masteryDistribution?.let { buckets ->
                    FlowRow(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                        buckets.forEach { Text(stringResource(R.string.srs_mastery_bucket, it.level, it.count),
                            style = MaterialTheme.typography.bodySmall) }
                    }
                }
                if (state.targets.isEmpty()) Text(stringResource(R.string.srs_empty))
                if (state.exclusions.isNotEmpty()) Text(stringResource(R.string.srs_excluded), style = MaterialTheme.typography.bodySmall)
                Button(if (model.hasAttempt()) model::resume else { { model.start() } },
                    Modifier.fillMaxWidth().heightIn(min = 48.dp), enabled = !state.loading && (model.hasAttempt() || state.targets.isNotEmpty())) {
                    Text(stringResource(if (model.hasAttempt()) R.string.srs_resume else R.string.srs_start))
                }
                TextButton(model::refresh, enabled = !state.loading) { Text(stringResource(R.string.srs_refresh)) }
            }
        } else {
            Text(stringResource(R.string.srs_progress, state.completed, state.sessionSize), style = MaterialTheme.typography.labelLarge)
            LinearProgressIndicator(progress = { if (state.sessionSize == 0) 0f else (state.completed + state.skippedCount).toFloat() / state.sessionSize }, Modifier.fillMaxWidth())
            if (state.summary) {
                Text(stringResource(R.string.srs_summary_title), style = MaterialTheme.typography.headlineMedium)
                Text(stringResource(R.string.srs_summary_counts, state.completed, state.passed, state.failed))
                Text(stringResource(R.string.srs_summary_change, state.masteryChange))
                if (state.skippedCount > 0) Text(stringResource(R.string.srs_summary_skipped, state.skippedCount))
            }
            state.result?.let { result ->
                Text(stringResource(if (result.outcome == "PASS") R.string.srs_pass else R.string.srs_fail), style = MaterialTheme.typography.titleLarge)
                if (result.previousMastery != null) Text(stringResource(R.string.srs_mastery_change, result.previousMastery, result.mastery))
                if (state.error == null) Button(model::next, Modifier.fillMaxWidth(), enabled = !state.loading) {
                    Text(stringResource(if (state.completed + state.skippedCount >= state.sessionSize) R.string.srs_summary_open else R.string.srs_next_word))
                }
            }
            state.stage?.let { stage ->
                ActiveReview(state, model, ink, stage)
            }
            if (state.loading) {
                LinearProgressIndicator(Modifier.fillMaxWidth())
                if (state.stage == null && state.result == null) Text(stringResource(R.string.srs_preparing))
            }
            TextButton(model::leave, enabled = !state.loading) { Text(stringResource(R.string.srs_dashboard)) }
        }
    }
    }
}

@Composable
private fun ReviewStageSelectors(state: ReviewUiState, model: ReviewViewModel, stage: ReviewStage) {
    val selected = state.selectedStage ?: stage.stage ?: "HANZI"
    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
        listOf("HANZI", "PINYIN").forEach { code ->
            val feedback = stage.feedback.firstOrNull { it.stage == code && it.firstCorrect != null }
            val status = stringResource(when {
                feedback != null && feedback.firstCorrect == true && !feedback.assisted -> R.string.srs_correct
                feedback != null -> R.string.srs_incorrect
                code in state.queuedStages -> R.string.srs_draft_saved
                else -> R.string.srs_unanswered
            })
            val color = when {
                feedback != null && (feedback.firstCorrect != true || feedback.assisted) -> MaterialTheme.colorScheme.error
                selected == code || feedback != null -> MaterialTheme.colorScheme.primary
                else -> MaterialTheme.colorScheme.outline
            }
            Column(Modifier.weight(1f).border(if (selected == code) 2.dp else 1.dp, color, RoundedCornerShape(12.dp))
                .selectable(selected == code, enabled = !state.loading, role = Role.Tab, onClick = { model.selectStage(code) })
                .semantics { stateDescription = status }.testTag("review_stage_$code").padding(8.dp)) {
                Text(stringResource(stageTitle(code)), style = MaterialTheme.typography.labelLarge)
                Text(status, color = color, style = MaterialTheme.typography.labelSmall)
            }
        }
    }
 }

@Composable
private fun ActiveReview(state: ReviewUiState, model: ReviewViewModel, ink: ReviewHandwritingViewModel?, stage: ReviewStage) {
    val selected = state.selectedStage ?: stage.stage ?: "HANZI"
    val feedback = stage.feedback.firstOrNull { it.stage == selected && it.firstCorrect != null }
    val question = stage.draftQuestions[selected] ?: stage.question?.takeIf { selected == stage.stage }
    if (feedback != null) {
        Feedback(feedback)
    } else if (question != null) {
        question.prompt?.let {
            val prompt = remember(it) { learnerPrompt(it) }
            Text(prompt.meaning, style = MaterialTheme.typography.headlineSmall)
            prompt.cue?.let { cue -> Text(cue, style = MaterialTheme.typography.bodySmall) }
        }
        question.simplified?.let { Text(it, fontSize = 36.sp) }
        val enabled = !state.loading && state.error == null
        var help by rememberSaveable(stage.attemptId, selected) { mutableStateOf(false) }
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.End) {
            TextButton({ help = !help }) { Text(stringResource(R.string.srs_help)) }
        }
        if (help) Text(stringResource(if (selected == "PINYIN") R.string.srs_pinyin_help else R.string.srs_draft_help), style = MaterialTheme.typography.bodySmall)
        val action = if (selected == stage.stage) R.string.srs_submit else R.string.srs_save_draft
        if (selected == "HANZI" && ink != null) {
            ReviewHandwritingInput(ink, stage.attemptId, question.characterCount, enabled, action) { model.submit(it, emptyList(), ink.evidence()) }
        } else if (selected == "PINYIN") {
            ReviewPinyinInput(stage.attemptId, state.draftText,
                { model.editDraft(it, state.draftSelections) }, enabled)
            Button({ model.submit(state.draftText, state.draftSelections) }, Modifier.fillMaxWidth(),
                enabled = enabled && (if (question.inputMode == "TEXT") state.draftText.isNotBlank() else state.draftSelections.isNotEmpty())) {
                Text(stringResource(action))
            }
        }
        if (selected in state.queuedStages) Text(stringResource(R.string.srs_draft_waiting), style = MaterialTheme.typography.bodySmall)
    } else Text(stringResource(R.string.srs_stage_waiting))
    if (stage.status == "READY_TO_FINALIZE" || feedback != null || state.feedbackVisible) {
        Button(model::continueReview, Modifier.fillMaxWidth(), enabled = !state.loading && state.error == null) { Text(stringResource(R.string.srs_continue)) }
    }
    LaunchedEffect(stage.attemptId, state.loading) {
        if (!state.loading) { withFrameNanos { }; model.rendered(stage.attemptId) }
    }
}

@Composable
private fun Feedback(feedback: ReviewFeedback) {
    val correct = feedback.firstCorrect == true && !feedback.assisted
    Text(stringResource(if (correct) R.string.srs_correct else R.string.srs_incorrect),
        color = if (correct) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.error,
        style = MaterialTheme.typography.titleMedium)
    if (feedback.toneMismatches.isNotEmpty()) Text(stringResource(R.string.srs_wrong_tone, feedback.toneMismatches.joinToString(", ")))
    if (feedback.syllableMismatches.isNotEmpty()) Text(stringResource(R.string.srs_wrong_syllable, feedback.syllableMismatches.joinToString(", ")))
    if (!correct && feedback.correctAnswer.isNotEmpty()) {
        val answers = feedback.correctAnswer
        Text(stringResource(R.string.srs_answer, answers.joinToString(", ")))
    }
}
private fun stageTitle(stage: String?) = when (stage) {
    "HANZI" -> R.string.srs_hanzi
    "PINYIN" -> R.string.srs_pinyin
    else -> R.string.srs_pos
}
internal fun displayReviewTime(value: String): String = runCatching {
    val normalized = value.replace(Regex("\\.\\d+"), "")
    val parser = java.text.SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ssXXX", java.util.Locale.ROOT)
    val date = requireNotNull(parser.parse(normalized))
    java.text.SimpleDateFormat("HH:mm · dd/MM/yyyy", java.util.Locale.forLanguageTag("vi")).format(date)
}.getOrDefault(value)
internal fun posLabel(code: String) = when (code) {
    "noun" -> R.string.srs_pos_noun
    "verb" -> R.string.srs_pos_verb
    "adjective" -> R.string.srs_pos_adjective
    "adverb" -> R.string.srs_pos_adverb
    "pronoun" -> R.string.srs_pos_pronoun
    "classifier" -> R.string.srs_pos_classifier
    "numeral" -> R.string.srs_pos_numeral
    "conjunction" -> R.string.srs_pos_conjunction
    "preposition" -> R.string.srs_pos_preposition
    "particle" -> R.string.srs_pos_particle
    "interjection" -> R.string.srs_pos_interjection
    "subject" -> R.string.srs_grammar_subject
    "predicate" -> R.string.srs_grammar_predicate
    "object" -> R.string.srs_grammar_object
    "attribute" -> R.string.srs_grammar_attribute
    "adverbial" -> R.string.srs_grammar_adverbial
    "complement" -> R.string.srs_grammar_complement
    "modal_modifier" -> R.string.srs_grammar_modal
    "independent_clause" -> R.string.srs_grammar_clause
    "greeting" -> R.string.srs_expression_greeting
    "farewell" -> R.string.srs_expression_farewell
    "gratitude" -> R.string.srs_expression_gratitude
    "apology" -> R.string.srs_expression_apology
    "wish" -> R.string.srs_expression_wish
    "bound_morpheme" -> R.string.srs_morpheme_bound
    "independent_word" -> R.string.srs_morpheme_word
    "quantity_phrase" -> R.string.srs_quantity_phrase
    else -> R.string.srs_pos_unknown
}
