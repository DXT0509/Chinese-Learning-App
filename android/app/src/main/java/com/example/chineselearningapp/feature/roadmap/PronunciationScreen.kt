package com.example.chineselearningapp.feature.roadmap

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.os.SystemClock
import android.provider.Settings
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import androidx.activity.compose.BackHandler
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.*
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInVertically
import androidx.compose.animation.slideOutVertically
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
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.PathEffect
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
import androidx.core.content.ContextCompat
import com.example.chineselearningapp.core.datastore.AppPreferences
import com.example.chineselearningapp.core.designsystem.*
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.text.Normalizer
import java.util.Locale

enum class PronunciationMode {
    WORD,
    SENTENCE
}

private enum class MicState {
    IDLE,
    LISTENING,
    PROCESSING
}

private val SUCCESS_TITLES = listOf("Phát âm chuẩn!", "Chuẩn luôn!", "Đỉnh thật!")

/**
 * Normalizes speech candidate and target:
 * lowercase, strips punctuation and surplus whitespace, NFC normalization.
 */
internal fun normalizePronunciationSpeech(text: String): String {
    val nfc = Normalizer.normalize(text, Normalizer.Form.NFC)
    return nfc.lowercase(Locale.ROOT)
        .replace(Regex("[\\p{P}\\p{Z}\\s，。！？、“”‘’：；, ! ? . ' \" : ; ( ) \\[ \\] \\- _ ~ …]"), "")
        .trim()
}

/**
 * Clean vector microphone icon rendered via Canvas.
 */
@Composable
private fun MicVectorIcon(
    tint: Color,
    modifier: Modifier = Modifier
) {
    Canvas(modifier = modifier) {
        val w = size.width
        val h = size.height

        val strokeWidth = (w * 0.085f).coerceAtLeast(1.5f)
        val stroke = Stroke(width = strokeWidth, cap = StrokeCap.Round, join = StrokeJoin.Round)

        // 1. Microphone capsule (head)
        val capW = w * 0.40f
        val capH = h * 0.52f
        val capLeft = (w - capW) / 2f
        val capTop = h * 0.08f
        val capRadius = CornerRadius(capW / 2f, capW / 2f)

        drawRoundRect(
            color = tint,
            topLeft = Offset(capLeft, capTop),
            size = Size(capW, capH),
            cornerRadius = capRadius
        )

        // 2. Cradle arc around capsule
        val arcW = w * 0.64f
        val arcH = h * 0.48f
        val arcLeft = (w - arcW) / 2f
        val arcTop = h * 0.22f

        drawArc(
            color = tint,
            startAngle = 0f,
            sweepAngle = 180f,
            useCenter = false,
            topLeft = Offset(arcLeft, arcTop),
            size = Size(arcW, arcH),
            style = stroke
        )

        // 3. Vertical stem
        val stemTop = arcTop + arcH
        val stemBottom = h * 0.86f
        drawLine(
            color = tint,
            start = Offset(w / 2f, stemTop),
            end = Offset(w / 2f, stemBottom),
            strokeWidth = strokeWidth,
            cap = StrokeCap.Round
        )

        // 4. Horizontal base
        val baseW = w * 0.42f
        drawLine(
            color = tint,
            start = Offset((w - baseW) / 2f, stemBottom),
            end = Offset((w + baseW) / 2f, stemBottom),
            strokeWidth = strokeWidth,
            cap = StrokeCap.Round
        )
    }
}

/**
 * Redesigned PronunciationScreen (shared with SpeakingScreen in SENTENCE mode).
 * IMPORTANT: No sample audio playback anywhere on this screen.
 */
@Composable
internal fun PronunciationScreen(
    target: String,
    meaning: String,
    pinyin: String,
    mode: PronunciationMode = PronunciationMode.WORD,
    state: LessonState = LessonState(),
    enabled: Boolean = true,
    result: (List<String>, Int) -> Unit = { _, _ -> },
    next: () -> Unit = {},
    back: () -> Unit = {},
    onSkip: () -> Unit = {},
    modifier: Modifier = Modifier,
    progress: Float = if (mode == PronunciationMode.WORD) 5f / 9f else 8f / 9f,
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
    val feedbackPlayer = rememberWritingFeedbackPlayer { audioVolume }

    var showSettingsSheet by rememberSaveable { mutableStateOf(false) }
    var attemptCount by rememberSaveable(target) { mutableIntStateOf(1) }
    var incorrectAttempts by rememberSaveable(target) { mutableIntStateOf(0) }

    var showSuccessBanner by remember { mutableStateOf(false) }
    var showErrorBanner by remember { mutableStateOf(false) }
    val isBannerShowing = showSuccessBanner || showErrorBanner

    var successTitle by remember { mutableStateOf(SUCCESS_TITLES.first()) }
    var recognizedCandidate by remember { mutableStateOf("") }
    var technicalErrorMessage by remember { mutableStateOf<String?>(null) }

    var isHintRevealed by rememberSaveable(target) { mutableStateOf(false) }
    val hintPopAnim = remember { Animatable(if (isHintRevealed) 1f else 0.5f) }

    var micState by remember { mutableStateOf(MicState.IDLE) }
    var rawRms by remember { mutableFloatStateOf(0f) }
    val smoothedRms by animateFloatAsState(
        targetValue = rawRms,
        animationSpec = tween(durationMillis = 80),
        label = "smoothedRms"
    )

    val micScaleAnim = remember { Animatable(1f) }
    var confettiTrigger by remember { mutableIntStateOf(0) }
    var micCenterOffset by remember { mutableStateOf(Offset.Zero) }

    var showPermissionDialog by remember { mutableStateOf(false) }
    var isPermissionDenied by remember { mutableStateOf(false) }

    var speechRecognizer by remember { mutableStateOf<SpeechRecognizer?>(null) }
    var captureStartTime by remember { mutableLongStateOf(0L) }
    var captureEndTime by remember { mutableLongStateOf(0L) }
    var heardSpeech by remember { mutableStateOf(false) }

    fun handleBack() {
        back()
    }

    BackHandler(enabled = !showSettingsSheet) {
        if (!isBannerShowing) {
            handleBack()
        }
    }

    LaunchedEffect(showSettingsSheet) {
        if (showSettingsSheet) {
            onPauseLesson()
        } else {
            onResumeLesson()
        }
    }

    fun handleRecognitionResult(candidates: List<String>, duration: Int) {
        if (candidates.isEmpty()) {
            technicalErrorMessage = "Mình chưa nghe thấy gì, thử lại nhé"
            return
        }

        val top3 = candidates.take(3)
        val normTarget = normalizePronunciationSpeech(target)
        val isCorrect = top3.any { normalizePronunciationSpeech(it) == normTarget }

        result(candidates, duration)

        if (isCorrect) {
            feedbackPlayer.playCorrect()
            confettiTrigger++
            successTitle = SUCCESS_TITLES.random()
            showErrorBanner = false
            showSuccessBanner = true
            coroutineScope.launch {
                micScaleAnim.snapTo(1f)
                micScaleAnim.animateTo(
                    targetValue = 1.08f,
                    animationSpec = tween(140, easing = FastOutSlowInEasing)
                )
                micScaleAnim.animateTo(
                    targetValue = 1f,
                    animationSpec = spring(dampingRatio = 0.5f, stiffness = Spring.StiffnessMedium)
                )
            }
        } else {
            feedbackPlayer.playIncorrect()
            incorrectAttempts++
            attemptCount++
            recognizedCandidate = candidates.firstOrNull().orEmpty()
            showSuccessBanner = false
            showErrorBanner = true
        }
    }

    fun startListening() {
        if (!SpeechRecognizer.isRecognitionAvailable(context)) {
            technicalErrorMessage = "Nhận diện giọng nói không khả dụng trên thiết bị này"
            return
        }
        technicalErrorMessage = null
        try {
            speechRecognizer?.cancel()
            speechRecognizer?.destroy()
            val recognizer = SpeechRecognizer.createSpeechRecognizer(context)
            speechRecognizer = recognizer
            captureStartTime = 0L
            captureEndTime = 0L
            heardSpeech = false
            rawRms = 0f

            recognizer.setRecognitionListener(object : RecognitionListener {
                override fun onReadyForSpeech(params: Bundle?) {
                    captureStartTime = SystemClock.elapsedRealtime()
                    micState = MicState.LISTENING
                }

                override fun onBeginningOfSpeech() {
                    heardSpeech = true
                }

                override fun onRmsChanged(rmsdB: Float) {
                    rawRms = ((rmsdB + 2f) / 12f).coerceIn(0f, 1f)
                }

                override fun onBufferReceived(buffer: ByteArray?) = Unit

                override fun onEndOfSpeech() {
                    captureEndTime = SystemClock.elapsedRealtime()
                    micState = MicState.PROCESSING
                    rawRms = 0f
                }

                override fun onError(error: Int) {
                    micState = MicState.IDLE
                    rawRms = 0f
                    when (error) {
                        SpeechRecognizer.ERROR_NO_MATCH,
                        SpeechRecognizer.ERROR_SPEECH_TIMEOUT -> {
                            technicalErrorMessage = "Mình chưa nghe thấy gì, thử lại nhé"
                        }
                        SpeechRecognizer.ERROR_NETWORK,
                        SpeechRecognizer.ERROR_NETWORK_TIMEOUT -> {
                            technicalErrorMessage = "Cần kết nối mạng để nhận diện giọng nói"
                        }
                        else -> {
                            technicalErrorMessage = "Mình chưa nghe thấy gì, thử lại nhé"
                        }
                    }
                }

                override fun onResults(results: Bundle?) {
                    micState = MicState.IDLE
                    rawRms = 0f
                    val candidates = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION).orEmpty()
                    val duration = if (!heardSpeech || captureStartTime == 0L) 1200 else
                        ((captureEndTime.takeIf { it > 0 } ?: SystemClock.elapsedRealtime()) - captureStartTime)
                            .coerceIn(1000, 300000).toInt()

                    handleRecognitionResult(candidates, duration)
                }

                override fun onPartialResults(partialResults: Bundle?) = Unit
                override fun onEvent(eventType: Int, params: Bundle?) = Unit
            })

            val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                putExtra(RecognizerIntent.EXTRA_LANGUAGE, "zh-CN")
                putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 5)
            }
            recognizer.startListening(intent)
            micState = MicState.LISTENING
        } catch (_: Exception) {
            micState = MicState.IDLE
            technicalErrorMessage = "Không thể kết nối dịch vụ nhận diện giọng nói"
        }
    }

    fun stopListeningEarly() {
        try {
            speechRecognizer?.stopListening()
            micState = MicState.PROCESSING
        } catch (_: Exception) {
            micState = MicState.IDLE
        }
    }

    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted) {
            isPermissionDenied = false
            startListening()
        } else {
            isPermissionDenied = true
        }
    }

    fun onMicTapped() {
        if (!enabled || isBannerShowing || isPermissionDenied) return
        when (micState) {
            MicState.IDLE -> {
                val hasPermission = ContextCompat.checkSelfPermission(
                    context,
                    Manifest.permission.RECORD_AUDIO
                ) == PackageManager.PERMISSION_GRANTED

                if (hasPermission) {
                    startListening()
                } else {
                    showPermissionDialog = true
                }
            }
            MicState.LISTENING -> {
                stopListeningEarly()
            }
            MicState.PROCESSING -> {
                // Locked
            }
        }
    }

    DisposableEffect(Unit) {
        onDispose {
            try {
                speechRecognizer?.cancel()
                speechRecognizer?.destroy()
                speechRecognizer = null
            } catch (_: Exception) {}
        }
    }

    // Auto dismiss technical error after 3.5s
    LaunchedEffect(technicalErrorMessage) {
        if (technicalErrorMessage != null) {
            delay(3500)
            technicalErrorMessage = null
        }
    }

    val mascotMessage = when {
        micState == MicState.LISTENING -> "Cứ đọc tự nhiên, mình đang nghe nè 👂"
        incorrectAttempts >= 2 -> "Khó nhỉ, thử thêm lần nữa, hoặc bỏ qua cũng được 💪"
        else -> "Nhấn mic và đọc to, rõ nhé! 🎤"
    }

    val isSentence = mode == PronunciationMode.SENTENCE || target.length > 4

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(Surface0)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(scrollState),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // 1. Common TopBar
            LessonTopBar(
                progress = progress,
                canGoBack = !isBannerShowing,
                onBack = { if (!isBannerShowing) handleBack() },
                onSettings = { showSettingsSheet = true }
            )

            status()

            // 2. Chip "LUYỆN PHÁT ÂM"
            Surface(
                shape = RoundedCornerShape(20.dp),
                color = PronunChipBg,
                border = BorderStroke(1.5.dp, PronunChipBorder),
                modifier = Modifier.padding(top = 14.dp)
            ) {
                Row(
                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 4.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(6.dp)
                ) {
                    MicVectorIcon(
                        tint = PronunChipText,
                        modifier = Modifier.size(13.dp)
                    )
                    Text(
                        text = "LUYỆN PHÁT ÂM",
                        color = PronunChipText,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Medium,
                        letterSpacing = 0.06.em
                    )
                }
            }

            Spacer(modifier = Modifier.height(14.dp))

            // 3. Thẻ chữ Hán
            if (!isSentence) {
                // Word Card: 140x140dp, bo 24dp, nền trắng, viền 2dp #d6e9de, bottom shadow 6dp #c8e0d2, lưới 田字格, chữ serif 82sp
                val charFontSize = when (target.length) {
                    0, 1 -> 82.sp
                    2 -> 54.sp
                    3 -> 42.sp
                    else -> 34.sp
                }

                Box(
                    modifier = Modifier.size(140.dp, 146.dp),
                    contentAlignment = Alignment.TopCenter
                ) {
                    // Bottom shadow 6dp #c8e0d2
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .offset(y = 6.dp)
                            .height(140.dp)
                            .background(LessonShadow, RoundedCornerShape(24.dp))
                    )
                    // Card Surface
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(140.dp)
                            .shadow(
                                elevation = 4.dp,
                                shape = RoundedCornerShape(24.dp),
                                spotColor = LessonShadow.copy(alpha = 0.5f),
                                ambientColor = LessonBorder
                            )
                            .background(Color.White, RoundedCornerShape(24.dp))
                            .border(2.dp, LessonBorder, RoundedCornerShape(24.dp)),
                        contentAlignment = Alignment.Center
                    ) {
                        TianZiGeGridCanvas(
                            inset = 8.dp,
                            cornerRadius = 16.dp,
                            color = TianZiGeGrid,
                            strokeWidth = 1.5.dp
                        )
                        Text(
                            text = target,
                            fontFamily = FontFamily.Serif,
                            fontSize = charFontSize,
                            color = TextPrimary,
                            textAlign = TextAlign.Center
                        )
                    }
                }
            } else {
                // Sentence Card: co chữ nhỏ lại, không có lưới 田字格
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 24.dp)
                        .heightIn(min = 120.dp),
                    contentAlignment = Alignment.TopCenter
                ) {
                    // Bottom shadow 6dp
                    Box(
                        modifier = Modifier
                            .matchParentSize()
                            .offset(y = 6.dp)
                            .background(LessonShadow, RoundedCornerShape(24.dp))
                    )
                    // Card Surface
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .wrapContentHeight()
                            .shadow(
                                elevation = 4.dp,
                                shape = RoundedCornerShape(24.dp),
                                spotColor = LessonShadow.copy(alpha = 0.5f)
                            )
                            .background(Color.White, RoundedCornerShape(24.dp))
                            .border(2.dp, LessonBorder, RoundedCornerShape(24.dp))
                            .padding(horizontal = 20.dp, vertical = 22.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = target,
                            fontFamily = FontFamily.Serif,
                            fontSize = if (target.length > 14) 22.sp else 28.sp,
                            lineHeight = if (target.length > 14) 30.sp else 36.sp,
                            color = TextPrimary,
                            textAlign = TextAlign.Center
                        )
                    }
                }
            }

            // 4. Nghĩa ngắn dưới thẻ: 16sp weight 500, căn giữa, margin top 12dp
            if (meaning.isNotBlank()) {
                Text(
                    text = meaning,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Medium,
                    color = TextPrimary,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.padding(top = 12.dp, start = 24.dp, end = 24.dp)
                )
            }

            Spacer(modifier = Modifier.height(14.dp))

            // 5. Hàng gợi ý (cao cố định 38dp để layout không nhảy)
            Box(
                modifier = Modifier
                    .height(38.dp)
                    .fillMaxWidth(),
                contentAlignment = Alignment.Center
            ) {
                if (!isHintRevealed) {
                    // Chip "💡 Gợi ý pinyin": nền trắng, viền nét đứt 1.5dp #b9dfc9, chữ Primary 12sp weight 500, bo 14dp, padding 5×14dp
                    Box(
                        modifier = Modifier
                            .clickable(
                                interactionSource = remember { MutableInteractionSource() },
                                indication = null,
                                enabled = !isBannerShowing && enabled
                            ) {
                                isHintRevealed = true
                                coroutineScope.launch {
                                    hintPopAnim.snapTo(0.5f)
                                    hintPopAnim.animateTo(
                                        targetValue = 1f,
                                        animationSpec = spring(
                                            dampingRatio = 0.6f,
                                            stiffness = Spring.StiffnessMedium
                                        )
                                    )
                                }
                            }
                            .background(Color.White, RoundedCornerShape(14.dp))
                            .padding(horizontal = 14.dp, vertical = 5.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Canvas(modifier = Modifier.matchParentSize()) {
                            val stroke = Stroke(
                                width = 1.5.dp.toPx(),
                                pathEffect = PathEffect.dashPathEffect(floatArrayOf(6f, 5f), 0f)
                            )
                            drawRoundRect(
                                color = PinyinBorder,
                                cornerRadius = CornerRadius(14.dp.toPx()),
                                style = stroke
                            )
                        }
                        Text(
                            text = "💡 Gợi ý pinyin",
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Medium,
                            color = Primary
                        )
                    }
                } else {
                    // Viên pinyin: nền #e8f5ee, viền 2dp #b9dfc9, bottom shadow 3dp #b9dfc9, chữ Primary 22sp weight 500 (spring pop)
                    Box(
                        modifier = Modifier
                            .graphicsLayer {
                                scaleX = hintPopAnim.value
                                scaleY = hintPopAnim.value
                            },
                        contentAlignment = Alignment.TopCenter
                    ) {
                        Box(
                            modifier = Modifier
                                .matchParentSize()
                                .offset(y = 3.dp)
                                .background(PinyinBorder, RoundedCornerShape(14.dp))
                        )
                        Surface(
                            shape = RoundedCornerShape(14.dp),
                            color = PinyinBg,
                            border = BorderStroke(2.dp, PinyinBorder)
                        ) {
                            Text(
                                text = pinyin.ifBlank { target },
                                fontSize = 22.sp,
                                fontWeight = FontWeight.Medium,
                                color = Primary,
                                modifier = Modifier.padding(horizontal = 16.dp, vertical = 2.dp)
                            )
                        }
                    }
                }
            }

            // 6. Khu vực mic (căn giữa, margin top 16dp)
            Spacer(modifier = Modifier.height(16.dp))

            val micInteractionSource = remember { MutableInteractionSource() }
            val isMicPressed by micInteractionSource.collectIsPressedAsState()
            val pressed = isMicPressed && micState != MicState.PROCESSING && !isBannerShowing && !isPermissionDenied
            val micOffsetY = if (pressed) 4.dp else 0.dp
            val micShadowY = if (pressed) 2.dp else 6.dp

            val micGradStart by animateColorAsState(
                targetValue = when (micState) {
                    MicState.IDLE -> if (showSuccessBanner) Color(0xFF4EE88D) else ProgressGradientStart
                    MicState.LISTENING -> MicListeningStart
                    MicState.PROCESSING -> MicProcessingStart
                },
                animationSpec = tween(300),
                label = "micGradStart"
            )
            val micGradEnd by animateColorAsState(
                targetValue = when (micState) {
                    MicState.IDLE -> if (showSuccessBanner) Color(0xFF1E9E56) else ProgressGradientEnd
                    MicState.LISTENING -> MicListeningEnd
                    MicState.PROCESSING -> MicProcessingEnd
                },
                animationSpec = tween(300),
                label = "micGradEnd"
            )
            val micShadowColor by animateColorAsState(
                targetValue = when (micState) {
                    MicState.IDLE -> PrimaryDark
                    MicState.LISTENING -> DangerColor
                    MicState.PROCESSING -> MicProcessingShadow
                },
                animationSpec = tween(300),
                label = "micShadowColor"
            )

            // 3 Concentric waves when LISTENING: 1.6s loop, 0.5s phase offset, scale 0.85 -> 1.7, alpha 0.8 -> 0
            val infiniteTransition = rememberInfiniteTransition(label = "waveTransition")
            val waveProgress by infiniteTransition.animateFloat(
                initialValue = 0f,
                targetValue = 1f,
                animationSpec = infiniteRepeatable(
                    animation = tween(durationMillis = 1600, easing = LinearEasing),
                    repeatMode = RepeatMode.Restart
                ),
                label = "waveProgress"
            )

            Box(
                modifier = Modifier
                    .size(176.dp)
                    .onGloballyPositioned { coordinates ->
                        val bounds = coordinates.boundsInRoot()
                        micCenterOffset = Offset(
                            bounds.left + bounds.width / 2f,
                            bounds.top + bounds.height / 2f
                        )
                    },
                contentAlignment = Alignment.Center
            ) {
                // Wave circles
                if (micState == MicState.LISTENING) {
                    listOf(0f, 0.3125f, 0.625f).forEach { phaseOffset ->
                        val p = (waveProgress + phaseOffset) % 1f
                        val scale = 0.85f + (1.7f - 0.85f) * p
                        val alpha = (0.8f * (1f - p)).coerceIn(0f, 0.8f) * 0.22f
                        Box(
                            modifier = Modifier
                                .size(104.dp)
                                .graphicsLayer {
                                    scaleX = scale
                                    scaleY = scale
                                    this.alpha = alpha
                                }
                                .background(Primary, CircleShape)
                        )
                    }
                }

                // Nút mic tròn 104dp (vùng chạm 120dp)
                Box(
                    modifier = Modifier
                        .size(120.dp)
                        .graphicsLayer {
                            scaleX = micScaleAnim.value
                            scaleY = micScaleAnim.value
                            alpha = if (isPermissionDenied) 0.4f else 1f
                        }
                        .clickable(
                            interactionSource = micInteractionSource,
                            indication = null,
                            enabled = enabled && micState != MicState.PROCESSING && !isBannerShowing && !isPermissionDenied,
                            onClick = { onMicTapped() }
                        ),
                    contentAlignment = Alignment.Center
                ) {
                    Box(
                        modifier = Modifier.size(104.dp),
                        contentAlignment = Alignment.TopCenter
                    ) {
                        // Bottom shadow
                        Box(
                            modifier = Modifier
                                .size(104.dp)
                                .offset(y = micShadowY)
                                .background(micShadowColor, CircleShape)
                        )
                        // Mic Button Surface
                        Box(
                            modifier = Modifier
                                .size(104.dp)
                                .offset(y = micOffsetY)
                                .shadow(
                                    elevation = 8.dp,
                                    shape = CircleShape,
                                    spotColor = micShadowColor.copy(alpha = 0.4f)
                                )
                                .background(
                                    brush = Brush.radialGradient(
                                        colors = listOf(micGradStart, micGradEnd)
                                    ),
                                    shape = CircleShape
                                ),
                            contentAlignment = Alignment.Center
                        ) {
                            if (micState == MicState.PROCESSING) {
                                CircularProgressIndicator(
                                    modifier = Modifier.size(36.dp),
                                    color = Color.White,
                                    strokeWidth = 3.5.dp
                                )
                            } else {
                                MicVectorIcon(
                                    tint = Color.White,
                                    modifier = Modifier.size(44.dp)
                                )
                            }
                        }
                    }
                }
            }

            // Thanh sóng âm: 5 cột bo tròn rộng 6dp, gap 5dp, cao 8-26dp dưới mic, margin top 12dp
            Row(
                modifier = Modifier
                    .padding(top = 12.dp)
                    .height(26.dp),
                horizontalArrangement = Arrangement.spacedBy(5.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                val barMultipliers = listOf(0.55f, 0.85f, 1.0f, 0.80f, 0.60f)
                val barColor = if (micState == MicState.LISTENING) MicListeningEnd else LessonShadow

                barMultipliers.forEach { multiplier ->
                    val factor = if (micState == MicState.LISTENING) (smoothedRms * multiplier).coerceIn(0f, 1f) else 0f
                    val barHeight = 8.dp + (26.dp - 8.dp) * factor
                    Box(
                        modifier = Modifier
                            .width(6.dp)
                            .height(barHeight)
                            .background(barColor, RoundedCornerShape(3.dp))
                    )
                }
            }

            // Dòng trạng thái 18sp weight 500 căn giữa dưới sóng âm
            Text(
                text = when (micState) {
                    MicState.IDLE -> "Nhấn để nói"
                    MicState.LISTENING -> "Đang nghe…"
                    MicState.PROCESSING -> "Đang xử lý…"
                },
                fontSize = 18.sp,
                fontWeight = FontWeight.Medium,
                color = TextPrimary,
                textAlign = TextAlign.Center,
                modifier = Modifier.padding(top = 8.dp)
            )

            // 7. Chip "Lần thử N": căn giữa, margin top 8dp, nền trắng, viền 1.5dp #d6e9de, bo 14dp, padding 3×12dp, chữ #5f7a6b 12sp weight 500
            Surface(
                shape = RoundedCornerShape(14.dp),
                color = Color.White,
                border = BorderStroke(1.5.dp, LessonBorder),
                modifier = Modifier.padding(top = 8.dp)
            ) {
                Text(
                    text = "Lần thử $attemptCount",
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Medium,
                    color = ToolbarTextColor,
                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 3.dp)
                )
            }

            // 8. Dòng chú thích: 10sp #8aa597 căn giữa, padding ngang 20dp
            Text(
                text = "Nhận diện giọng nói dùng dịch vụ hệ thống, có thể cần mạng.",
                fontSize = 10.sp,
                color = PronunNoteText,
                textAlign = TextAlign.Center,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 8.dp, start = 20.dp, end = 20.dp)
            )

            // Technical error light banner
            AnimatedVisibility(
                visible = technicalErrorMessage != null,
                enter = fadeIn() + slideInVertically(),
                exit = fadeOut()
            ) {
                Surface(
                    modifier = Modifier.padding(top = 8.dp, start = 24.dp, end = 24.dp),
                    shape = RoundedCornerShape(12.dp),
                    color = NewWordChipBg,
                    border = BorderStroke(1.dp, NewWordChipBorder)
                ) {
                    Text(
                        text = technicalErrorMessage.orEmpty(),
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Medium,
                        color = NewWordChipText,
                        textAlign = TextAlign.Center,
                        modifier = Modifier.padding(horizontal = 14.dp, vertical = 6.dp)
                    )
                }
            }

            // Permission denied card
            if (isPermissionDenied) {
                Surface(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(top = 12.dp, start = 24.dp, end = 24.dp),
                    shape = RoundedCornerShape(16.dp),
                    color = DangerBg,
                    border = BorderStroke(1.5.dp, DangerBorder)
                ) {
                    Row(
                        modifier = Modifier.padding(14.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = "Cần quyền micro để nhận diện phát âm",
                                fontSize = 13.sp,
                                fontWeight = FontWeight.Medium,
                                color = DangerColor
                            )
                            Text(
                                text = "Vui lòng mở Cài đặt ứng dụng để cấp quyền ghi âm.",
                                fontSize = 11.sp,
                                color = DangerColor.copy(alpha = 0.8f)
                            )
                        }
                        TextButton(
                            onClick = {
                                val intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
                                    data = Uri.fromParts("package", context.packageName, null)
                                }
                                context.startActivity(intent)
                            }
                        ) {
                            Text("Cài đặt", color = DangerColor, fontWeight = FontWeight.Bold, fontSize = 13.sp)
                        }
                    }
                }
            }

            // 9. Spacer, hàng mascot (TigerMascot nhỏ + bubble) ở đáy
            Spacer(modifier = Modifier.height(24.dp))
            Spacer(modifier = Modifier.weight(1f).defaultMinSize(minHeight = 16.dp))

            TigerMascot(
                message = mascotMessage,
                modifier = Modifier.padding(horizontal = 24.dp)
            )

            Spacer(modifier = Modifier.height(20.dp).navigationBarsPadding())
        }

        // Confetti Overlay
        ConfettiOverlay(
            trigger = confettiTrigger,
            originCenter = micCenterOffset
        )

        // ResultBanner: Correct
        AnimatedVisibility(
            visible = showSuccessBanner,
            enter = slideInVertically(initialOffsetY = { it }),
            exit = slideOutVertically(targetOffsetY = { it }),
            modifier = Modifier.align(Alignment.BottomCenter)
        ) {
            ResultBanner(
                isCorrect = true,
                title = successTitle,
                subtitle = "Nghe như người bản xứ luôn 👏",
                buttonText = "Tiếp tục",
                onButton = { next() },
                answerChip = null,
                onPlayAudio = null
            )
        }

        // ResultBanner: Incorrect
        AnimatedVisibility(
            visible = showErrorBanner,
            enter = slideInVertically(initialOffsetY = { it }),
            exit = slideOutVertically(targetOffsetY = { it }),
            modifier = Modifier.align(Alignment.BottomCenter)
        ) {
            ResultBanner(
                isCorrect = false,
                title = "Chưa đúng rồi",
                subtitle = if (recognizedCandidate.isNotBlank()) {
                    "Mình nghe được: “$recognizedCandidate”. Thử lại nhé!"
                } else {
                    "Mình chưa nghe rõ. Thử lại nhé!"
                },
                buttonText = "Thử lại",
                onButton = { showErrorBanner = false },
                answerChip = null,
                onPlayAudio = null,
                secondaryText = if (incorrectAttempts >= 3) "Bỏ qua câu này" else null,
                onSecondary = if (incorrectAttempts >= 3) {
                    {
                        showErrorBanner = false
                        onSkip()
                        next()
                    }
                } else null
            )
        }

        // Settings BottomSheet
        if (showSettingsSheet) {
            LessonSettingsSheet(
                onKnownWord = onKnownWord,
                onLeaveLesson = onLeaveLesson,
                onDismiss = { showSettingsSheet = false }
            )
        }

        // Permission Rationale Dialog
        if (showPermissionDialog) {
            AlertDialog(
                onDismissRequest = { showPermissionDialog = false },
                title = {
                    Text(
                        text = "Cho phép sử dụng micro?",
                        fontSize = 17.sp,
                        fontWeight = FontWeight.Bold,
                        color = TextPrimary
                    )
                },
                text = {
                    Text(
                        text = "Ứng dụng cần quyền ghi âm để nhận diện giọng nói và giúp bạn luyện phát âm chuẩn xác.",
                        fontSize = 14.sp,
                        color = TextSecondary
                    )
                },
                confirmButton = {
                    TextButton(
                        onClick = {
                            showPermissionDialog = false
                            permissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
                        }
                    ) {
                        Text("Đồng ý", color = PrimaryDark, fontWeight = FontWeight.Bold)
                    }
                },
                dismissButton = {
                    TextButton(onClick = { showPermissionDialog = false }) {
                        Text("Hủy", color = TextSecondary)
                    }
                },
                shape = RoundedCornerShape(20.dp),
                containerColor = Color.White
            )
        }
    }
}

/**
 * Backward-compatible overloads
 */
@Composable
internal fun PronunciationScreen(
    target: String,
    state: LessonState,
    enabled: Boolean,
    result: (List<String>, Int) -> Unit,
    next: () -> Unit,
    back: () -> Unit,
    onSkip: () -> Unit = {},
    status: @Composable () -> Unit = {}
) = PronunciationScreen(
    target = target,
    meaning = "",
    pinyin = "",
    mode = PronunciationMode.WORD,
    state = state,
    enabled = enabled,
    result = result,
    next = next,
    back = back,
    onSkip = onSkip,
    status = status
)

@Composable
internal fun PronunciationScreen(
    target: String,
    state: LessonState,
    enabled: Boolean,
    result: (String, Int) -> Unit,
    next: () -> Unit,
    back: () -> Unit,
    status: @Composable () -> Unit = {}
) = PronunciationScreen(
    target = target,
    state = state,
    enabled = enabled,
    result = { candidates, duration -> result(candidates.firstOrNull().orEmpty(), duration) },
    next = next,
    back = back,
    onSkip = {},
    status = status
)
