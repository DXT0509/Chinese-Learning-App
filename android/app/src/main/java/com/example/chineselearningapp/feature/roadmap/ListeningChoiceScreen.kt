package com.example.chineselearningapp.feature.roadmap

import android.widget.Toast
import androidx.activity.compose.BackHandler
import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.StrokeJoin
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.layout.boundsInRoot
import androidx.compose.ui.layout.onGloballyPositioned
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.em
import androidx.compose.ui.unit.sp
import com.example.chineselearningapp.core.datastore.AppPreferences
import com.example.chineselearningapp.core.designsystem.*
import com.example.chineselearningapp.domain.model.ListeningQuestion
import com.example.chineselearningapp.domain.model.Word
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlin.math.sin

private val SUCCESS_TITLES = listOf("Tai thính thật!", "Nghe chuẩn luôn!", "Đúng rồi!")

/**
 * ListeningChoiceScreen (Nghe -> chọn chữ).
 * Displays a 4-option grid of Hanzi characters for a listening question.
 */
@Composable
fun ListeningChoiceScreen(
    question: ListeningQuestion,
    onAnswerChecked: (isCorrect: Boolean) -> Unit = {},
    onContinue: () -> Unit,
    onBack: () -> Unit,
    modifier: Modifier = Modifier,
    progress: Float = 6f / 9f,
    onKnownWord: () -> Unit = {},
    onLeaveLesson: () -> Unit = {},
    onPauseLesson: () -> Unit = {},
    onResumeLesson: () -> Unit = {},
    status: @Composable () -> Unit = {}
) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    val scrollState = rememberScrollState()

    val appPreferences = remember(context) { AppPreferences(context.applicationContext) }
    val audioVolume by appPreferences.audioVolume.collectAsState(initial = 1.0f)
    val speech = rememberWordSpeech(question.answerWord.hanzi.orEmpty(), volume = audioVolume)
    val feedbackPlayer = rememberWritingFeedbackPlayer { audioVolume }

    var showSettingsSheet by rememberSaveable { mutableStateOf(false) }
    var selectedIndex by rememberSaveable(question.questionIndex) { mutableStateOf<Int?>(null) }
    var isEvaluated by rememberSaveable(question.questionIndex) { mutableStateOf(false) }
    var isAnswerCorrect by rememberSaveable(question.questionIndex) { mutableStateOf<Boolean?>(null) }
    var mistakeCount by rememberSaveable { mutableIntStateOf(0) }

    var showBanner by remember { mutableStateOf(false) }
    var successTitle by remember { mutableStateOf(SUCCESS_TITLES.first()) }
    var confettiTrigger by remember { mutableIntStateOf(0) }
    var gridCenter by remember { mutableStateOf(Offset.Zero) }

    // Autoplay audio once at 1.0 rate 300ms after entering screen / moving to new question
    LaunchedEffect(question.questionIndex, question.answerWord.hanzi) {
        showBanner = false
        selectedIndex = null
        isEvaluated = false
        isAnswerCorrect = null
        delay(300)
        speech.speakWithRate(1.0f)
    }

    fun handleBack() {
        if (showSettingsSheet) {
            showSettingsSheet = false
        } else {
            onBack()
        }
    }

    BackHandler(enabled = true) {
        handleBack()
    }

    LaunchedEffect(showSettingsSheet) {
        if (showSettingsSheet) {
            speech.stop()
            onPauseLesson()
        } else {
            onResumeLesson()
        }
    }

    fun handleCheck() {
        val chosenIndex = selectedIndex ?: return
        if (isEvaluated) return

        isEvaluated = true
        val chosenWord = question.options.getOrNull(chosenIndex)
        val correct = chosenWord?.hanzi == question.answerWord.hanzi
        isAnswerCorrect = correct
        onAnswerChecked(correct)

        if (correct) {
            successTitle = SUCCESS_TITLES.random()
            feedbackPlayer.playCorrect()
            confettiTrigger++
            showBanner = true
        } else {
            mistakeCount++
            feedbackPlayer.playIncorrect()
            showBanner = true
            // Replay correct audio once after 500ms
            coroutineScope.launch {
                delay(500)
                speech.speakWithRate(1.0f)
            }
        }
    }

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(Surface0)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .imePadding(),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // 1. Top bar
            LessonTopBar(
                progress = progress,
                canGoBack = true,
                onBack = { handleBack() },
                onSettings = { showSettingsSheet = true }
            )

            status()

            Column(
                modifier = Modifier
                    .weight(1f)
                    .widthIn(max = 680.dp)
                    .fillMaxWidth()
                    .verticalScroll(scrollState)
                    .padding(horizontal = 24.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // 2. Chip "👂 NGHE VÀ CHỌN": nền #efe8ff, viền 1.5dp #cdbdf2, chữ #5b36b0 11sp weight 500 letterSpacing 0.06em, bo 20dp, padding 4×12dp
                Surface(
                    shape = RoundedCornerShape(20.dp),
                    color = ListeningChipBg,
                    border = BorderStroke(1.5.dp, ListeningChipBorder),
                    modifier = Modifier.padding(top = 14.dp)
                ) {
                    Text(
                        text = "👂 NGHE VÀ CHỌN",
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 4.dp),
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Medium,
                        letterSpacing = 0.06.em,
                        color = ListeningPurple
                    )
                }

                // 3. Chấm tiến độ câu: hàng questionCount thanh nhỏ (22×6dp, bo 3dp, gap 6dp), căn giữa, margin top 10dp
                Row(
                    modifier = Modifier.padding(top = 10.dp),
                    horizontalArrangement = Arrangement.spacedBy(6.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    for (i in 0 until question.questionCount) {
                        val active = i <= question.questionIndex
                        val color = if (active) Primary else LessonBorder
                        Box(
                            modifier = Modifier
                                .size(width = 22.dp, height = 6.dp)
                                .background(color, RoundedCornerShape(3.dp))
                        )
                    }
                }

                // 4. Câu hỏi "Bạn nghe thấy chữ nào?" 15sp weight 500 #3b4a42, căn giữa, margin top 10dp
                Text(
                    text = "Bạn nghe thấy chữ nào?",
                    fontSize = 15.sp,
                    fontWeight = FontWeight.Medium,
                    color = ListeningQuestionText,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.padding(top = 10.dp)
                )

                // 5. Khu vực phát audio (margin top 14dp, căn giữa)
                AudioPlaybackArea(
                    isAudioPlaying = speech.isSpeaking,
                    onPlayNormal = { speech.speakWithRate(1.0f) },
                    onPlaySlow = { speech.speakWithRate(0.7f) },
                    modifier = Modifier.padding(top = 14.dp)
                )

                // 6. Lưới 2×2 đáp án (margin top 14dp, gap 12dp)
                AnimatedContent(
                    targetState = question.questionIndex,
                    transitionSpec = {
                        (slideInVertically(tween(300)) { it / 4 } + fadeIn(tween(300)))
                            .togetherWith(fadeOut(tween(200)))
                    },
                    label = "QuestionOptionGrid"
                ) { _ ->
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(top = 14.dp)
                            .onGloballyPositioned { coordinates ->
                                gridCenter = coordinates.boundsInRoot().center
                            },
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        question.options.chunked(2).forEachIndexed { rowIndex, rowWords ->
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(12.dp)
                            ) {
                                rowWords.forEachIndexed { colIndex, word ->
                                    val index = rowIndex * 2 + colIndex
                                    val isSelected = selectedIndex == index
                                    val isAnswerWord = word.hanzi == question.answerWord.hanzi

                                    val cardState = when {
                                        !isEvaluated -> if (isSelected) OptionCardState.Selected else OptionCardState.Normal
                                        isSelected && isAnswerWord -> OptionCardState.Correct
                                        isSelected && !isAnswerWord -> OptionCardState.Incorrect
                                        !isSelected && isAnswerWord -> OptionCardState.Correct // Reveal correct answer on error
                                        else -> OptionCardState.Normal
                                    }

                                    OptionCard(
                                        hanzi = word.hanzi.orEmpty(),
                                        state = cardState,
                                        enabled = !isEvaluated,
                                        onClick = {
                                            if (!isEvaluated) {
                                                selectedIndex = index
                                            }
                                        },
                                        modifier = Modifier.weight(1f)
                                    )
                                }
                                if (rowWords.size == 1) {
                                    Spacer(modifier = Modifier.weight(1f))
                                }
                            }
                        }
                    }
                }

                Spacer(modifier = Modifier.height(18.dp))

                // 7. Mascot row
                TigerMascot(
                    message = "Nghe kỹ rồi chọn chữ đúng nhé! 👂",
                    modifier = Modifier.fillMaxWidth()
                )

                Spacer(modifier = Modifier.height(24.dp))
            }

            // 8. PrimaryButton 3D "Kiểm tra": disabled (opacity 0.4) khi chưa chọn hoặc đang hiện banner
            Box(
                modifier = Modifier
                    .widthIn(max = 680.dp)
                    .fillMaxWidth()
                    .navigationBarsPadding()
                    .padding(horizontal = 24.dp, vertical = 12.dp)
            ) {
                LessonPrimary3DButton(
                    text = "Kiểm tra",
                    onClick = { handleCheck() },
                    enabled = selectedIndex != null && !isEvaluated && !showBanner
                )
            }
        }

        // Confetti burst from grid center
        ConfettiOverlay(
            trigger = confettiTrigger,
            originCenter = gridCenter
        )

        // ResultBanner sliding up from bottom
        AnimatedVisibility(
            visible = showBanner,
            enter = slideInVertically(
                initialOffsetY = { it },
                animationSpec = spring(dampingRatio = 0.65f, stiffness = Spring.StiffnessLow)
            ),
            exit = slideOutVertically(
                targetOffsetY = { it },
                animationSpec = tween(durationMillis = 200, easing = LinearEasing)
            ),
            modifier = Modifier.align(Alignment.BottomCenter)
        ) {
            val isCorrect = isAnswerCorrect == true
            ResultBanner(
                isCorrect = isCorrect,
                title = if (isCorrect) successTitle else "Chưa đúng rồi",
                subtitle = if (isCorrect) {
                    val pinyin = question.answerWord.pinyin.orEmpty()
                    val meaning = question.answerWord.meaning.orEmpty()
                    "${question.answerWord.hanzi.orEmpty()} · $pinyin · $meaning"
                } else {
                    "Đáp án đúng là"
                },
                buttonText = "Tiếp tục",
                onButton = {
                    showBanner = false
                    onContinue()
                },
                customAnswerChip = if (!isCorrect) {
                    {
                        Surface(
                            shape = RoundedCornerShape(12.dp),
                            color = Color.White,
                            border = BorderStroke(2.dp, DangerBorder)
                        ) {
                            Row(
                                modifier = Modifier.padding(horizontal = 14.dp, vertical = 6.dp),
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                Text(
                                    text = question.answerWord.hanzi.orEmpty(),
                                    fontSize = 26.sp,
                                    fontFamily = FontFamily.Serif,
                                    fontWeight = FontWeight.Normal,
                                    color = TextPrimary
                                )
                                val pinyinAndMeaning = listOfNotNull(
                                    question.answerWord.pinyin?.takeIf { it.isNotBlank() },
                                    question.answerWord.meaning?.takeIf { it.isNotBlank() }
                                ).joinToString(" · ")
                                if (pinyinAndMeaning.isNotBlank()) {
                                    Text(
                                        text = pinyinAndMeaning,
                                        fontSize = 14.sp,
                                        fontWeight = FontWeight.Medium,
                                        color = DangerColor
                                    )
                                }
                            }
                        }
                    }
                } else null
            )
        }

        // Lesson Settings Bottom Sheet
        if (showSettingsSheet) {
            LessonSettingsSheet(
                onKnownWord = onKnownWord,
                onLeaveLesson = onLeaveLesson,
                onDismiss = {
                    showSettingsSheet = false
                    onResumeLesson()
                }
            )
        }
    }
}

/**
 * Audio playback area:
 * - 88dp round speaker button (touch zone 96dp), radial gradient #8a63e0 -> #5b36b0, bottom shadow 6dp #3c2278
 * - 2 concentric wave circles behind speaker (alpha 0.2), active only when playing: scale 0.85 -> 1.6, alpha 0.8 -> 0, 1.1s loop, phase 0.35s
 * - 0.7x slow button next to speaker
 * - 7-column audio waveform below speaker (width 5dp, height 6-18dp, margin top 8dp)
 */
@Composable
private fun AudioPlaybackArea(
    isAudioPlaying: Boolean,
    onPlayNormal: () -> Unit,
    onPlaySlow: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier.fillMaxWidth(),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.Center,
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Spacer on left to keep speaker button centered
            Spacer(modifier = Modifier.width(68.dp))

            // Speaker button with concentric wave rings
            SpeakerButtonWithWaves(
                isAudioPlaying = isAudioPlaying,
                onClick = onPlayNormal
            )

            // 0.7x slow speed button on the right
            Box(
                modifier = Modifier
                    .width(68.dp)
                    .padding(start = 12.dp),
                contentAlignment = Alignment.CenterStart
            ) {
                SlowSpeedButton(onClick = onPlaySlow)
            }
        }

        // 7-column waveform bar
        WaveformBars(
            isAudioPlaying = isAudioPlaying,
            modifier = Modifier.padding(top = 8.dp)
        )
    }
}

/**
 * 88dp Round Speaker Button with 2 concentric wave rings behind it.
 */
@Composable
private fun SpeakerButtonWithWaves(
    isAudioPlaying: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val interactionSource = remember { MutableInteractionSource() }
    val isPressed by interactionSource.collectIsPressedAsState()

    val offsetY = if (isPressed) 4.dp else 0.dp
    val shadowY = if (isPressed) 2.dp else 6.dp

    // Infinite transition for the 2 concentric wave rings
    val transition = rememberInfiniteTransition(label = "SpeakerConcentricWaves")
    val waveTime by transition.animateFloat(
        initialValue = 0f,
        targetValue = 1100f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 1100, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "ConcentricWaveTime"
    )

    Box(
        modifier = modifier.size(96.dp),
        contentAlignment = Alignment.Center
    ) {
        // Wave rings behind speaker button (only active when playing)
        if (isAudioPlaying) {
            // Wave 1
            val t1 = (waveTime / 1100f).coerceIn(0f, 1f)
            val scale1 = 0.85f + 0.75f * t1
            val alpha1 = 0.8f * (1f - t1) * 0.25f

            Box(
                modifier = Modifier
                    .size(88.dp)
                    .graphicsLayer {
                        scaleX = scale1
                        scaleY = scale1
                    }
                    .background(ListeningPurple.copy(alpha = alpha1), CircleShape)
            )

            // Wave 2 (phase offset 350ms)
            val t2 = ((waveTime + 350f) % 1100f) / 1100f
            val scale2 = 0.85f + 0.75f * t2
            val alpha2 = 0.8f * (1f - t2) * 0.25f

            Box(
                modifier = Modifier
                    .size(88.dp)
                    .graphicsLayer {
                        scaleX = scale2
                        scaleY = scale2
                    }
                    .background(ListeningPurple.copy(alpha = alpha2), CircleShape)
            )
        }

        // Speaker Button 3D bottom shadow
        Box(
            modifier = Modifier
                .offset(y = shadowY)
                .size(88.dp)
                .background(ListeningSpeakerShadow, CircleShape)
        )

        // Speaker Button surface (radial gradient #8a63e0 -> #5b36b0)
        Box(
            modifier = Modifier
                .offset(y = offsetY)
                .size(88.dp)
                .shadow(elevation = 6.dp, shape = CircleShape, spotColor = ListeningSpeakerShadow)
                .background(
                    brush = Brush.radialGradient(
                        colors = listOf(ListeningSpeakerStart, ListeningPurple)
                    ),
                    shape = CircleShape
                )
                .clickable(
                    interactionSource = interactionSource,
                    indication = null,
                    onClick = onClick
                ),
            contentAlignment = Alignment.Center
        ) {
            SpeakerVectorIcon(modifier = Modifier.size(42.dp))
        }
    }
}

/**
 * 42dp White Vector Speaker Icon.
 */
@Composable
private fun SpeakerVectorIcon(modifier: Modifier = Modifier) {
    Canvas(modifier = modifier) {
        val w = size.width
        val h = size.height

        // Speaker horn body
        val path = Path().apply {
            moveTo(w * 0.12f, h * 0.36f)
            lineTo(w * 0.36f, h * 0.36f)
            lineTo(w * 0.60f, h * 0.16f)
            lineTo(w * 0.60f, h * 0.84f)
            lineTo(w * 0.36f, h * 0.64f)
            lineTo(w * 0.12f, h * 0.64f)
            close()
        }
        drawPath(path, Color.White)

        // Arc 1 (inner sound wave)
        val stroke1 = Stroke(width = 3.dp.toPx(), cap = StrokeCap.Round)
        drawArc(
            color = Color.White,
            startAngle = -38f,
            sweepAngle = 76f,
            useCenter = false,
            topLeft = Offset(w * 0.44f, h * 0.31f),
            size = Size(w * 0.38f, h * 0.38f),
            style = stroke1
        )

        // Arc 2 (outer sound wave)
        val stroke2 = Stroke(width = 3.dp.toPx(), cap = StrokeCap.Round)
        drawArc(
            color = Color.White,
            startAngle = -42f,
            sweepAngle = 84f,
            useCenter = false,
            topLeft = Offset(w * 0.52f, h * 0.20f),
            size = Size(w * 0.48f, h * 0.60f),
            style = stroke2
        )
    }
}

/**
 * Nút "0.7×" (nghe chậm) bên phải loa:
 * nền trắng, viền 2dp #cdbdf2, bottom shadow 3dp #cdbdf2, chữ #5b36b0 13sp weight 500, bo 14dp, padding 7×12dp.
 */
@Composable
private fun SlowSpeedButton(
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val interactionSource = remember { MutableInteractionSource() }
    val isPressed by interactionSource.collectIsPressedAsState()

    val offsetY = if (isPressed) 2.dp else 0.dp
    val shadowY = if (isPressed) 1.dp else 3.dp

    Box(
        modifier = modifier,
        contentAlignment = Alignment.TopStart
    ) {
        // Bottom shadow
        Box(
            modifier = Modifier
                .offset(y = shadowY)
                .background(ListeningChipBorder, RoundedCornerShape(14.dp))
                .padding(horizontal = 12.dp, vertical = 7.dp)
        ) {
            Text(
                text = "0.7×",
                fontSize = 13.sp,
                fontWeight = FontWeight.Medium,
                color = Color.Transparent
            )
        }

        // Button body
        Box(
            modifier = Modifier
                .offset(y = offsetY)
                .background(Color.White, RoundedCornerShape(14.dp))
                .border(2.dp, ListeningChipBorder, RoundedCornerShape(14.dp))
                .clickable(
                    interactionSource = interactionSource,
                    indication = null,
                    onClick = onClick
                )
                .padding(horizontal = 12.dp, vertical = 7.dp),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = "0.7×",
                fontSize = 13.sp,
                fontWeight = FontWeight.Medium,
                color = ListeningPurple
            )
        }
    }
}

/**
 * Thanh sóng âm 7 cột (rộng 5dp, cao 6–18dp) dưới loa:
 * đang phát -> cột màu #5b36b0 nhấp nhô lệch pha; chờ -> #d8cdf3
 */
@Composable
private fun WaveformBars(
    isAudioPlaying: Boolean,
    modifier: Modifier = Modifier
) {
    val staticHeights = listOf(7f, 10f, 14f, 18f, 14f, 10f, 7f)

    val transition = rememberInfiniteTransition(label = "WaveformBarsAnim")
    val wavePhase by transition.animateFloat(
        initialValue = 0f,
        targetValue = (2 * Math.PI).toFloat(),
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 650, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "WaveformPhase"
    )

    Row(
        modifier = modifier.height(18.dp),
        horizontalArrangement = Arrangement.spacedBy(4.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        for (i in 0 until 7) {
            val barHeight = if (isAudioPlaying) {
                val factor = (sin(wavePhase + i * 0.9f) + 1f) / 2f
                6.dp + 12.dp * factor
            } else {
                staticHeights[i].dp
            }
            val barColor = if (isAudioPlaying) ListeningPurple else ListeningWaveIdle

            Box(
                modifier = Modifier
                    .width(5.dp)
                    .height(barHeight)
                    .background(barColor, RoundedCornerShape(2.5.dp))
            )
        }
    }
}

private enum class OptionCardState {
    Normal,
    Selected,
    Correct,
    Incorrect
}

/**
 * OptionCard for 2x2 grid:
 * - Cao 104dp, bo 20dp, nền trắng, viền 2dp #d6e9de, bottom shadow 5dp #c8e0d2, chữ Hán serif 52sp căn giữa.
 * - Nhấn: translateY +3dp, shadow về 2dp.
 * - Đã chọn: viền #34c478, nền #e8f5ee, bottom shadow #b9dfc9, vòng ngoài 4dp #34c478 alpha 0.18, nâng lên translateY -2dp.
 * - ĐÚNG: thẻ chọn -> nền #dff5e8, viền #34c478, bottom shadow #34c478, huy hiệu tròn xanh #1a9a58 (24dp, icon dấu tích trắng) ở góc trên phải thẻ (lệch -8dp).
 * - SAI: thẻ chọn -> nền #fde8e8, viền #e5484d, bottom shadow #f0a8a8, rung ngang ±9dp 500ms, huy hiệu tròn đỏ #e5484d icon dấu X trắng.
 */
@Composable
private fun OptionCard(
    hanzi: String,
    state: OptionCardState,
    enabled: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val interactionSource = remember { MutableInteractionSource() }
    val isPressed by interactionSource.collectIsPressedAsState()
    val pressed = isPressed && enabled

    // Horizontal shake animation for incorrect card (±9dp 500ms)
    val shakeAnim = remember { Animatable(0f) }
    LaunchedEffect(state) {
        if (state == OptionCardState.Incorrect) {
            shakeAnim.snapTo(0f)
            shakeAnim.animateTo(
                targetValue = 0f,
                animationSpec = keyframes {
                    durationMillis = 500
                    0f at 0
                    -9f at 50
                    9f at 100
                    -9f at 150
                    9f at 200
                    -6f at 275
                    6f at 350
                    -3f at 425
                    0f at 500
                }
            )
        }
    }

    val baseOffsetY = when {
        pressed -> 3.dp
        state == OptionCardState.Selected -> (-2).dp
        else -> 0.dp
    }
    val shadowOffsetY = when {
        pressed -> 2.dp
        state == OptionCardState.Selected -> 5.dp
        else -> 5.dp
    }

    val backgroundColor = when (state) {
        OptionCardState.Normal -> Color.White
        OptionCardState.Selected -> PinyinBg // #e8f5ee
        OptionCardState.Correct -> SuccessBannerBg // #dff5e8
        OptionCardState.Incorrect -> DangerBannerBg // #fde8e8
    }

    val borderColor = when (state) {
        OptionCardState.Normal -> LessonBorder // #d6e9de
        OptionCardState.Selected -> CorrectGlowColor // #34c478
        OptionCardState.Correct -> CorrectGlowColor // #34c478
        OptionCardState.Incorrect -> ErrorColor // #e5484d
    }

    val shadowColor = when (state) {
        OptionCardState.Normal -> LessonShadow // #c8e0d2
        OptionCardState.Selected -> PinyinBorder // #b9dfc9
        OptionCardState.Correct -> CorrectGlowColor // #34c478
        OptionCardState.Incorrect -> DangerCardShadow // #f0a8a8
    }

    Box(
        modifier = modifier
            .height(112.dp)
            .graphicsLayer { translationX = shakeAnim.value },
        contentAlignment = Alignment.TopCenter
    ) {
        // Outer glow/ring 4dp #34c478 alpha 0.18 for selected state
        if (state == OptionCardState.Selected) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .offset(y = (-2).dp)
                    .height(108.dp)
                    .border(4.dp, CorrectGlowColor.copy(alpha = 0.18f), RoundedCornerShape(22.dp))
            )
        }

        // Bottom shadow box
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .offset(y = shadowOffsetY)
                .height(104.dp)
                .background(shadowColor, RoundedCornerShape(20.dp))
        )

        // Card surface
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .offset(y = baseOffsetY)
                .height(104.dp)
                .background(backgroundColor, RoundedCornerShape(20.dp))
                .border(2.dp, borderColor, RoundedCornerShape(20.dp))
                .clickable(
                    interactionSource = interactionSource,
                    indication = null,
                    enabled = enabled,
                    onClick = onClick
                ),
            contentAlignment = Alignment.Center
        ) {
            // Chinese Hanzi text in serif 52sp centered
            Text(
                text = hanzi,
                fontSize = 52.sp,
                fontFamily = FontFamily.Serif,
                fontWeight = FontWeight.Normal,
                color = TextPrimary,
                textAlign = TextAlign.Center
            )
        }

        // Result Badge at top right corner (24dp, offset -8dp)
        if (state == OptionCardState.Correct) {
            Box(
                modifier = Modifier
                    .align(Alignment.TopEnd)
                    .offset(x = 6.dp, y = (-6).dp)
                    .size(24.dp)
                    .background(SuccessStrokeColor, CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Canvas(modifier = Modifier.size(14.dp)) {
                    val stroke = Stroke(width = 2.4.dp.toPx(), cap = StrokeCap.Round, join = StrokeJoin.Round)
                    val path = Path().apply {
                        moveTo(size.width * 0.22f, size.height * 0.52f)
                        lineTo(size.width * 0.44f, size.height * 0.74f)
                        lineTo(size.width * 0.80f, size.height * 0.28f)
                    }
                    drawPath(path, Color.White, style = stroke)
                }
            }
        } else if (state == OptionCardState.Incorrect) {
            Box(
                modifier = Modifier
                    .align(Alignment.TopEnd)
                    .offset(x = 6.dp, y = (-6).dp)
                    .size(24.dp)
                    .background(ErrorColor, CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Canvas(modifier = Modifier.size(14.dp)) {
                    val stroke = Stroke(width = 2.4.dp.toPx(), cap = StrokeCap.Round)
                    drawLine(
                        color = Color.White,
                        start = Offset(size.width * 0.25f, size.height * 0.25f),
                        end = Offset(size.width * 0.75f, size.height * 0.75f),
                        strokeWidth = stroke.width,
                        cap = stroke.cap
                    )
                    drawLine(
                        color = Color.White,
                        start = Offset(size.width * 0.75f, size.height * 0.25f),
                        end = Offset(size.width * 0.25f, size.height * 0.75f),
                        strokeWidth = stroke.width,
                        cap = stroke.cap
                    )
                }
            }
        }
    }
}

