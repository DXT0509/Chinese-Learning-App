package com.example.chineselearningapp.feature.review

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.stateDescription
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.compose.LocalLifecycleOwner
import androidx.lifecycle.repeatOnLifecycle
import com.example.chineselearningapp.R
import com.example.chineselearningapp.core.designsystem.*
import com.example.chineselearningapp.domain.repository.*
import com.example.chineselearningapp.feature.dictionary.handwriting.HandwritingPhase
import kotlinx.coroutines.delay

@Composable
fun ReviewScreen(
    state: ReviewUiState,
    model: ReviewViewModel,
    ink: ReviewHandwritingViewModel? = null,
    onLearnNewWords: () -> Unit = {}
) {
    val lifecycle = LocalLifecycleOwner.current.lifecycle
    val latest by rememberUpdatedState(state)
    LaunchedEffect(model, lifecycle) {
        fun inkReady(): Boolean = latest.selectedStage != "HANZI" || ink?.state?.value?.phase !in setOf(
            HandwritingPhase.Preparing, HandwritingPhase.Downloading, HandwritingPhase.Recognizing, HandwritingPhase.ModelError
        )
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

    val daily = state.dashboard?.dailyReview
    val activeMins = (daily?.activeSeconds ?: state.activeSeconds) / 60
    val targetMins = (daily?.targetSeconds ?: 1200) / 60

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Surface0)
            .statusBarsPadding()
            .pointerInput(model) { awaitPointerEventScope { while (true) { awaitPointerEvent(); model.interaction() } } }
            .imePadding()
            .padding(horizontal = SpaceLG, vertical = SpaceMD),
        verticalArrangement = Arrangement.spacedBy(SpaceMD)
    ) {
        // 1. StatusBar + Page title "Ôn tập" (FontTitle)
        Text(
            text = stringResource(R.string.review),
            style = FontTitle,
            color = TextPrimary
        )

        // 2. TodayRow: label "Hôm nay" + ProgressBar (flex 1) + "12 / 20 phút" (caption) — nằm ngang 1 hàng
        TodayRow(
            activeMinutes = activeMins,
            targetMinutes = targetMins
        )

        // Error banners if any
        state.error?.let { error ->
            ErrorCard(error = error, onRetry = model::retry, onRestart = model::restart, loading = state.loading)
        }

        if (state.loading && !state.sessionOpen) {
            AppProgressBar(progress = 0.6f)
        }

        // Main content scrollable area
        Column(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth()
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(SpaceXL)
        ) {
            if (!state.sessionOpen) {
                // ==========================================
                // 3. MÀN HÌNH ÔN TẬP TỔNG QUAN
                // ==========================================
                ReviewOverviewContent(
                    state = state,
                    model = model,
                    onLearnNewWords = onLearnNewWords
                )
            } else {
                // ==========================================
                // 4. MÀN HÌNH VẼ CHỮ / ÔN TỪ (TRONG SESSION)
                // ==========================================
                ReviewSessionContent(
                    state = state,
                    model = model,
                    ink = ink
                )
            }
        }
    }
}

/**
 * 3. MÀN HÌNH ÔN TẬP TỔNG QUAN
 */
@Composable
private fun ColumnScope.ReviewOverviewContent(
    state: ReviewUiState,
    model: ReviewViewModel,
    onLearnNewWords: () -> Unit
) {
    val dashboard = state.dashboard
    val dueCount = dashboard?.due ?: state.targets.count { it.due }
    val availableCount = dashboard?.available ?: state.targets.size
    val laterCount = (availableCount - dueCount).coerceAtLeast(0)
    val estimatedMinutes = maxOf(1, (dueCount * 1.5).toInt())

    // 3. HeroCard (border-radius 20dp, gradient bg từ Primary → PrimaryDark, padding 20dp)
    HeroCard(
        dueCount = dueCount,
        estimatedMinutes = estimatedMinutes,
        laterCount = laterCount
    )

    // Action buttons:
    // 4. PrimaryButton "Ôn tập ngay"
    PrimaryButton(
        text = if (model.hasAttempt()) "Tiếp tục ôn tập" else "Ôn tập ngay",
        onClick = { if (model.hasAttempt()) model.resume() else model.start() },
        enabled = !state.loading && (model.hasAttempt() || state.targets.isNotEmpty() || dueCount > 0),
        loading = state.loading
    )

    // 5. SecondaryButton "Học từ mới"
    SecondaryButton(
        text = "Học từ mới",
        onClick = onLearnNewWords,
        enabled = !state.loading
    )

    // 6. SectionLabel "MỨC ĐỘ THÀNH THẠO"
    SectionLabel("MỨC ĐỘ THÀNH THẠO")

    // 7. MasteryList — 6 rows
    MasteryList(distribution = dashboard?.masteryDistribution)

    if (state.exclusions.isNotEmpty()) {
        Text(
            text = stringResource(R.string.srs_excluded),
            style = FontCaption.copy(color = TextMuted)
        )
    }

    // Refresh action
    TextButton(
        onClick = model::refresh,
        enabled = !state.loading,
        modifier = Modifier.align(Alignment.CenterHorizontally)
    ) {
        Text(
            text = stringResource(R.string.srs_refresh),
            style = FontBody.copy(color = Primary, fontSize = 14.sp)
        )
    }
}

/**
 * 4. MÀN HÌNH VẼ CHỮ / ÔN TỪ (TRONG SESSION ÔN TẬP)
 */
@Composable
private fun ColumnScope.ReviewSessionContent(
    state: ReviewUiState,
    model: ReviewViewModel,
    ink: ReviewHandwritingViewModel?
) {
    val completed = state.completed
    val total = maxOf(1, state.sessionSize)
    val currentWordIndex = (completed + 1).coerceAtMost(total)
    val remaining = (total - completed).coerceAtLeast(0)
    val remainingMinutes = maxOf(1, (remaining * 1.5).toInt())
    val progress = (completed.toFloat() / total).coerceIn(0f, 1f)

    // 2. ProgressRow: "Từ X / Y" (TextSecondary) + "Còn Z từ · ~N phút" (TextMuted) + MiniProgressBar full width
    Column(verticalArrangement = Arrangement.spacedBy(SpaceXS)) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "Từ $currentWordIndex / $total",
                style = FontLabel.copy(fontWeight = FontWeight.Medium, color = TextSecondary)
            )
            Text(
                text = "Còn $remaining từ · ~$remainingMinutes phút",
                style = FontCaption.copy(color = TextMuted)
            )
        }
        MiniProgressBar(
            progress = progress,
            fillColor = Primary
        )
    }

    // Summary Screen when completed
    if (state.summary) {
        SessionSummaryCard(state = state, onLeave = model::leave)
        return
    }

    // Result card if word finished
    state.result?.let { result ->
        SessionResultCard(result = result, state = state, onNext = model::next)
    }

    state.stage?.let { stage ->
        ActiveStageCard(
            state = state,
            model = model,
            ink = ink,
            stage = stage
        )
    }

    if (state.loading) {
        AppProgressBar(progress = 0.7f)
        if (state.stage == null && state.result == null) {
            Text(
                text = stringResource(R.string.srs_preparing),
                style = FontLabel.copy(color = TextSecondary),
                modifier = Modifier.align(Alignment.CenterHorizontally)
            )
        }
    }

    // Secondary action to leave or return to dashboard
    TextButton(
        onClick = model::leave,
        enabled = !state.loading,
        modifier = Modifier.align(Alignment.CenterHorizontally)
    ) {
        Text(
            text = stringResource(R.string.srs_dashboard),
            style = FontBody.copy(color = TextSecondary, fontSize = 14.sp)
        )
    }
}

@Composable
private fun ColumnScope.ActiveStageCard(
    state: ReviewUiState,
    model: ReviewViewModel,
    ink: ReviewHandwritingViewModel?,
    stage: ReviewStage
) {
    val selected = state.selectedStage ?: stage.stage ?: "HANZI"
    val question = stage.draftQuestions[selected] ?: stage.question?.takeIf { selected == stage.stage }
    val feedback = stage.feedback.firstOrNull { it.stage == selected && it.firstCorrect != null }

    val promptData = remember(question?.prompt) {
        question?.prompt?.let { learnerPrompt(it) }
    }
    val meaning = promptData?.meaning ?: question?.prompt ?: ""
    val exampleOrCue = promptData?.cue

    // 3. WordCard (Surface1 bg, border-radius 16dp, padding 16dp):
    // - Nghĩa từ: 16sp weight 500, TextPrimary
    // - Ví dụ: 13sp TextMuted
    WordCard(
        meaning = meaning.ifEmpty { "Từ cần ôn tập" },
        exampleOrCue = exampleOrCue
    )

    // 4. ModeTabs — 2 tab ngang ("1. Chữ Hán" / "2. Pinyin"), border 1dp Border, active: border Primary, text Primary, bg PrimaryLight
    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(SpaceSM)) {
        listOf("HANZI" to "1. Chữ Hán", "PINYIN" to "2. Pinyin").forEach { (code, title) ->
            val isSelected = selected == code
            val stageFeedback = stage.feedback.firstOrNull { it.stage == code && it.firstCorrect != null }
            val status = stringResource(when {
                stageFeedback != null && stageFeedback.firstCorrect == true && !stageFeedback.assisted -> R.string.srs_correct
                stageFeedback != null -> R.string.srs_incorrect
                code in state.queuedStages -> R.string.srs_draft_saved
                else -> R.string.srs_unanswered
            })
            val borderColor = when {
                stageFeedback != null && (stageFeedback.firstCorrect != true || stageFeedback.assisted) -> MaterialTheme.colorScheme.error
                isSelected -> Primary
                else -> Border
            }
            val bgColor = when {
                isSelected -> PrimaryLight
                else -> Surface1
            }
            val textColor = when {
                stageFeedback != null && (stageFeedback.firstCorrect != true || stageFeedback.assisted) -> MaterialTheme.colorScheme.error
                isSelected -> Primary
                else -> TextSecondary
            }

            Box(
                modifier = Modifier
                    .weight(1f)
                    .clip(RoundedCornerShape(RadiusMedium))
                    .background(bgColor)
                    .border(1.dp, borderColor, RoundedCornerShape(RadiusMedium))
                    .selectable(
                        selected = isSelected,
                        enabled = !state.loading,
                        role = Role.Tab,
                        onClick = { model.selectStage(code) }
                    )
                    .semantics { stateDescription = status }
                    .testTag("review_stage_$code")
                    .padding(vertical = SpaceMD, horizontal = SpaceSM),
                contentAlignment = Alignment.Center
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(
                        text = title,
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Medium,
                        color = textColor
                    )
                    if (stageFeedback != null) {
                        Text(
                            text = status,
                            fontSize = 11.sp,
                            color = textColor
                        )
                    }
                }
            }
        }
    }

    if (feedback != null) {
        FeedbackBanner(feedback)
    } else if (question != null) {
        val enabled = !state.loading && state.error == null
        var showHint by rememberSaveable(stage.attemptId, selected) { mutableStateOf(false) }

        val action = if (selected == stage.stage) R.string.srs_submit else R.string.srs_save_draft

        if (selected == "HANZI" && ink != null) {
            val targetChar = if (showHint) question.simplified?.firstOrNull()?.toString() else null
            ReviewHandwritingInput(
                model = ink,
                attempt = stage.attemptId,
                count = question.characterCount,
                enabled = enabled,
                placeholder = targetChar,
                submitLabel = action
            ) { model.submit(it, emptyList(), ink.evidence()) }
        } else if (selected == "PINYIN") {
            ReviewPinyinInput(
                draftKey = stage.attemptId,
                value = state.draftText,
                onValueChange = { model.editDraft(it, state.draftSelections) },
                enabled = enabled
            )
            PrimaryButton(
                text = stringResource(action),
                onClick = { model.submit(state.draftText, state.draftSelections) },
                enabled = enabled && (if (question.inputMode == "TEXT") state.draftText.isNotBlank() else state.draftSelections.isNotEmpty())
            )
        }

        // 8. Link text "Khó quá? Xem gợi ý" (TextMuted, "Xem gợi ý" in Primary)
        val hintAnnotatedString = buildAnnotatedString {
            withStyle(SpanStyle(color = TextMuted, fontSize = 13.sp, fontWeight = FontWeight.Normal)) {
                append("Khó quá? ")
            }
            withStyle(SpanStyle(color = Primary, fontSize = 13.sp, fontWeight = FontWeight.Medium)) {
                append(if (showHint) "Ẩn gợi ý" else "Xem gợi ý")
            }
        }
        Text(
            text = hintAnnotatedString,
            modifier = Modifier
                .clickable { showHint = !showHint }
                .padding(vertical = SpaceXS)
                .align(Alignment.CenterHorizontally)
        )

        if (showHint) {
            Surface(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(RadiusMedium),
                color = PrimaryLight,
                border = BorderStroke(1.dp, PrimaryMuted)
            ) {
                Column(Modifier.padding(SpaceMD), verticalArrangement = Arrangement.spacedBy(SpaceXS)) {
                    Text(
                        text = stringResource(if (selected == "PINYIN") R.string.srs_pinyin_help else R.string.srs_draft_help),
                        style = FontBody.copy(fontSize = 13.sp, color = TextPrimary)
                    )
                    question.simplified?.let {
                        Text(
                            text = "Gợi ý chữ Hán: $it",
                            style = FontHeading.copy(color = Primary)
                        )
                    }
                }
            }
        }
    }

    if (stage.status == "READY_TO_FINALIZE" || feedback != null || state.feedbackVisible) {
        PrimaryButton(
            text = stringResource(R.string.srs_continue),
            onClick = model::continueReview,
            enabled = !state.loading && state.error == null
        )
    }

    LaunchedEffect(stage.attemptId, state.loading) {
        if (!state.loading) { withFrameNanos { }; model.rendered(stage.attemptId) }
    }
}

@Composable
private fun FeedbackBanner(feedback: ReviewFeedback) {
    val correct = feedback.firstCorrect == true && !feedback.assisted
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(RadiusMedium),
        color = if (correct) PrimaryLight else Color(0xFFFCE8E8),
        border = BorderStroke(1.dp, if (correct) Primary else Color(0xFFA32D2D))
    ) {
        Column(Modifier.padding(SpaceMD), verticalArrangement = Arrangement.spacedBy(SpaceXS)) {
            Text(
                text = stringResource(if (correct) R.string.srs_correct else R.string.srs_incorrect),
                color = if (correct) Primary else Color(0xFFA32D2D),
                fontSize = 16.sp,
                fontWeight = FontWeight.Medium
            )
            if (feedback.toneMismatches.isNotEmpty()) {
                Text(
                    text = stringResource(R.string.srs_wrong_tone, feedback.toneMismatches.joinToString(", ")),
                    style = FontBody.copy(fontSize = 13.sp, color = TextSecondary)
                )
            }
            if (feedback.syllableMismatches.isNotEmpty()) {
                Text(
                    text = stringResource(R.string.srs_wrong_syllable, feedback.syllableMismatches.joinToString(", ")),
                    style = FontBody.copy(fontSize = 13.sp, color = TextSecondary)
                )
            }
            if (!correct && feedback.correctAnswer.isNotEmpty()) {
                Text(
                    text = stringResource(R.string.srs_answer, feedback.correctAnswer.joinToString(", ")),
                    style = FontBody.copy(fontSize = 14.sp, fontWeight = FontWeight.Medium, color = TextPrimary)
                )
            }
        }
    }
}

@Composable
private fun SessionResultCard(result: ReviewResult, state: ReviewUiState, onNext: () -> Unit) {
    val pass = result.outcome == "PASS"
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(RadiusLarge),
        color = Surface1,
        border = BorderStroke(1.dp, Border)
    ) {
        Column(Modifier.padding(SpaceLG), verticalArrangement = Arrangement.spacedBy(SpaceMD)) {
            Text(
                text = stringResource(if (pass) R.string.srs_pass else R.string.srs_fail),
                fontSize = 20.sp,
                fontWeight = FontWeight.Medium,
                color = if (pass) Primary else Color(0xFFA32D2D)
            )
            if (result.previousMastery != null) {
                Text(
                    text = stringResource(R.string.srs_mastery_change, result.previousMastery, result.mastery),
                    style = FontBody.copy(color = TextSecondary)
                )
            }
            if (state.error == null) {
                PrimaryButton(
                    text = stringResource(if (state.completed + state.skippedCount >= state.sessionSize) R.string.srs_summary_open else R.string.srs_next_word),
                    onClick = onNext,
                    enabled = !state.loading
                )
            }
        }
    }
}

@Composable
private fun SessionSummaryCard(state: ReviewUiState, onLeave: () -> Unit) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(RadiusLarge),
        color = Surface1,
        border = BorderStroke(1.dp, Border)
    ) {
        Column(Modifier.padding(SpaceXL), verticalArrangement = Arrangement.spacedBy(SpaceMD)) {
            Text(
                text = stringResource(R.string.srs_summary_title),
                style = FontTitle,
                color = TextPrimary
            )
            Text(
                text = stringResource(R.string.srs_summary_counts, state.completed, state.passed, state.failed),
                style = FontBody.copy(color = TextSecondary)
            )
            Text(
                text = stringResource(R.string.srs_summary_change, state.masteryChange),
                style = FontBody.copy(color = Primary, fontWeight = FontWeight.Medium)
            )
            if (state.skippedCount > 0) {
                Text(
                    text = stringResource(R.string.srs_summary_skipped, state.skippedCount),
                    style = FontCaption.copy(color = TextMuted)
                )
            }
            PrimaryButton(
                text = "Quay về Ôn tập",
                onClick = onLeave
            )
        }
    }
}

@Composable
private fun ErrorCard(error: ReviewError, onRetry: () -> Unit, onRestart: () -> Unit, loading: Boolean) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(RadiusMedium),
        color = Color(0xFFFCE8E8),
        border = BorderStroke(1.dp, Color(0xFFA32D2D))
    ) {
        Column(Modifier.padding(SpaceMD), verticalArrangement = Arrangement.spacedBy(SpaceSM)) {
            Text(
                text = stringResource(when (error) {
                    ReviewError.Network -> R.string.srs_network
                    ReviewError.Timeout -> R.string.srs_timeout
                    ReviewError.Server -> R.string.srs_server
                    ReviewError.Response -> R.string.srs_response
                    ReviewError.Expired -> R.string.srs_expired
                    ReviewError.Invalid -> R.string.srs_invalid
                    ReviewError.Unavailable -> R.string.srs_unavailable
                    ReviewError.StartUnknown -> R.string.srs_start_unknown
                    ReviewError.EmptyPlan -> R.string.srs_empty_plan
                }),
                color = Color(0xFFA32D2D),
                fontSize = 14.sp
            )
            Row(horizontalArrangement = Arrangement.spacedBy(SpaceSM)) {
                if (error in listOf(ReviewError.Network, ReviewError.Timeout, ReviewError.Server, ReviewError.Response, ReviewError.Invalid, ReviewError.Unavailable)) {
                    SecondaryButton(
                        text = stringResource(R.string.srs_retry),
                        onClick = onRetry,
                        enabled = !loading,
                        modifier = Modifier.weight(1f)
                    )
                }
                if (error in listOf(ReviewError.Expired, ReviewError.StartUnknown, ReviewError.Unavailable)) {
                    SecondaryButton(
                        text = stringResource(R.string.srs_abandon),
                        onClick = onRestart,
                        enabled = !loading,
                        modifier = Modifier.weight(1f)
                    )
                }
            }
        }
    }
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
