package com.example.chineselearningapp.feature.roadmap

import android.widget.Toast
import androidx.activity.compose.BackHandler
import androidx.compose.animation.Crossfade
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
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Rect
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.clearAndSetSemantics
import androidx.compose.ui.semantics.text
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.chineselearningapp.R
import com.example.chineselearningapp.core.datastore.AppPreferences
import com.example.chineselearningapp.core.designsystem.*
import com.example.chineselearningapp.domain.model.RoadmapWord
import kotlinx.coroutines.launch

/**
 * Shorten meanings to core definitions, stripping long parenthetical explanations.
 * e.g., "tốt; ổn; khỏe (khi nói về tình trạng sức khỏe)" -> "tốt; ổn; khỏe"
 */
internal fun shortenMeaning(meanings: List<String>): String {
    val regex = Regex("[\\(（\\[【].*?[\\)）\\]】]")
    return meanings
        .map { it.replace(regex, "").trim() }
        .filter { it.isNotBlank() }
        .joinToString("; ")
}

/**
 * Scene 1: WordIntroductionScreen
 * 4-step reveal: Hanzi -> Pinyin + Audio -> Meaning -> Sino-Vietnamese -> "Đã nhớ ✓"
 */
@Composable
fun WordIntroductionScreen(
    word: RoadmapWord,
    enabled: Boolean,
    acknowledge: () -> Unit,
    modifier: Modifier = Modifier,
    canGoBackToPreviousScene: Boolean = false,
    onBackToPreviousScene: () -> Unit = {},
    onKnownWord: () -> Unit = {},
    onLeaveLesson: () -> Unit = {},
    onPauseLesson: () -> Unit = {},
    onResumeLesson: () -> Unit = {},
    progress: Float = 0f / 9f,
    header: @Composable ColumnScope.() -> Unit = {},
) {
    val context = LocalContext.current
    val haptic = LocalHapticFeedback.current
    val appPreferences = remember(context) { AppPreferences(context.applicationContext) }
    val audioVolume by appPreferences.audioVolume.collectAsState(initial = 1.0f)

    var step by rememberSaveable(word.id, word.contentVersion) { mutableIntStateOf(0) }
    var showSettingsSheet by rememberSaveable { mutableStateOf(false) }

    val reading = word.sinoVietnamese?.takeIf { it.isNotBlank() }
    val maxStep = if (reading != null) 3 else 2
    val isFinalStep = step >= maxStep
    val speech = rememberWordSpeech(word.simplified, volume = audioVolume)

    // Back behavior:
    // Back decrements reveal step in current scene; at step 0:
    // if canGoBackToPreviousScene -> onBackToPreviousScene()
    // else canGoBack = false (TopBar back button dimmed to 0.3 opacity, system back shows toast)
    val canGoBack = step > 0 || canGoBackToPreviousScene

    fun handleBack() {
        if (step > 0) {
            step--
        } else if (canGoBackToPreviousScene) {
            onBackToPreviousScene()
        } else {
            Toast.makeText(context, "Dùng ⚙ để rời bài học", Toast.LENGTH_SHORT).show()
        }
    }

    BackHandler(enabled = !showSettingsSheet) {
        handleBack()
    }

    LaunchedEffect(showSettingsSheet) {
        if (showSettingsSheet) {
            speech.stop()
            onPauseLesson()
        }
    }

    // Audio autoplay & wave animation when pinyin reveals at step 1
    val waveAnim = remember { Animatable(0f) }
    var autoPlayedForWord by rememberSaveable(word.id) { mutableStateOf(false) }
    val coroutineScope = rememberCoroutineScope()

    LaunchedEffect(step, speech.ready) {
        if (step >= 1 && speech.ready && !autoPlayedForWord) {
            autoPlayedForWord = true
            speech.speak()
            waveAnim.snapTo(0f)
            waveAnim.animateTo(
                targetValue = 2f,
                animationSpec = tween(durationMillis = 1400, easing = LinearEasing)
            )
        }
    }

    // Hanzi character entrance animation: scale 0.4 -> 1 spring overshoot
    val hanziScaleAnim = remember { Animatable(0.4f) }
    LaunchedEffect(word.simplified) {
        hanziScaleAnim.snapTo(0.4f)
        hanziScaleAnim.animateTo(
            targetValue = 1f,
            animationSpec = spring(
                dampingRatio = 0.55f,
                stiffness = Spring.StiffnessLow
            )
        )
    }

    // Idle translateY animation for Hanzi card: 0 <-> -4dp, 3.5s cycle
    val infiniteTransition = rememberInfiniteTransition(label = "HanziCardIdle")
    val cardIdleY by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = -4f,
        animationSpec = infiniteRepeatable(
            animation = tween(1750, easing = EaseInOut),
            repeatMode = RepeatMode.Reverse
        ),
        label = "HanziCardTranslateY"
    )
    val currentCardIdleY = if (showSettingsSheet) 0f else cardIdleY

    // Sino-Vietnamese stamp animation: scale 1.6 -> 1 quickly (180ms) + haptic
    val stampScaleAnim = remember { Animatable(1f) }
    LaunchedEffect(step) {
        if (step == 3 && reading != null) {
            stampScaleAnim.snapTo(1.6f)
            try {
                haptic.performHapticFeedback(HapticFeedbackType.LongPress)
            } catch (_: Exception) {}
            stampScaleAnim.animateTo(
                targetValue = 1f,
                animationSpec = tween(durationMillis = 180, easing = FastOutLinearInEasing)
            )
        }
    }

    // Background gradient: #e3f4ea -> #f4faf6 (55%) -> #ffffff
    val screenBackgroundBrush = Brush.verticalGradient(
        colorStops = arrayOf(
            0.0f to ScreenGradientTop,
            0.55f to ScreenGradientMid,
            1.0f to Color.White
        )
    )

    Box(modifier = modifier.fillMaxSize()) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .background(screenBackgroundBrush)
                .statusBarsPadding(),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // 1. LessonTopBar
            LessonTopBar(
                progress = progress,
                canGoBack = canGoBack,
                onBack = ::handleBack,
                onSettings = { showSettingsSheet = true }
            )

        // Optional header slot for backward compatibility
        Column(
            modifier = Modifier
                .widthIn(max = 680.dp)
                .fillMaxWidth()
                .padding(horizontal = 16.dp),
            content = header
        )

        // Middle scrollable viewport
        BoxWithConstraints(
            modifier = Modifier
                .weight(1f)
                .widthIn(max = 680.dp)
                .fillMaxWidth()
        ) {
            val minHeight = maxHeight
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .verticalScroll(rememberScrollState())
                    .heightIn(min = minHeight)
                    .padding(horizontal = 24.dp, vertical = 12.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Top
            ) {
                // 2. Chip "✦ TỪ MỚI"
                Box(
                    modifier = Modifier
                        .padding(top = 8.dp)
                        .background(NewWordChipBg, RoundedCornerShape(20.dp))
                        .border(1.5.dp, NewWordChipBorder, RoundedCornerShape(20.dp))
                        .padding(horizontal = 12.dp, vertical = 4.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = "✦ TỪ MỚI",
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Medium,
                        letterSpacing = 0.06.sp,
                        color = NewWordChipText
                    )
                }

                Spacer(Modifier.height(16.dp))

                // 3. Thẻ chữ Hán (luôn hiện từ đầu)
                Box(
                    modifier = Modifier
                        .size(width = 210.dp, height = 217.dp)
                        .graphicsLayer { translationY = currentCardIdleY.dp.toPx() },
                    contentAlignment = Alignment.TopCenter
                ) {
                    // Bottom shadow 7dp #c8e0d2
                    Box(
                        modifier = Modifier
                            .offset(y = 7.dp)
                            .size(210.dp)
                            .background(LessonShadow, RoundedCornerShape(28.dp))
                    )
                    // Card surface
                    Box(
                        modifier = Modifier
                            .size(210.dp)
                            .background(Color.White, RoundedCornerShape(28.dp))
                            .border(2.dp, LessonBorder, RoundedCornerShape(28.dp)),
                        contentAlignment = Alignment.Center
                    ) {
                        // Tian Zi Ge (田字格) grid Canvas
                        TianZiGeGridCanvas(
                            modifier = Modifier.fillMaxSize(),
                            inset = 14.dp,
                            cornerRadius = 14.dp
                        )

                        // Hanzi character 108sp serif
                        Text(
                            text = word.simplified,
                            fontSize = 108.sp,
                            lineHeight = 116.sp,
                            fontFamily = FontFamily.Serif,
                            color = TextPrimary,
                            textAlign = TextAlign.Center,
                            modifier = Modifier.graphicsLayer {
                                scaleX = hanziScaleAnim.value
                                scaleY = hanziScaleAnim.value
                            }
                        )
                    }
                }

                // 4. Hàng pinyin (reveal bước 1)
                RevealContainer(
                    visible = step >= 1,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(top = 18.dp)
                ) {
                    val isWaving = waveAnim.value > 0f && waveAnim.value < 2f
                    val waveCycle = waveAnim.value % 1f
                    val currentWaveScale = if (isWaving) 0.9f + 0.6f * waveCycle else 1f
                    val currentWaveAlpha = if (isWaving) (1f - waveCycle).coerceIn(0f, 1f) else 0f

                    Row(
                        modifier = Modifier.padding(horizontal = 8.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(14.dp)
                    ) {
                        // Viên thuốc pinyin: nền #e8f5ee, viền 2dp #b9dfc9, bottom shadow 4dp #b9dfc9, bo 16dp, padding 4×18dp, chữ 30sp weight 500 màu Primary
                        Box(
                            modifier = Modifier.height(IntrinsicSize.Min),
                            contentAlignment = Alignment.TopCenter
                        ) {
                            Box(
                                modifier = Modifier
                                    .matchParentSize()
                                    .offset(y = 4.dp)
                                    .background(PinyinBorder, RoundedCornerShape(16.dp))
                            )
                            Box(
                                modifier = Modifier
                                    .background(PinyinBg, RoundedCornerShape(16.dp))
                                    .border(2.dp, PinyinBorder, RoundedCornerShape(16.dp))
                                    .padding(horizontal = 18.dp, vertical = 4.dp),
                                contentAlignment = Alignment.Center
                            ) {
                                Text(
                                    text = word.pinyin,
                                    fontSize = 30.sp,
                                    fontWeight = FontWeight.Medium,
                                    color = Primary,
                                    textAlign = TextAlign.Center
                                )
                            }
                        }

                        // Nút loa tròn 48dp, nền Primary, bottom shadow 4dp #0f5533, icon loa trắng
                        val speakerInteraction = remember { MutableInteractionSource() }
                        val isSpeakerPressed by speakerInteraction.collectIsPressedAsState()
                        val speakerOffset = if (isSpeakerPressed && speech.ready) 3.dp else 0.dp

                        Box(
                            modifier = Modifier.size(width = 48.dp, height = 52.dp),
                            contentAlignment = Alignment.TopCenter
                        ) {
                            // Lan tỏa sóng
                            if (currentWaveAlpha > 0.01f) {
                                Box(
                                    modifier = Modifier
                                        .size(48.dp)
                                        .graphicsLayer {
                                            scaleX = currentWaveScale
                                            scaleY = currentWaveScale
                                            alpha = currentWaveAlpha
                                        }
                                        .border(2.dp, Primary, CircleShape)
                                )
                            }

                            // Bottom shadow 4dp #0f5533
                            Box(
                                modifier = Modifier
                                    .offset(y = 4.dp)
                                    .size(48.dp)
                                    .background(PrimaryDark, CircleShape)
                            )

                            // Speaker surface
                            Box(
                                modifier = Modifier
                                    .offset(y = speakerOffset)
                                    .size(48.dp)
                                    .background(Primary, CircleShape)
                                    .clickable(
                                        interactionSource = speakerInteraction,
                                        indication = null,
                                        enabled = speech.ready,
                                        onClick = {
                                            speech.speak()
                                            coroutineScope.launch {
                                                waveAnim.snapTo(0f)
                                                waveAnim.animateTo(
                                                    targetValue = 1f,
                                                    animationSpec = tween(durationMillis = 700, easing = LinearEasing)
                                                )
                                            }
                                        }
                                    ),
                                contentAlignment = Alignment.Center
                            ) {
                                Icon(
                                    painter = painterResource(R.drawable.ic_volume),
                                    contentDescription = stringResource(R.string.word_reveal_listen),
                                    tint = Color.White,
                                    modifier = Modifier.size(24.dp)
                                )
                            }
                        }
                    }
                }

                // 5. Thẻ nghĩa (reveal bước 2)
                RevealContainer(
                    visible = step >= 2,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(top = 14.dp, start = 8.dp, end = 8.dp)
                ) {
                    val shortened = remember(word.meanings) { shortenMeaning(word.meanings) }
                    Box(
                        modifier = Modifier.fillMaxWidth(),
                        contentAlignment = Alignment.TopCenter
                    ) {
                        // Bottom shadow 4dp #c8e0d2
                        Box(
                            modifier = Modifier
                                .matchParentSize()
                                .offset(y = 4.dp)
                                .background(LessonShadow, RoundedCornerShape(18.dp))
                        )
                        // Meaning card surface
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .background(Color.White, RoundedCornerShape(18.dp))
                                .border(2.dp, LessonBorder, RoundedCornerShape(18.dp))
                                .padding(horizontal = 14.dp, vertical = 10.dp),
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.spacedBy(4.dp)
                        ) {
                            Text(
                                text = "NGHĨA",
                                fontSize = 10.sp,
                                letterSpacing = 0.08.sp,
                                color = MeaningLabel,
                                fontWeight = FontWeight.SemiBold
                            )
                            Text(
                                text = shortened,
                                fontSize = 17.sp,
                                fontWeight = FontWeight.Medium,
                                color = TextPrimary,
                                textAlign = TextAlign.Center
                            )
                        }
                    }
                }

                // 6. Con dấu Hán Việt (reveal bước 3, chỉ hiện nếu có data)
                if (reading != null) {
                    RevealContainer(
                        visible = step >= 3,
                        modifier = Modifier
                            .padding(top = 12.dp)
                            .graphicsLayer {
                                rotationZ = -2f
                                scaleX = stampScaleAnim.value
                                scaleY = stampScaleAnim.value
                            }
                    ) {
                        Box(
                            modifier = Modifier
                                .clearAndSetSemantics {
                                    text = AnnotatedString("Hán Việt: $reading")
                                },
                            contentAlignment = Alignment.TopCenter
                        ) {
                            // Bottom shadow 3dp #e8a5a5
                            Box(
                                modifier = Modifier
                                    .matchParentSize()
                                    .offset(y = 3.dp)
                                    .background(SealBorder, RoundedCornerShape(12.dp))
                            )
                            // Seal surface
                            Row(
                                modifier = Modifier
                                    .background(DangerBg, RoundedCornerShape(12.dp))
                                    .border(2.dp, SealBorder, RoundedCornerShape(12.dp))
                                    .padding(horizontal = 12.dp, vertical = 5.dp),
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(6.dp)
                            ) {
                                Text(
                                    text = "HÁN VIỆT",
                                    fontSize = 10.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = DangerColor
                                )
                                Text(
                                    text = reading,
                                    fontSize = 16.sp,
                                    fontWeight = FontWeight.Medium,
                                    color = DangerColor
                                )
                            }
                        }
                    }
                }

                if (step >= 1 && speech.unavailable) {
                    Spacer(Modifier.height(8.dp))
                    Text(
                        text = stringResource(R.string.word_reveal_tts_unavailable),
                        style = FontLabel,
                        textAlign = TextAlign.Center
                    )
                }

                // 7. Spacer đẩy phần dưới xuống đáy
                Spacer(Modifier.height(24.dp))
            }
        }

        // 8. Hàng mascot + 9. Primary Button ở đáy màn hình
        Column(
            modifier = Modifier
                .widthIn(max = 680.dp)
                .fillMaxWidth()
                .navigationBarsPadding()
                .padding(start = 20.dp, end = 20.dp, bottom = 16.dp, top = 8.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {
            // Mascot messages
            val mascotMessage = when {
                step == 0 -> "Nhìn kỹ chữ này đi đã, rồi mới nhấn Tiếp tục nha 👀"
                step == 1 -> "Bấm vào cái loa để nghe phát âm nhé 🔊"
                step == 2 -> "Nghĩa của từ nè, nhẩm trong đầu thử xem 🧠"
                else -> "Hán Việt giúp nhớ nhanh hơn đó, nhớ sơ sơ là được 💪"
            }

            // Hàng mascot: TigerMascot nhỏ (46×56dp) + bubble chat (nền trắng, viền 1.5dp #d6e9de, bo 14 14 14 4dp, chữ 12sp)
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                TigerCanvas(width = 46.dp, height = 56.dp)
                Surface(
                    modifier = Modifier.weight(1f),
                    shape = RoundedCornerShape(
                        topStart = 14.dp,
                        topEnd = 14.dp,
                        bottomEnd = 14.dp,
                        bottomStart = 4.dp
                    ),
                    color = Color.White,
                    border = BorderStroke(1.5.dp, LessonBorder)
                ) {
                    Crossfade(
                        targetState = mascotMessage,
                        animationSpec = tween(200),
                        label = "tigerMessageAnim"
                    ) { text ->
                        Text(
                            text = text,
                            modifier = Modifier.padding(horizontal = 14.dp, vertical = 10.dp),
                            fontSize = 12.sp,
                            lineHeight = 17.sp,
                            color = TextPrimary
                        )
                    }
                }
            }

            // 9. PrimaryButton: h=52dp, bo 16dp, bottom shadow 5dp #0f5533, lún 4dp khi nhấn
            LessonPrimary3DButton(
                text = if (isFinalStep) "Đã nhớ ✓" else "Tiếp tục",
                onClick = {
                    if (isFinalStep) {
                        acknowledge()
                    } else {
                        step = if (step == 2 && reading == null) 2 else step + 1
                    }
                },
                enabled = enabled
            )
        }
    }

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
