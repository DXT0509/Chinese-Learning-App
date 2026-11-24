package com.example.chineselearningapp.feature.roadmap

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.LiveRegionMode
import androidx.compose.ui.semantics.liveRegion
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.createSavedStateHandle
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.lifecycle.viewmodel.initializer
import androidx.lifecycle.viewmodel.viewModelFactory
import com.example.chineselearningapp.R
import com.example.chineselearningapp.core.designsystem.*
import com.example.chineselearningapp.domain.model.ReviewSession
import com.example.chineselearningapp.domain.model.ReviewWord
import com.example.chineselearningapp.domain.model.RoadmapCompletion
import com.example.chineselearningapp.feature.dictionary.handwriting.HandwritingRecognizer
import com.example.chineselearningapp.feature.dictionary.handwriting.HandwritingStroke
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

enum class ReviewSubStep {
    MultipleChoice,
    Writing,
    Pronunciation
}

/**
 * 1. Trắc nghiệm: cho chữ Hán → chọn nghĩa đúng (4 đáp án)
 */
@Composable
fun MultipleChoiceScreen(
    word: ReviewWord,
    feedback: Boolean?,
    enabled: Boolean,
    onSubmit: (isCorrect: Boolean) -> Unit,
    onNext: () -> Unit,
    onBack: () -> Unit,
    status: @Composable () -> Unit = {}
) {
    // 4 options: 1 correct meaning + 3 distractors, shuffled stably per word
    val options = rememberSaveable(word.hanzi) {
        (listOf(word.meaning) + word.distractors).shuffled()
    }
    var selectedIndex by rememberSaveable(word.hanzi) { mutableStateOf<Int?>(null) }
    var submittedIndex by rememberSaveable(word.hanzi) { mutableStateOf<Int?>(null) }
    val result = if (submittedIndex == selectedIndex) feedback else null

    LessonFrame(
        title = stringResource(R.string.lesson_flow_choice),
        step = LessonStep.MultipleChoice,
        enabled = enabled,
        back = onBack,
        hint = stringResource(R.string.review_flow_mc_hint),
        action = stringResource(if (feedback != null) R.string.roadmap_continue else R.string.roadmap_answer),
        actionEnabled = selectedIndex != null,
        onAction = {
            if (feedback != null) {
                onNext()
            } else {
                selectedIndex?.let { index ->
                    submittedIndex = index
                    val isCorrect = options[index] == word.meaning
                    onSubmit(isCorrect)
                }
            }
        },
        status = status
    ) {
        // Cho chữ Hán (prompt)
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(8.dp),
            modifier = Modifier.padding(vertical = 12.dp)
        ) {
            Text(
                text = word.hanzi,
                fontSize = 54.sp,
                fontWeight = FontWeight.Bold,
                color = TextPrimary
            )
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text(
                    text = word.pinyin,
                    fontSize = 20.sp,
                    color = Primary,
                    fontWeight = FontWeight.Medium
                )
                LessonListen(word.hanzi)
            }
        }

        // 4 options arranged in a 2 x 2 grid
        options.chunked(2).forEachIndexed { row, rowOptions ->
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                rowOptions.forEachIndexed { col, optionText ->
                    val index = row * 2 + col
                    val isSelected = selectedIndex == index
                    val borderColor = when {
                        result == null -> if (isSelected) Primary else Border
                        isSelected && result == true -> Primary
                        isSelected && result == false -> MaterialTheme.colorScheme.error
                        optionText == word.meaning && result == false -> Primary // reveal correct answer on error
                        else -> Border
                    }
                    OutlinedButton(
                        onClick = { if (feedback == null) selectedIndex = index },
                        enabled = enabled && feedback == null,
                        shape = RoundedCornerShape(16.dp),
                        border = BorderStroke(2.dp, borderColor),
                        colors = ButtonDefaults.outlinedButtonColors(
                            containerColor = if (isSelected) Surface1 else Color.Transparent
                        ),
                        modifier = Modifier
                            .weight(1f)
                            .heightIn(min = 88.dp)
                    ) {
                        Text(
                            text = optionText,
                            style = FontBody,
                            textAlign = TextAlign.Center,
                            color = TextPrimary
                        )
                    }
                }
                if (rowOptions.size == 1) Spacer(Modifier.weight(1f))
            }
        }

        LessonFeedback(result)
    }
}

/**
 * 2. Viết: cho nghĩa tiếng Việt → vẽ chữ Hán trên canvas (WritingScreen 3B)
 */
@Composable
fun WritingScreen3B(
    word: ReviewWord,
    enabled: Boolean,
    onResult: (isCorrect: Boolean) -> Unit,
    onNext: () -> Unit,
    onBack: () -> Unit,
    onSkip: () -> Unit = {},
    recognizer: HandwritingRecognizer? = null,
    status: @Composable () -> Unit = {}
) {
    var strokes by remember(word.hanzi) { mutableStateOf<List<HandwritingStroke>>(emptyList()) }
    var recognizing by remember(word.hanzi) { mutableStateOf(false) }
    var showError by remember(word.hanzi) { mutableStateOf(false) }
    var showSuccess by remember(word.hanzi) { mutableStateOf(false) }
    val scope = rememberCoroutineScope()

    fun checkWriting() {
        if (!enabled || recognizing || strokes.isEmpty() || showSuccess) return
        recognizing = true
        showError = false

        scope.launch {
            try {
                val isCorrect = if (recognizer != null) {
                    recognizer.prepareModel {}
                    val candidates = recognizer.recognize(strokes)
                    candidates.firstOrNull() == word.hanzi
                } else {
                    // Fallback stroke evaluation: ink present with valid points
                    strokes.isNotEmpty() && strokes.all { it.isValid }
                }

                if (isCorrect) {
                    showSuccess = true
                    onResult(true)
                    delay(1200)
                    onNext()
                } else {
                    showError = true
                    onResult(false)
                    delay(2000)
                    showError = false
                }
            } catch (_: Exception) {
                showError = true
                onResult(false)
            } finally {
                recognizing = false
            }
        }
    }

    Box(
        Modifier
            .fillMaxSize()
            .background(Surface0)
    ) {
        Column(
            modifier = Modifier
                .widthIn(max = 680.dp)
                .fillMaxWidth()
                .align(Alignment.TopCenter)
                .fillMaxHeight()
                .navigationBarsPadding()
                .padding(horizontal = 24.dp, vertical = 12.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // Top App Bar
            Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                TextButton(onClick = onBack, enabled = enabled && !recognizing) {
                    Text(stringResource(R.string.writing_back))
                }
                Box(Modifier.weight(1f), contentAlignment = Alignment.Center) {
                    Surface(color = PrimaryMuted, shape = RoundedCornerShape(20.dp)) {
                        Text(
                            stringResource(R.string.roadmap_handwriting),
                            Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
                            color = Primary,
                            fontSize = 12.sp
                        )
                    }
                }
                TextButton(onClick = onSkip, enabled = enabled && !recognizing) {
                    Text(stringResource(R.string.roadmap_skip))
                }
            }

            status()
            if (recognizing) LinearProgressIndicator(Modifier.fillMaxWidth())

            // Prompt: Cho nghĩa tiếng Việt (+ pinyin hint), KHÔNG hiển thị chữ Hán
            Surface(
                modifier = Modifier
                    .fillMaxWidth()
                    .testTag("review_writing_prompt"),
                color = Surface1,
                shape = RoundedCornerShape(14.dp)
            ) {
                Column(
                    modifier = Modifier.padding(horizontal = 16.dp, vertical = 12.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Text(
                        text = stringResource(R.string.review_flow_write_instruction),
                        fontSize = 13.sp,
                        color = TextMuted
                    )
                    Text(
                        text = word.meaning,
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold,
                        color = TextPrimary,
                        textAlign = TextAlign.Center
                    )
                    Text(
                        text = "(${word.pinyin})",
                        fontSize = 16.sp,
                        color = Primary,
                        fontWeight = FontWeight.Medium
                    )
                }
            }

            // Canvas & Drawing Tools (Independent mode 3B: no guide character)
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                DrawingCanvas(
                    strokes = strokes,
                    enabled = enabled && !recognizing,
                    onBeginStroke = {},
                    onCompleteStroke = { stroke ->
                        if (stroke != null && stroke.isValid) {
                            strokes = strokes + stroke
                        }
                    },
                    guideCharacter = null, // Independent 3B: no background guide character
                    showGrid = true,
                    modifier = Modifier
                        .fillMaxWidth()
                        .weight(1f)
                )

                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    TextButton(
                        onClick = { if (strokes.isNotEmpty()) strokes = strokes.dropLast(1) },
                        enabled = enabled && !recognizing && strokes.isNotEmpty(),
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(10.dp)
                    ) {
                        Text(stringResource(R.string.ink_undo))
                    }
                    TextButton(
                        onClick = { strokes = emptyList() },
                        enabled = enabled && !recognizing && strokes.isNotEmpty(),
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(10.dp)
                    ) {
                        Text(stringResource(R.string.writing_clear))
                    }
                }
            }

            MascotChatBar(stringResource(R.string.writing_independent_hint))

            PrimaryButton(
                text = stringResource(R.string.writing_check),
                onClick = ::checkWriting,
                enabled = enabled && !recognizing && strokes.isNotEmpty(),
                loading = recognizing
            )
        }

        if (showError) {
            Surface(
                Modifier
                    .align(Alignment.BottomCenter)
                    .navigationBarsPadding()
                    .padding(24.dp)
                    .semantics { liveRegion = LiveRegionMode.Polite },
                color = Color(0xFFFCE8E8),
                shape = RoundedCornerShape(12.dp)
            ) {
                Text(
                    stringResource(R.string.writing_incorrect),
                    Modifier.padding(16.dp),
                    color = Color(0xFFA32D2D)
                )
            }
        }

        if (showSuccess) {
            Box(
                Modifier
                    .fillMaxSize()
                    .background(Color.White.copy(alpha = 0.92f))
                    .semantics { liveRegion = LiveRegionMode.Polite },
                contentAlignment = Alignment.Center
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Text("✓", color = Primary, fontSize = 64.sp)
                    Text(stringResource(R.string.writing_correct), color = Primary, style = FontTitle)
                }
            }
        }
    }
}

/**
 * Alias for WritingScreen 3B
 */
@Composable
fun WritingScreen(
    word: ReviewWord,
    enabled: Boolean,
    onResult: (isCorrect: Boolean) -> Unit,
    onNext: () -> Unit,
    onBack: () -> Unit,
    onSkip: () -> Unit = {},
    recognizer: HandwritingRecognizer? = null,
    status: @Composable () -> Unit = {}
) = WritingScreen3B(word, enabled, onResult, onNext, onBack, onSkip, recognizer, status)

/**
 * 3. Phát âm: cho chữ Hán + nghĩa → nói vào mic
 */
@Composable
fun PronunciationScreen(
    word: ReviewWord,
    state: LessonState,
    enabled: Boolean,
    onSpeechResult: (candidates: List<String>, durationMs: Int) -> Unit,
    onNext: () -> Unit,
    onBack: () -> Unit,
    onSkip: () -> Unit,
    progress: Float = 1f,
    status: @Composable () -> Unit = {}
) {
    PronunciationScreen(
        target = word.hanzi,
        meaning = word.meaning,
        pinyin = word.pinyin,
        mode = PronunciationMode.WORD,
        state = state,
        enabled = enabled,
        result = onSpeechResult,
        next = onNext,
        back = onBack,
        onSkip = onSkip,
        progress = progress,
        status = status
    )
}

/**
 * Full ReviewSession flow:
 * ReviewSession load → với mỗi từ trong words, lần lượt chạy:
 *   MultipleChoiceScreen(word) →
 *   WritingScreen 3B(word) →
 *   PronunciationScreen(word)
 * → sau khi hết tất cả từ → LessonSummaryScreen
 */
@Composable
fun ReviewSessionFlow(
    session: ReviewSession,
    lessonModel: LessonViewModel? = null,
    recognizer: HandwritingRecognizer? = null,
    onBack: () -> Unit = {},
    onFinish: (xp: Int) -> Unit = {}
) {
    val flowKey = "review:${session.groupId}"
    val lesson: LessonViewModel = lessonModel ?: viewModel(
        key = flowKey,
        factory = viewModelFactory { initializer { LessonViewModel(createSavedStateHandle()) } }
    )
    val state by lesson.state.collectAsStateWithLifecycle()

    var wordIndex by rememberSaveable(flowKey) { mutableIntStateOf(0) }
    var subStep by rememberSaveable(flowKey) { mutableStateOf(ReviewSubStep.MultipleChoice) }
    var isFinished by rememberSaveable(flowKey) { mutableStateOf(false) }

    // Khởi tạo lại mistakeCount = 0 khi bắt đầu ReviewSession mới
    LaunchedEffect(flowKey) {
        lesson.resetReviewSession()
    }

    val currentWord = session.words.getOrNull(wordIndex) ?: session.words.first()
    val enabled = !state.waiting

    // Back handling
    fun handleBack() {
        when {
            isFinished -> onBack()
            subStep == ReviewSubStep.Pronunciation -> {
                lesson.clearFeedback()
                subStep = ReviewSubStep.Writing
            }
            subStep == ReviewSubStep.Writing -> {
                lesson.clearFeedback()
                subStep = ReviewSubStep.MultipleChoice
            }
            subStep == ReviewSubStep.MultipleChoice && wordIndex > 0 -> {
                wordIndex--
                lesson.clearFeedback()
                subStep = ReviewSubStep.Pronunciation
            }
            else -> onBack()
        }
    }

    BackHandler { handleBack() }

    if (isFinished) {
        val finalXP = lesson.calculateReviewXp(50)
        val completion = remember(finalXP) { RoadmapCompletion(status = "COMPLETED", exp = finalXP) }

        LessonSummaryScreen(
            state = state,
            completion = completion,
            enabled = enabled,
            ready = true,
            back = onBack,
            complete = { onFinish(finalXP) },
            continuePath = { onFinish(finalXP) },
            resume = {},
            hasNextWord = false,
            replay = {
                wordIndex = 0
                subStep = ReviewSubStep.MultipleChoice
                isFinished = false
                lesson.resetReviewSession()
            },
            status = {}
        )
        return
    }

    when (subStep) {
        ReviewSubStep.MultipleChoice -> {
            MultipleChoiceScreen(
                word = currentWord,
                feedback = state.feedback,
                enabled = enabled,
                onSubmit = { isCorrect ->
                    lesson.recordAnswer(isCorrect)
                },
                onNext = {
                    lesson.clearFeedback()
                    subStep = ReviewSubStep.Writing
                },
                onBack = ::handleBack
            )
        }
        ReviewSubStep.Writing -> {
            WritingScreen3B(
                word = currentWord,
                enabled = enabled,
                onResult = { isCorrect ->
                    lesson.recordAnswer(isCorrect)
                },
                onNext = {
                    lesson.clearFeedback()
                    subStep = ReviewSubStep.Pronunciation
                },
                onBack = ::handleBack,
                onSkip = {
                    lesson.recordAnswer(false)
                    lesson.clearFeedback()
                    subStep = ReviewSubStep.Pronunciation
                },
                recognizer = recognizer
            )
        }
        ReviewSubStep.Pronunciation -> {
            PronunciationScreen(
                word = currentWord,
                state = state,
                enabled = enabled,
                onSpeechResult = { candidates, duration ->
                    lesson.speechResult(candidates, duration, currentWord.hanzi)
                },
                onNext = {
                    lesson.clearFeedback()
                    if (wordIndex < session.words.lastIndex) {
                        wordIndex++
                        lesson.nextReviewWord()
                        subStep = ReviewSubStep.MultipleChoice
                    } else {
                        lesson.finish()
                        isFinished = true
                    }
                },
                onBack = ::handleBack,
                onSkip = {
                    lesson.skipSpeech()
                    lesson.clearFeedback()
                    if (wordIndex < session.words.lastIndex) {
                        wordIndex++
                        lesson.nextReviewWord()
                        subStep = ReviewSubStep.MultipleChoice
                    } else {
                        lesson.finish()
                        isFinished = true
                    }
                }
            )
        }
    }
}

