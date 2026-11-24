package com.example.chineselearningapp.feature.roadmap

import androidx.activity.compose.BackHandler
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.Animatable
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.keyframes
import androidx.compose.animation.core.spring
import androidx.compose.animation.core.tween
import androidx.compose.animation.slideInVertically
import androidx.compose.animation.slideOutVertically
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.StrokeJoin
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.layout.boundsInRoot
import androidx.compose.ui.layout.onGloballyPositioned
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.chineselearningapp.R
import com.example.chineselearningapp.core.datastore.AppPreferences
import com.example.chineselearningapp.core.designsystem.*
import kotlin.random.Random

enum class WritingMode { Guided, Independent }

private val CORRECT_TITLES = listOf("Tuyệt vời!", "Chuẩn rồi!", "Quá đỉnh!", "Giỏi lắm!")
private val CORRECT_SUBTITLES = listOf("Nét bút chuẩn lắm 👏", "Viết đẹp đó!")
private val INCORRECT_TITLES = listOf("Chưa đúng rồi", "Suýt đúng rồi", "Thử lại nhé")
private val INCORRECT_SUBTITLES = listOf("Chú ý thứ tự nét nhé!", "Xem lại chữ mẫu rồi viết lại nào")

/**
 * Redesigned WritingScreen (3A Guided + 3B Independent).
 */
@Composable
internal fun WritingScreen(
    state: RoadmapState,
    model: RoadmapViewModel,
    onSkip: () -> Unit,
    writingMode: WritingMode? = null,
    onBack: (() -> Unit)? = null,
    onContinue: (() -> Unit)? = null,
    onCheck: (() -> Unit)? = null,
    allowMissingGuide: Boolean = false
) {
    val context = LocalContext.current
    val appPreferences = remember(context) { AppPreferences(context.applicationContext) }
    val audioVolume by appPreferences.audioVolume.collectAsState(initial = 1.0f)
    val feedbackPlayer = rememberWritingFeedbackPlayer { audioVolume }

    val lesson = checkNotNull(state.lesson)
    val word = lesson.words.getOrNull(state.wordIndex) ?: return
    val activity = state.activity
    val mode = writingMode ?: if (activity?.kind == "STROKE_ORDER") WritingMode.Guided else WritingMode.Independent
    val guided = mode == WritingMode.Guided

    val strokeData = remember(word.simplified) {
        StrokeDataLoader.load(context, word.simplified)
    }

    var showSettingsSheet by rememberSaveable { mutableStateOf(false) }
    var replayCount by remember(word.simplified) { mutableIntStateOf(0) }
    var failCount by rememberSaveable(word.simplified, mode) { mutableIntStateOf(0) }

    // Banner texts (picked randomly without consecutive duplicates)
    var lastCorrectIdx by remember { mutableIntStateOf(-1) }
    var lastIncorrectIdx by remember { mutableIntStateOf(-1) }
    var currentTitle by remember { mutableStateOf("") }
    var currentSubtitle by remember { mutableStateOf("") }

    // Feedback effect state
    var showSuccessBanner by remember { mutableStateOf(false) }
    var showErrorBanner by remember { mutableStateOf(false) }

    // Animation drivers
    val cardScale = remember { androidx.compose.animation.core.Animatable(1f) }
    val cardShakeX = remember { androidx.compose.animation.core.Animatable(0f) }
    val strokeColorAnim = remember { androidx.compose.animation.Animatable(Color(0xFF1A1A18)) }
    var confettiTrigger by remember { mutableIntStateOf(0) }
    var canvasCenter by remember { mutableStateOf(Offset.Zero) }

    val isBannerShowing = showSuccessBanner || showErrorBanner
    val enabled = !state.busy && !state.deliveryPending && !state.recognizing && !isBannerShowing

    // Trigger effects on recognition result
    LaunchedEffect(state.writingResult, state.writingFeedbackId) {
        if (state.writingResult == true) {
            showErrorBanner = false
            showSuccessBanner = true
            // Pick random title & subtitle
            var cIdx = Random.nextInt(CORRECT_TITLES.size)
            if (cIdx == lastCorrectIdx) cIdx = (cIdx + 1) % CORRECT_TITLES.size
            lastCorrectIdx = cIdx
            currentTitle = CORRECT_TITLES[cIdx]
            currentSubtitle = CORRECT_SUBTITLES[Random.nextInt(CORRECT_SUBTITLES.size)]

            feedbackPlayer.playCorrect()
            confettiTrigger++

            // Animate stroke color to green #1a9a58 in 250ms
            strokeColorAnim.animateTo(
                SuccessStrokeColor,
                animationSpec = tween(durationMillis = 250, easing = LinearEasing)
            )

            // Canvas card pump: 1 -> 1.025 -> 1 in 700ms
            cardScale.animateTo(
                1.025f,
                animationSpec = tween(durationMillis = 350, easing = FastOutSlowInEasing)
            )
            cardScale.animateTo(
                1f,
                animationSpec = tween(durationMillis = 350, easing = FastOutSlowInEasing)
            )
        } else if (state.writingResult == false) {
            failCount++
            showSuccessBanner = false
            showErrorBanner = true

            var iIdx = Random.nextInt(INCORRECT_TITLES.size)
            if (iIdx == lastIncorrectIdx) iIdx = (iIdx + 1) % INCORRECT_TITLES.size
            lastIncorrectIdx = iIdx
            currentTitle = INCORRECT_TITLES[iIdx]
            currentSubtitle = INCORRECT_SUBTITLES[Random.nextInt(INCORRECT_SUBTITLES.size)]

            feedbackPlayer.playIncorrect()

            // Animate stroke color to red #e5484d
            strokeColorAnim.animateTo(
                ErrorColor,
                animationSpec = tween(durationMillis = 250, easing = LinearEasing)
            )

            // Replay demo card for 3A
            if (guided) {
                replayCount++
            }

            // Shake horizontally ±10dp, decaying over 500ms
            cardShakeX.animateTo(
                0f,
                animationSpec = keyframes {
                    durationMillis = 500
                    0f at 0
                    -10f at 50
                    10f at 120
                    -8f at 200
                    8f at 280
                    -4f at 360
                    4f at 430
                    0f at 500
                }
            )
        }
    }

    // Reset stroke color when ink is cleared
    LaunchedEffect(state.strokes.isEmpty()) {
        if (state.strokes.isEmpty()) {
            strokeColorAnim.snapTo(Color(0xFF1A1A18))
        }
    }

    fun handleBack() {
        if (state.busy || state.deliveryPending || state.drawing) return
        if (onBack != null) { onBack(); return }
        val previous = lesson.activities.indexOfFirst { it.kind == if (guided) "COMPONENTS" else "STROKE_ORDER" }
        if (previous >= 0) model.chooseActivity(previous) else model.leave()
    }

    BackHandler { handleBack() }

    Box(
        Modifier
            .fillMaxSize()
            .background(Surface0)
    ) {
        Column(
            Modifier
                .widthIn(max = 680.dp)
                .fillMaxWidth()
                .align(Alignment.TopCenter)
                .fillMaxHeight()
                .navigationBarsPadding(),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f, fill = false),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                // 1. LessonTopBar: scene 3A = 2/9, 3B = 3/9
                val sceneProgress = if (guided) 2f / 9f else 3f / 9f
                LessonTopBar(
                    progress = sceneProgress,
                    canGoBack = true,
                    onBack = ::handleBack,
                    onSettings = { showSettingsSheet = true }
                )

                RoadmapError(state.error, if (state.error == R.string.roadmap_recognition_error) onCheck ?: model::checkWriting else model::retry)
                if (state.busy) LinearProgressIndicator(Modifier.fillMaxWidth())

                // Main body column
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 20.dp),
                    verticalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    // 2. [3A ONLY] Demo Card (150dp height, 22dp corner, #d6e9de border 2dp, #c8e0d2 bottom shadow 5dp)
                    if (guided) {
                        Column(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .height(155.dp),
                                contentAlignment = Alignment.TopCenter
                            ) {
                                // Bottom shadow
                                Box(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .offset(y = 5.dp)
                                        .height(150.dp)
                                        .background(LessonShadow, RoundedCornerShape(22.dp))
                                )
                                // White card
                                Box(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .height(150.dp)
                                        .background(Color.White, RoundedCornerShape(22.dp))
                                        .border(2.dp, LessonBorder, RoundedCornerShape(22.dp))
                                        .padding(10.dp),
                                    contentAlignment = Alignment.Center
                                ) {
                                    // TianZiGe grid
                                    TianZiGeGrid(
                                        modifier = Modifier.fillMaxSize(),
                                        color = DemoGridColor
                                    )

                                    if (strokeData != null) {
                                        StrokeOrderPlayer(
                                            strokeData = strokeData,
                                            replayTrigger = replayCount,
                                            size = 128.dp,
                                            modifier = Modifier.testTag("writing_stroke_order")
                                        )
                                    } else if (lesson.strokeOrder.available) {
                                        // Fallback to original GIF at 1x
                                        ReviewedAsset(
                                            lesson.strokeOrder,
                                            model::media,
                                            animationControls = true,
                                            showPlaybackControls = false,
                                            replayRequest = replayCount,
                                            imageModifier = Modifier.size(128.dp)
                                        )
                                    } else {
                                        Text(
                                            text = stringResource(R.string.roadmap_unavailable),
                                            color = TextMuted,
                                            fontSize = 14.sp
                                        )
                                    }

                                    // Round Play Button: 34dp, bottom-right, Primary bg, bottom shadow 3dp #0f5533
                                    Box(
                                        modifier = Modifier
                                            .align(Alignment.BottomEnd)
                                            .padding(4.dp)
                                            .size(width = 34.dp, height = 37.dp),
                                        contentAlignment = Alignment.TopCenter
                                    ) {
                                        Box(
                                            modifier = Modifier
                                                .size(34.dp)
                                                .offset(y = 3.dp)
                                                .background(PrimaryDark, CircleShape)
                                        )
                                        Box(
                                            modifier = Modifier
                                                .size(34.dp)
                                                .background(Primary, CircleShape)
                                                .clickable(enabled = enabled) { replayCount++ },
                                            contentAlignment = Alignment.Center
                                        ) {
                                            Text(
                                                text = "▶",
                                                color = Color.White,
                                                fontSize = 15.sp,
                                                modifier = Modifier.offset(x = 1.dp)
                                            )
                                        }
                                    }
                                }
                            }

                            // Caption below demo card
                            val strokeText = if (strokeData != null) {
                                "${strokeData.strokeCount} nét · Nhấn ▶ để xem lại"
                            } else {
                                "Nhấn ▶ để xem lại"
                            }
                            Text(
                                text = strokeText,
                                fontSize = 12.sp,
                                color = SubtitleCaptionColor,
                                textAlign = TextAlign.Center,
                                modifier = Modifier.padding(top = 8.dp)
                            )
                        }
                    } else {
                        // 3. [3B ONLY] Word info row: pinyin pill + short meaning
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 4.dp),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(10.dp)
                        ) {
                            Surface(
                                shape = RoundedCornerShape(12.dp),
                                color = PinyinBg,
                                border = BorderStroke(1.5.dp, PinyinBorder)
                            ) {
                                Text(
                                    text = word.pinyin,
                                    color = PrimaryDark,
                                    fontSize = 16.sp,
                                    fontWeight = FontWeight.Medium,
                                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
                                )
                            }
                            Text(
                                text = shortenMeaning(word.meanings),
                                color = TextSecondary,
                                fontSize = 14.sp,
                                modifier = Modifier.weight(1f)
                            )
                        }
                    }

                    // 4. Canvas Card (weight 1, min height 180dp)
                    val cardBorderColor = when {
                        showSuccessBanner -> CorrectGlowColor
                        showErrorBanner -> ErrorColor
                        else -> LessonBorder
                    }
                    val cardShadowColor = when {
                        showSuccessBanner -> CorrectGlowColor
                        showErrorBanner -> DangerCardShadow
                        else -> LessonShadow
                    }
                    val cardGlowAlpha = when {
                        showSuccessBanner -> 0.25f
                        showErrorBanner -> 0.18f
                        else -> 0f
                    }
                    val cardGlowColor = when {
                        showSuccessBanner -> CorrectGlowColor
                        showErrorBanner -> ErrorColor
                        else -> Color.Transparent
                    }

                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .heightIn(min = 180.dp, max = 290.dp)
                            .graphicsLayer {
                                scaleX = cardScale.value
                                scaleY = cardScale.value
                                translationX = cardShakeX.value
                            }
                            .onGloballyPositioned { coordinates ->
                                val bounds = coordinates.boundsInRoot()
                                canvasCenter = Offset(bounds.left + bounds.width / 2f, bounds.top + bounds.height / 2f)
                            },
                        contentAlignment = Alignment.TopCenter
                    ) {
                        // Outer glow 6dp
                        if (cardGlowAlpha > 0f) {
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .fillMaxHeight()
                                    .padding(vertical = 2.dp)
                                    .border(6.dp, cardGlowColor.copy(alpha = cardGlowAlpha), RoundedCornerShape(26.dp))
                            )
                        }
                        // Bottom shadow
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .fillMaxHeight()
                                .offset(y = 5.dp)
                                .background(cardShadowColor, RoundedCornerShape(22.dp))
                        )
                        // Canvas card body
                        BoxWithConstraints(
                            modifier = Modifier
                                .fillMaxWidth()
                                .fillMaxHeight()
                                .background(Color.White, RoundedCornerShape(22.dp))
                                .border(2.dp, cardBorderColor, RoundedCornerShape(22.dp))
                                .clip(RoundedCornerShape(22.dp)),
                            contentAlignment = Alignment.Center
                        ) {
                            // TianZiGe grid
                            TianZiGeGrid(
                                modifier = Modifier.fillMaxSize().padding(10.dp),
                                color = DemoGridColor
                            )

                            // Ghost hint: 3A has 0.08 opacity; 3B has 0.12 opacity if failCount >= 3
                            val ghostAlpha = when {
                                guided -> 0.08f
                                failCount >= 3 -> 0.12f
                                else -> 0f
                            }
                            if (strokeData != null && ghostAlpha > 0f) {
                                StrokeGuideGhost(
                                    strokeData = strokeData,
                                    alpha = ghostAlpha,
                                    modifier = Modifier.fillMaxSize().padding(18.dp)
                                )
                            } else if (ghostAlpha > 0f && word.simplified.isNotEmpty()) {
                                val minDimension = if (maxWidth < maxHeight) maxWidth else maxHeight
                                val density = LocalDensity.current
                                val fontSize = with(density) { (minDimension * 0.75f).toSp() }
                                Text(
                                    text = word.simplified,
                                    fontSize = fontSize,
                                    color = TextPrimary.copy(alpha = ghostAlpha),
                                    textAlign = TextAlign.Center
                                )
                            }

                            // Drawing canvas
                            DrawingCanvas(
                                strokes = state.strokes,
                                enabled = enabled && !isBannerShowing,
                                onBeginStroke = model::beginStroke,
                                onCompleteStroke = model::endStroke,
                                guideCharacter = null,
                                showGrid = false, // already rendered TianZiGe grid
                                strokeColor = strokeColorAnim.value,
                                strokeWidthDp = 7f,
                                backgroundColor = Color.Transparent,
                                drawBorder = false,
                                modifier = Modifier.fillMaxSize()
                            )
                        }
                    }

                    // 5. Toolbar: 2 pill buttons (Undo, Clear All), height 36dp, rounded 12dp, bg White, border 1.5dp #d6e9de
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(top = 4.dp),
                        horizontalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        WritingToolbarButton(
                            text = "Hoàn tác",
                            icon = { UndoVectorIcon(tint = ToolbarTextColor) },
                            onClick = model::undo,
                            enabled = enabled && !state.drawing && state.strokes.isNotEmpty(),
                            modifier = Modifier.weight(1f)
                        )
                        WritingToolbarButton(
                            text = "Xóa hết",
                            icon = { TrashVectorIcon(tint = ToolbarTextColor) },
                            onClick = model::clearInk,
                            enabled = enabled && !state.drawing && state.strokes.isNotEmpty(),
                            modifier = Modifier.weight(1f)
                        )
                    }
                }
            }

            // Bottom Area: Mascot bar + Check button (or ResultBanner)
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 8.dp)
            ) {
                // Default footer: Mascot + PrimaryButton 3D
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 20.dp, vertical = 10.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    val mascotMessage = if (guided) {
                        "Xem kỹ thứ tự nét rồi viết theo nhé, đừng vội! ✍️"
                    } else {
                        "Giờ tự viết thử xem nào, không cần hoàn hảo đâu 😄"
                    }
                    TigerMascot(message = mascotMessage)

                    val canCheck = enabled && !state.drawing && state.strokes.isNotEmpty()
                    LessonPrimary3DButton(
                        text = "Kiểm tra",
                        onClick = {
                            (onCheck ?: model::checkWriting).invoke()
                        },
                        enabled = canCheck,
                        modifier = Modifier.testTag("writing_check_button")
                    )
                }

                // Banner slide-up overlay
                androidx.compose.animation.AnimatedVisibility(
                    visible = isBannerShowing,
                    enter = slideInVertically(
                        initialOffsetY = { it },
                        animationSpec = spring(
                            dampingRatio = 0.65f,
                            stiffness = Spring.StiffnessMediumLow
                        )
                    ),
                    exit = slideOutVertically(targetOffsetY = { it }),
                    modifier = Modifier.align(Alignment.BottomCenter)
                ) {
                    if (showSuccessBanner) {
                        ResultBanner(
                            isCorrect = true,
                            title = currentTitle,
                            subtitle = currentSubtitle,
                            buttonText = "Tiếp tục",
                            onButton = {
                                showSuccessBanner = false
                                model.clearWritingResult()
                                if (onContinue != null) {
                                    onContinue()
                                } else if (guided) {
                                    if (activity != null && (state.accepted[activity.id]?.size ?: 0) < activity.repetitions) model.acknowledge()
                                    else lesson.activities.indexOfFirst { it.kind == "HANDWRITING" }.takeIf { it >= 0 }?.let(model::chooseActivity)
                                } else {
                                    lesson.activities.indexOfFirst { it.kind == "QUIZ" || it.kind == "PRONUNCIATION" }.takeIf { it >= 0 }?.let(model::chooseActivity)
                                }
                            }
                        )
                    } else if (showErrorBanner) {
                        ResultBanner(
                            isCorrect = false,
                            title = currentTitle,
                            subtitle = currentSubtitle,
                            buttonText = "Viết lại",
                            onButton = {
                                showErrorBanner = false
                                model.clearInk()
                            }
                        )
                    }
                }
            }
        }

        // Confetti Canvas Overlay
        ConfettiOverlay(
            trigger = confettiTrigger,
            originCenter = canvasCenter
        )

        // Settings Bottom Sheet
        if (showSettingsSheet) {
            LessonSettingsSheet(
                onKnownWord = {
                    showSettingsSheet = false
                    model.markWordKnown()
                },
                onLeaveLesson = {
                    showSettingsSheet = false
                    model.leaveLesson()
                },
                onDismiss = { showSettingsSheet = false }
            )
        }
    }
}

/**
 * Toolbar pill button: height 36dp, rounded 12dp, bg White, border 1.5dp #d6e9de, text 13sp #5f7a6b weight 500.
 */
@Composable
private fun WritingToolbarButton(
    text: String,
    icon: @Composable () -> Unit,
    onClick: () -> Unit,
    enabled: Boolean,
    modifier: Modifier = Modifier
) {
    Surface(
        modifier = modifier
            .height(36.dp)
            .clickable(enabled = enabled, onClick = onClick),
        shape = RoundedCornerShape(12.dp),
        color = Color.White,
        border = BorderStroke(1.5.dp, LessonBorder),
        shadowElevation = 0.5.dp
    ) {
        Row(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.Center
        ) {
            Box(modifier = Modifier.size(15.dp)) {
                icon()
            }
            Spacer(modifier = Modifier.width(6.dp))
            Text(
                text = text,
                fontSize = 13.sp,
                fontWeight = FontWeight.Medium,
                color = if (enabled) ToolbarTextColor else ToolbarTextColor.copy(alpha = 0.4f)
            )
        }
    }
}

@Composable
private fun UndoVectorIcon(tint: Color) {
    Canvas(modifier = Modifier.fillMaxSize()) {
        val w = size.width
        val h = size.height
        val stroke = Stroke(width = 1.6.dp.toPx(), cap = StrokeCap.Round, join = StrokeJoin.Round)
        val path = androidx.compose.ui.graphics.Path().apply {
            moveTo(w * 0.40f, h * 0.25f)
            lineTo(w * 0.15f, h * 0.50f)
            lineTo(w * 0.40f, h * 0.75f)
        }
        drawPath(path, tint, style = stroke)
        val arcPath = androidx.compose.ui.graphics.Path().apply {
            moveTo(w * 0.18f, h * 0.50f)
            cubicTo(
                w * 0.50f, h * 0.35f,
                w * 0.85f, h * 0.45f,
                w * 0.85f, h * 0.75f
            )
        }
        drawPath(arcPath, tint, style = stroke)
    }
}

@Composable
private fun TrashVectorIcon(tint: Color) {
    Canvas(modifier = Modifier.fillMaxSize()) {
        val w = size.width
        val h = size.height
        val stroke = Stroke(width = 1.5.dp.toPx(), cap = StrokeCap.Round, join = StrokeJoin.Round)
        // Lid
        drawLine(tint, Offset(w * 0.20f, h * 0.25f), Offset(w * 0.80f, h * 0.25f), stroke.width, stroke.cap)
        drawLine(tint, Offset(w * 0.40f, h * 0.18f), Offset(w * 0.60f, h * 0.18f), stroke.width, stroke.cap)
        // Body
        val body = androidx.compose.ui.graphics.Path().apply {
            moveTo(w * 0.25f, h * 0.25f)
            lineTo(w * 0.30f, h * 0.85f)
            lineTo(w * 0.70f, h * 0.85f)
            lineTo(w * 0.75f, h * 0.25f)
        }
        drawPath(body, tint, style = stroke)
        // Internal bars
        drawLine(tint, Offset(w * 0.42f, h * 0.38f), Offset(w * 0.42f, h * 0.72f), stroke.width, stroke.cap)
        drawLine(tint, Offset(w * 0.58f, h * 0.38f), Offset(w * 0.58f, h * 0.72f), stroke.width, stroke.cap)
    }
}

/**
 * TianZiGe Grid (dashed lines #d9ebe0).
 */
@Composable
private fun TianZiGeGrid(
    modifier: Modifier = Modifier,
    color: Color = DemoGridColor
) {
    Canvas(modifier = modifier) {
        val stroke = Stroke(
            width = 1.2.dp.toPx(),
            pathEffect = PathEffect.dashPathEffect(floatArrayOf(10f, 10f), 0f)
        )
        // Vertical dashed line
        drawLine(
            color = color,
            start = Offset(size.width / 2f, 0f),
            end = Offset(size.width / 2f, size.height),
            strokeWidth = stroke.width,
            pathEffect = stroke.pathEffect
        )
        // Horizontal dashed line
        drawLine(
            color = color,
            start = Offset(0f, size.height / 2f),
            end = Offset(size.width, size.height / 2f),
            strokeWidth = stroke.width,
            pathEffect = stroke.pathEffect
        )
    }
}
