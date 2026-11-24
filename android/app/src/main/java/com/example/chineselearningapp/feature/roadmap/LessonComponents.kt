package com.example.chineselearningapp.feature.roadmap

import android.media.AudioManager
import android.media.ToneGenerator
import androidx.activity.compose.BackHandler
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.FastOutLinearInEasing
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.LinearOutSlowInEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.keyframes
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.spring
import androidx.compose.animation.core.tween
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.gestures.detectVerticalDragGestures
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
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Rect
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.Shadow
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.StrokeJoin
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.TextUnit
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlin.math.roundToInt
import com.example.chineselearningapp.R
import com.example.chineselearningapp.core.datastore.AppPreferences
import com.example.chineselearningapp.core.designsystem.*
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

/**
 * 3D Icon button with bottom shadow and pressed depression effect.
 * When pressed: translateY +3dp, bottom shadow reduces to 0dp.
 */
@Composable
fun Lesson3DIconButton(
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    content: @Composable () -> Unit,
) {
    val interactionSource = remember { MutableInteractionSource() }
    val isPressed by interactionSource.collectIsPressedAsState()
    val pressed = isPressed && enabled
    val offsetY = if (pressed) 3.dp else 0.dp
    val shadowY = if (pressed) 0.dp else 3.dp
    val alpha = if (enabled) 1f else 0.3f

    Box(
        modifier = modifier
            .size(width = 38.dp, height = 41.dp)
            .graphicsLayer { this.alpha = alpha },
        contentAlignment = Alignment.TopStart
    ) {
        if (shadowY > 0.dp) {
            Box(
                modifier = Modifier
                    .offset(y = 3.dp)
                    .size(38.dp)
                    .background(LessonShadow, RoundedCornerShape(12.dp))
            )
        }
        Box(
            modifier = Modifier
                .offset(y = offsetY)
                .size(38.dp)
                .background(Color.White, RoundedCornerShape(12.dp))
                .border(1.5.dp, LessonBorder, RoundedCornerShape(12.dp))
                .clickable(
                    interactionSource = interactionSource,
                    indication = null,
                    enabled = enabled,
                    onClick = onClick
                ),
            contentAlignment = Alignment.Center
        ) {
            content()
        }
    }
}

/**
 * Common TopBar for all lesson scenes (1 -> 9).
 * Back button | Animated Progress Bar with gradient & shine | Settings button
 */
@Composable
fun LessonTopBar(
    progress: Float,
    canGoBack: Boolean,
    onBack: () -> Unit,
    onSettings: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .padding(16.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(14.dp)
    ) {
        // 1. Back button: 38x38dp square, rounded 12dp, icon "<" stroke 2.8dp Primary
        Lesson3DIconButton(
            onClick = onBack,
            enabled = canGoBack
        ) {
            Canvas(modifier = Modifier.size(16.dp)) {
                val stroke = Stroke(width = 2.8.dp.toPx(), cap = StrokeCap.Round, join = StrokeJoin.Round)
                val path = Path().apply {
                    moveTo(size.width * 0.65f, size.height * 0.15f)
                    lineTo(size.width * 0.25f, size.height * 0.5f)
                    lineTo(size.width * 0.65f, size.height * 0.85f)
                }
                drawPath(path, color = Primary, style = stroke)
            }
        }

        // 2. Lesson progress bar: h=12dp, rounded, track #d6e9de, fill gradient #34c478 -> #1a7a4a, shine 3dp
        val animatedProgress by animateFloatAsState(
            targetValue = progress.coerceIn(0f, 1f),
            animationSpec = tween(durationMillis = 400, easing = FastOutSlowInEasing),
            label = "lessonProgressAnimation"
        )
        Canvas(
            modifier = Modifier
                .weight(1f)
                .height(12.dp)
        ) {
            val h = size.height
            val w = size.width
            val radius = CornerRadius(h / 2f, h / 2f)

            // Track
            drawRoundRect(
                color = LessonBorder,
                size = size,
                cornerRadius = radius
            )

            // Fill
            val fillW = (w * animatedProgress).coerceIn(0f, w)
            if (fillW > 0f) {
                drawRoundRect(
                    brush = Brush.horizontalGradient(
                        colors = listOf(ProgressGradientStart, ProgressGradientEnd),
                        startX = 0f,
                        endX = fillW
                    ),
                    size = Size(fillW, h),
                    cornerRadius = radius
                )
                // White highlight shine in upper half (3dp)
                if (fillW > 6.dp.toPx()) {
                    val shineH = 3.dp.toPx()
                    val insetX = 2.dp.toPx()
                    drawRoundRect(
                        color = Color.White.copy(alpha = 0.45f),
                        topLeft = Offset(insetX, 1.5.dp.toPx()),
                        size = Size(fillW - insetX * 2, shineH),
                        cornerRadius = CornerRadius(shineH / 2f, shineH / 2f)
                    )
                }
            }
        }

        // 3. Settings button: gear icon
        Lesson3DIconButton(
            onClick = onSettings,
            enabled = true
        ) {
            Icon(
                painter = painterResource(R.drawable.ic_settings),
                contentDescription = "Cài đặt bài học",
                tint = Primary,
                modifier = Modifier.size(20.dp)
            )
        }
    }
}

/**
 * Vector Speaker Icon (20dp).
 */
@Composable
private fun SpeakerIcon(
    tint: Color,
    modifier: Modifier = Modifier
) {
    Canvas(modifier = modifier) {
        val w = size.width
        val h = size.height
        val stroke = Stroke(width = 1.8.dp.toPx(), cap = StrokeCap.Round, join = StrokeJoin.Round)
        val path = Path().apply {
            moveTo(w * 0.15f, h * 0.35f)
            lineTo(w * 0.35f, h * 0.35f)
            lineTo(w * 0.60f, h * 0.15f)
            lineTo(w * 0.60f, h * 0.85f)
            lineTo(w * 0.35f, h * 0.65f)
            lineTo(w * 0.15f, h * 0.65f)
            close()
        }
        drawPath(path, tint)
        drawArc(
            color = tint,
            startAngle = -45f,
            sweepAngle = 90f,
            useCenter = false,
            topLeft = Offset(w * 0.45f, h * 0.25f),
            size = Size(w * 0.45f, h * 0.50f),
            style = stroke
        )
    }
}

/**
 * Vector Mute Speaker Icon (18dp) with diagonal slash.
 */
@Composable
private fun MuteSpeakerIcon(
    tint: Color,
    modifier: Modifier = Modifier
) {
    Canvas(modifier = modifier) {
        val w = size.width
        val h = size.height
        val stroke = Stroke(width = 2.dp.toPx(), cap = StrokeCap.Round, join = StrokeJoin.Round)
        val path = Path().apply {
            moveTo(w * 0.15f, h * 0.35f)
            lineTo(w * 0.35f, h * 0.35f)
            lineTo(w * 0.60f, h * 0.15f)
            lineTo(w * 0.60f, h * 0.85f)
            lineTo(w * 0.35f, h * 0.65f)
            lineTo(w * 0.15f, h * 0.65f)
            close()
        }
        drawPath(path, tint)
        // Diagonal slash line
        drawLine(
            color = tint,
            start = Offset(w * 0.15f, h * 0.15f),
            end = Offset(w * 0.85f, h * 0.85f),
            strokeWidth = stroke.width,
            cap = stroke.cap
        )
    }
}

/**
 * Vector Check Circle Icon (20dp).
 */
@Composable
private fun CheckCircleIcon(
    tint: Color,
    modifier: Modifier = Modifier
) {
    Canvas(modifier = modifier) {
        val w = size.width
        val h = size.height
        val stroke = Stroke(width = 2.dp.toPx(), cap = StrokeCap.Round, join = StrokeJoin.Round)
        drawCircle(
            color = tint,
            radius = w * 0.45f,
            style = stroke
        )
        val checkPath = Path().apply {
            moveTo(w * 0.28f, h * 0.50f)
            lineTo(w * 0.44f, h * 0.66f)
            lineTo(w * 0.72f, h * 0.36f)
        }
        drawPath(checkPath, tint, style = stroke)
    }
}

/**
 * Vector Exit Door Icon (20dp).
 */
@Composable
private fun ExitDoorIcon(
    tint: Color,
    modifier: Modifier = Modifier
) {
    Canvas(modifier = modifier) {
        val w = size.width
        val h = size.height
        val stroke = Stroke(width = 2.dp.toPx(), cap = StrokeCap.Round, join = StrokeJoin.Round)
        // Door frame
        val doorPath = Path().apply {
            moveTo(w * 0.50f, h * 0.15f)
            lineTo(w * 0.20f, h * 0.15f)
            lineTo(w * 0.20f, h * 0.85f)
            lineTo(w * 0.50f, h * 0.85f)
        }
        drawPath(doorPath, tint, style = stroke)
        // Arrow going out to the right
        drawLine(
            color = tint,
            start = Offset(w * 0.35f, h * 0.50f),
            end = Offset(w * 0.85f, h * 0.50f),
            strokeWidth = stroke.width,
            cap = stroke.cap
        )
        val arrowHead = Path().apply {
            moveTo(w * 0.68f, h * 0.34f)
            lineTo(w * 0.85f, h * 0.50f)
            lineTo(w * 0.68f, h * 0.66f)
        }
        drawPath(arrowHead, tint, style = stroke)
    }
}

/**
 * Bottom Sheet for lesson settings:
 * - Scrim: Color.Black alpha 0.40 covering full screen, click or swipe down closes sheet.
 * - Sheet: anchored at bottom, rounded top corners 24dp, white background,
 *   padding: top 10dp, horizontal 16dp, bottom 18dp + navigationBarsPadding().
 * - Grab handle: 40x4dp, bo 2dp, #d6e9de, centered, 12dp margin bottom.
 * - Title: "Cài đặt bài học" 15sp weight 500, margin bottom 10dp.
 * - Volume Row: #f4faf6 background, rounded 14dp, padding 10x12dp, gap 10dp.
 *   Speaker icon Primary 20dp, Slider (weight 1, Primary), Mute button 34dp rounded 12dp,
 *   border 1.5dp #d6e9de, bottom shadow 2dp #c8e0d2, icon loa gạch chéo #a32d2d.
 * - Option "Tôi đã biết từ này": #e8f5ee background, #b9dfc9 border 2dp, rounded 14dp,
 *   padding 11x12dp, gap 10dp, text #0f5533. Icon check 20dp. Confirmation dialog -> onKnownWord().
 * - Option "Rời bài học": #fdecec background, #f0bcbc border 2dp, rounded 14dp,
 *   padding 11x12dp, gap 10dp, text #a32d2d. Icon door 20dp. Confirmation dialog -> onLeaveLesson().
 * - Animation: open (scrim fadeIn 250ms + sheet slide up spring dampingRatio 0.7),
 *   close (sheet slide down + scrim fadeOut 200ms).
 */
@Composable
fun LessonSettingsSheet(
    onKnownWord: () -> Unit,
    onLeaveLesson: () -> Unit,
    onDismiss: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val appPreferences = remember(context) { AppPreferences(context.applicationContext) }
    val scope = rememberCoroutineScope()
    val audioVolume by appPreferences.audioVolume.collectAsState(initial = 1.0f)
    var currentVol by remember(audioVolume) { mutableFloatStateOf(audioVolume) }
    var previousVolume by rememberSaveable { mutableFloatStateOf(0.70f) }

    var showKnownWordDialog by remember { mutableStateOf(false) }
    var showLeaveDialog by remember { mutableStateOf(false) }

    val toneGen = remember {
        try { ToneGenerator(AudioManager.STREAM_MUSIC, 100) } catch (_: Exception) { null }
    }
    DisposableEffect(Unit) {
        onDispose { toneGen?.release() }
    }

    val scrimAlpha = remember { Animatable(0f) }
    val sheetOffsetY = remember { Animatable(1000f) }
    var isClosing by remember { mutableStateOf(false) }

    fun dismissWithAnimation() {
        if (isClosing) return
        isClosing = true
        scope.launch {
            launch {
                scrimAlpha.animateTo(
                    targetValue = 0f,
                    animationSpec = tween(durationMillis = 200, easing = FastOutLinearInEasing)
                )
            }
            sheetOffsetY.animateTo(
                targetValue = 1000f,
                animationSpec = tween(durationMillis = 200, easing = FastOutLinearInEasing)
            )
            onDismiss()
        }
    }

    LaunchedEffect(Unit) {
        launch {
            scrimAlpha.animateTo(
                targetValue = 0.40f,
                animationSpec = tween(durationMillis = 250, easing = LinearOutSlowInEasing)
            )
        }
        sheetOffsetY.animateTo(
            targetValue = 0f,
            animationSpec = spring(
                dampingRatio = 0.7f,
                stiffness = Spring.StiffnessMediumLow
            )
        )
    }

    BackHandler(enabled = true) {
        if (showKnownWordDialog || showLeaveDialog) {
            showKnownWordDialog = false
            showLeaveDialog = false
        } else {
            dismissWithAnimation()
        }
    }

    var lastTingTime by remember { mutableLongStateOf(0L) }

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(Color.Black.copy(alpha = scrimAlpha.value))
            .clickable(
                interactionSource = remember { MutableInteractionSource() },
                indication = null,
                onClick = { dismissWithAnimation() }
            )
    ) {
        // Sheet Card resting at bottom
        Box(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .fillMaxWidth()
                .offset { IntOffset(0, sheetOffsetY.value.roundToInt().coerceAtLeast(0)) }
                .shadow(
                    elevation = 16.dp,
                    shape = RoundedCornerShape(topStart = 24.dp, topEnd = 24.dp),
                    spotColor = Color.Black.copy(alpha = 0.25f)
                )
                .background(
                    color = Color.White,
                    shape = RoundedCornerShape(topStart = 24.dp, topEnd = 24.dp)
                )
                .pointerInput(Unit) {
                    detectVerticalDragGestures(
                        onVerticalDrag = { change, dragAmount ->
                            change.consume()
                            if (dragAmount > 0) {
                                scope.launch {
                                    sheetOffsetY.snapTo(sheetOffsetY.value + dragAmount)
                                }
                            }
                        },
                        onDragEnd = {
                            if (sheetOffsetY.value > 120f) {
                                dismissWithAnimation()
                            } else {
                                scope.launch {
                                    sheetOffsetY.animateTo(
                                        targetValue = 0f,
                                        animationSpec = spring(dampingRatio = 0.7f)
                                    )
                                }
                            }
                        }
                    )
                }
                .clickable(
                    interactionSource = remember { MutableInteractionSource() },
                    indication = null,
                    onClick = {} // Consume click inside sheet
                )
                .navigationBarsPadding()
                .padding(top = 10.dp, start = 16.dp, end = 16.dp, bottom = 18.dp)
        ) {
            Column(
                modifier = Modifier.fillMaxWidth()
            ) {
                // Grab handle: 40x4dp, bo 2dp, #d6e9de, centered, 12dp margin below
                Box(
                    modifier = Modifier
                        .align(Alignment.CenterHorizontally)
                        .size(width = 40.dp, height = 4.dp)
                        .background(LessonBorder, RoundedCornerShape(2.dp))
                )

                Spacer(modifier = Modifier.height(12.dp))

                // 1. Tiêu đề "Cài đặt bài học": 15sp weight 500, margin bottom 10dp
                Text(
                    text = "Cài đặt bài học",
                    fontSize = 15.sp,
                    fontWeight = FontWeight.Medium,
                    color = TextPrimary
                )

                Spacer(modifier = Modifier.height(10.dp))

                // 2. Hàng âm lượng: nền #f4faf6, bo 14dp, padding 10x12dp, Row căn giữa dọc, gap 10dp
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(LessonVolumeBg, RoundedCornerShape(14.dp))
                        .padding(horizontal = 12.dp, vertical = 10.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    // Icon loa Primary 20dp
                    SpeakerIcon(
                        tint = Primary,
                        modifier = Modifier.size(20.dp)
                    )

                    // Slider âm lượng (weight 1, accent Primary, 0-100)
                    Slider(
                        value = currentVol,
                        onValueChange = { newVol ->
                            currentVol = newVol
                            val now = System.currentTimeMillis()
                            if (now - lastTingTime > 150L && newVol > 0.05f) {
                                lastTingTime = now
                                try { toneGen?.startTone(ToneGenerator.TONE_PROP_BEEP, 40) } catch (_: Exception) {}
                            }
                        },
                        onValueChangeFinished = {
                            scope.launch { appPreferences.setAudioVolume(currentVol) }
                        },
                        valueRange = 0f..1f,
                        colors = SliderDefaults.colors(
                            thumbColor = Primary,
                            activeTrackColor = Primary,
                            inactiveTrackColor = LessonBorder
                        ),
                        modifier = Modifier.weight(1f)
                    )

                    // Nút mute vuông 34dp, bo 12dp, nền trắng, viền 1.5dp #d6e9de, bottom shadow 2dp #c8e0d2, icon loa gạch chéo #a32d2d
                    val isMuted = currentVol <= 0.001f
                    Box(
                        modifier = Modifier
                            .size(34.dp)
                            .shadow(
                                elevation = 2.dp,
                                shape = RoundedCornerShape(12.dp),
                                spotColor = LessonShadow,
                                ambientColor = LessonShadow
                            )
                            .background(Color.White, RoundedCornerShape(12.dp))
                            .border(1.5.dp, LessonBorder, RoundedCornerShape(12.dp))
                            .clickable {
                                if (isMuted) {
                                    val restore = if (previousVolume > 0.05f) previousVolume else 0.70f
                                    currentVol = restore
                                    scope.launch { appPreferences.setAudioVolume(restore) }
                                } else {
                                    previousVolume = if (currentVol > 0.05f) currentVol else 0.70f
                                    currentVol = 0f
                                    scope.launch { appPreferences.setAudioVolume(0f) }
                                }
                            },
                        contentAlignment = Alignment.Center
                    ) {
                        MuteSpeakerIcon(
                            tint = DangerColor,
                            modifier = Modifier.size(18.dp)
                        )
                    }
                }

                Spacer(modifier = Modifier.height(10.dp))

                // 3. Option "Tôi đã biết từ này": nền #e8f5ee, viền 2dp #b9dfc9, bo 14dp, padding 11x12dp, gap 10dp, chữ #0f5533
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(PinyinBg, RoundedCornerShape(14.dp))
                        .border(2.dp, PinyinBorder, RoundedCornerShape(14.dp))
                        .clickable { showKnownWordDialog = true }
                        .padding(horizontal = 12.dp, vertical = 11.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    // Icon dấu tích 20dp
                    CheckCircleIcon(
                        tint = PrimaryDark,
                        modifier = Modifier.size(20.dp)
                    )

                    Column(
                        modifier = Modifier.weight(1f)
                    ) {
                        Text(
                            text = "Tôi đã biết từ này",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Medium,
                            color = PrimaryDark
                        )
                        Text(
                            text = "Tính hoàn thành, không cộng XP",
                            fontSize = 11.sp,
                            color = PrimaryDark.copy(alpha = 0.75f)
                        )
                    }
                }

                Spacer(modifier = Modifier.height(10.dp))

                // 4. Option "Rời bài học": nền #fdecec, viền 2dp #f0bcbc, bo 14dp, padding 11x12dp, gap 10dp, chữ #a32d2d
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(DangerBg, RoundedCornerShape(14.dp))
                        .border(2.dp, DangerBorder, RoundedCornerShape(14.dp))
                        .clickable { showLeaveDialog = true }
                        .padding(horizontal = 12.dp, vertical = 11.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    // Icon cửa 20dp
                    ExitDoorIcon(
                        tint = DangerColor,
                        modifier = Modifier.size(20.dp)
                    )

                    Column(
                        modifier = Modifier.weight(1f)
                    ) {
                        Text(
                            text = "Rời bài học",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Medium,
                            color = DangerColor
                        )
                        Text(
                            text = "Chưa tính hoàn thành",
                            fontSize = 11.sp,
                            color = DangerColor.copy(alpha = 0.75f)
                        )
                    }
                }
            }
        }

        // Dialog xác nhận "Đánh dấu đã biết từ này?"
        if (showKnownWordDialog) {
            AlertDialog(
                onDismissRequest = { showKnownWordDialog = false },
                title = {
                    Text(
                        text = "Đánh dấu đã biết từ này?",
                        fontSize = 17.sp,
                        fontWeight = FontWeight.Bold,
                        color = TextPrimary
                    )
                },
                text = {
                    Text(
                        text = "Từ này sẽ được tính là đã học xong mà không cộng điểm XP.",
                        fontSize = 14.sp,
                        color = TextSecondary
                    )
                },
                confirmButton = {
                    TextButton(
                        onClick = {
                            showKnownWordDialog = false
                            onDismiss()
                            onKnownWord()
                        }
                    ) {
                        Text("Đồng ý", color = PrimaryDark, fontWeight = FontWeight.Bold)
                    }
                },
                dismissButton = {
                    TextButton(onClick = { showKnownWordDialog = false }) {
                        Text("Hủy", color = TextSecondary)
                    }
                },
                shape = RoundedCornerShape(20.dp),
                containerColor = Color.White
            )
        }

        // Dialog xác nhận "Rời bài học?"
        if (showLeaveDialog) {
            AlertDialog(
                onDismissRequest = { showLeaveDialog = false },
                title = {
                    Text(
                        text = "Rời bài học?",
                        fontSize = 17.sp,
                        fontWeight = FontWeight.Bold,
                        color = TextPrimary
                    )
                },
                text = {
                    Text(
                        text = "Tiến độ bài này sẽ không được lưu.",
                        fontSize = 14.sp,
                        color = TextSecondary
                    )
                },
                confirmButton = {
                    TextButton(
                        onClick = {
                            showLeaveDialog = false
                            onDismiss()
                            onLeaveLesson()
                        }
                    ) {
                        Text("Rời đi", color = DangerColor, fontWeight = FontWeight.Bold)
                    }
                },
                dismissButton = {
                    TextButton(onClick = { showLeaveDialog = false }) {
                        Text("Ở lại", color = TextSecondary)
                    }
                },
                shape = RoundedCornerShape(20.dp),
                containerColor = Color.White
            )
        }
    }
}

/**
 * 3D Primary Button: height 52dp, rounded 16dp, bottom shadow 5dp #0f5533, depresses 4dp when pressed.
 */
@Composable
fun LessonPrimary3DButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    containerColor: Color = Primary,
    shadowColor: Color = PrimaryDark,
) {
    val interactionSource = remember { MutableInteractionSource() }
    val isPressed by interactionSource.collectIsPressedAsState()
    val pressed = isPressed && enabled
    val offsetY = if (pressed) 4.dp else 0.dp
    val alpha = if (enabled) 1f else 0.40f

    Box(
        modifier = modifier
            .fillMaxWidth()
            .height(57.dp)
            .graphicsLayer { this.alpha = alpha },
        contentAlignment = Alignment.TopCenter
    ) {
        // Bottom shadow
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .offset(y = 5.dp)
                .height(52.dp)
                .background(shadowColor, RoundedCornerShape(16.dp))
        )
        // Button surface
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .offset(y = offsetY)
                .height(52.dp)
                .background(containerColor, RoundedCornerShape(16.dp))
                .clickable(
                    interactionSource = interactionSource,
                    indication = null,
                    enabled = enabled,
                    onClick = onClick
                ),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = text,
                color = Color.White,
                fontSize = 17.sp,
                fontWeight = FontWeight.SemiBold
            )
        }
    }
}

/**
 * Tian Zi Ge (田字格) dashed grid canvas.
 */
@Composable
fun TianZiGeGridCanvas(
    modifier: Modifier = Modifier,
    inset: Dp = 10.dp,
    cornerRadius: Dp = 14.dp,
    color: Color = TianZiGeGrid,
    strokeWidth: Dp = 1.5.dp,
) {
    Canvas(modifier = modifier.fillMaxSize()) {
        val insetPx = inset.toPx()
        val gridRect = Rect(insetPx, insetPx, size.width - insetPx, size.height - insetPx)
        val dashEffect = PathEffect.dashPathEffect(floatArrayOf(10f, 8f), 0f)
        val stroke = Stroke(width = strokeWidth.toPx(), pathEffect = dashEffect)

        // Outer dashed box
        drawRoundRect(
            color = color,
            topLeft = Offset(gridRect.left, gridRect.top),
            size = Size(gridRect.width, gridRect.height),
            cornerRadius = CornerRadius(cornerRadius.toPx(), cornerRadius.toPx()),
            style = stroke
        )

        // Horizontal dashed divider
        val midY = gridRect.top + gridRect.height / 2f
        drawLine(
            color = color,
            start = Offset(gridRect.left, midY),
            end = Offset(gridRect.right, midY),
            strokeWidth = strokeWidth.toPx(),
            pathEffect = dashEffect
        )

        // Vertical dashed divider
        val midX = gridRect.left + gridRect.width / 2f
        drawLine(
            color = color,
            start = Offset(midX, gridRect.top),
            end = Offset(midX, gridRect.bottom),
            strokeWidth = strokeWidth.toPx(),
            pathEffect = dashEffect
        )
    }
}

/**
 * Reveal animation container:
 * fadeIn + translateY 18dp -> 0 + scale 0.96 -> 1, 450ms spring (dampingRatio 0.6).
 * Reserves its layout space when not visible so the surrounding layout never jumps.
 * Blocks touch when not visible.
 */
@Composable
fun RevealContainer(
    visible: Boolean,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit,
) {
    val revealProgress by animateFloatAsState(
        targetValue = if (visible) 1f else 0f,
        animationSpec = spring(
            dampingRatio = 0.6f,
            stiffness = Spring.StiffnessLow
        ),
        label = "revealSpringAnim"
    )

    Box(
        modifier = modifier
            .graphicsLayer {
                alpha = revealProgress
                scaleX = 0.96f + 0.04f * revealProgress
                scaleY = 0.96f + 0.04f * revealProgress
                translationY = 18.dp.toPx() * (1f - revealProgress)
            },
        contentAlignment = Alignment.Center
    ) {
        Box(
            modifier = if (revealProgress < 0.95f) Modifier.pointerInput(Unit) {
                // Block touch interactions when invisible/revealing
                awaitPointerEventScope {
                    while (true) {
                        val event = awaitPointerEvent()
                        event.changes.forEach { it.consume() }
                    }
                }
            } else Modifier
        ) {
            content()
        }
    }
}

@Composable
internal fun LessonFrame(title: String, step: LessonStep, enabled: Boolean, back: () -> Unit,
    hint: String, action: String, actionEnabled: Boolean, onAction: () -> Unit,
    status: @Composable () -> Unit = {}, content: @Composable ColumnScope.() -> Unit) {
    Column(Modifier.fillMaxSize().background(Surface0).imePadding(), horizontalAlignment = Alignment.CenterHorizontally) {
        Row(Modifier.widthIn(max = 680.dp).fillMaxWidth().padding(horizontal = 12.dp), verticalAlignment = Alignment.CenterVertically) {
            TextButton(onClick = back, enabled = enabled) { Text(stringResource(R.string.writing_back)) }
            Text(title, Modifier.weight(1f), style = FontTitle)
            Text(stringResource(R.string.lesson_flow_step, step.ordinal + 1, LessonStep.entries.size), style = FontLabel, color = TextMuted)
        }
        Column(Modifier.widthIn(max = 680.dp).fillMaxWidth().padding(horizontal = 24.dp)) { status() }
        Column(Modifier.weight(1f).widthIn(max = 680.dp).fillMaxWidth()
            .verticalScroll(rememberScrollState()).padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(16.dp), content = content)
        Column(Modifier.widthIn(max = 680.dp).fillMaxWidth().navigationBarsPadding().padding(24.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)) {
            MascotChatBar(hint)
            PrimaryButton(action, onAction, enabled = enabled && actionEnabled)
        }
    }
}

@Composable
internal fun LessonListen(text: String) {
    val speech = rememberWordSpeech(text)
    IconButton(onClick = speech.speak, enabled = speech.ready) {
        Icon(painterResource(R.drawable.ic_volume), stringResource(R.string.word_reveal_listen), tint = Primary)
    }
    if (speech.unavailable) Text(stringResource(R.string.word_reveal_tts_unavailable), style = FontLabel)
}

@Composable
internal fun LessonFeedback(correct: Boolean?) {
    if (correct != null) Text(stringResource(if (correct) R.string.lesson_flow_correct else R.string.lesson_flow_incorrect),
        color = if (correct) Primary else MaterialTheme.colorScheme.error, style = FontBody)
}

/**
 * ResultBanner: shared bottom feedback banner for lessons (writing, quiz, pinyin, etc.).
 * Slides up from bottom with spring (dampingRatio 0.65).
 * - Correct: bg #dff5e8, top border 2dp #b9dfc9, text #0f5533, TigerVariant.Happy (bouncing translateY 0 -> -8dp)
 * - Incorrect: bg #fde8e8, top border 2dp #f0bcbc, text #a32d2d, TigerVariant.Sad (stationary)
 */
@Composable
fun ResultBanner(
    isCorrect: Boolean,
    title: String,
    subtitle: String,
    buttonText: String,
    onButton: () -> Unit,
    modifier: Modifier = Modifier,
    answerChip: String? = null,
    onPlayAudio: (() -> Unit)? = null,
    secondaryText: String? = null,
    onSecondary: (() -> Unit)? = null,
    customAnswerChip: (@Composable () -> Unit)? = null
) {
    val bgColor = if (isCorrect) SuccessBannerBg else DangerBannerBg
    val borderColor = if (isCorrect) PinyinBorder else DangerBorder
    val textColor = if (isCorrect) PrimaryDark else DangerColor
    val btnBgColor = if (isCorrect) Primary else DangerButtonBg
    val btnShadowColor = if (isCorrect) PrimaryDark else DangerColor

    val tigerVariant = if (isCorrect) TigerVariant.Happy else TigerVariant.Sad

    // Continuous bouncing for happy tiger: translateY 0 -> -8dp
    val infiniteTransition = rememberInfiniteTransition(label = "HappyTigerBounce")
    val bounceTranslateY by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = -8f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 350, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "BounceY"
    )
    val tigerOffset = if (isCorrect) bounceTranslateY.dp else 0.dp

    Box(
        modifier = modifier
            .fillMaxWidth()
            .shadow(elevation = 16.dp, shape = RoundedCornerShape(topStart = 24.dp, topEnd = 24.dp))
            .background(bgColor, RoundedCornerShape(topStart = 24.dp, topEnd = 24.dp))
            .border(
                BorderStroke(2.dp, borderColor),
                RoundedCornerShape(topStart = 24.dp, topEnd = 24.dp)
            )
            .navigationBarsPadding()
            .padding(top = 14.dp, start = 16.dp, end = 16.dp, bottom = 18.dp)
    ) {
        Column(
            modifier = Modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // Tiger avatar: 54x64dp
                TigerCanvas(
                    modifier = Modifier.offset(y = tigerOffset),
                    variant = tigerVariant,
                    animateIdle = !isCorrect,
                    width = 54.dp,
                    height = 64.dp
                )

                // Text column
                Column(
                    modifier = Modifier.weight(1f),
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Text(
                        text = title,
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Medium,
                        color = textColor
                    )
                    if (customAnswerChip != null) {
                        customAnswerChip()
                    } else if (answerChip != null) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                            modifier = Modifier.padding(vertical = 2.dp)
                        ) {
                            Surface(
                                shape = RoundedCornerShape(12.dp),
                                color = Color.White,
                                border = BorderStroke(2.dp, DangerBorder)
                            ) {
                                Text(
                                    text = answerChip,
                                    modifier = Modifier.padding(horizontal = 14.dp, vertical = 3.dp),
                                    fontSize = 22.sp,
                                    fontWeight = FontWeight.Medium,
                                    color = TextPrimary
                                )
                            }
                            if (onPlayAudio != null) {
                                Box(
                                    modifier = Modifier
                                        .size(32.dp)
                                        .background(Color.White, CircleShape)
                                        .border(1.5.dp, DangerBorder, CircleShape)
                                        .clickable(onClick = onPlayAudio),
                                    contentAlignment = Alignment.Center
                                ) {
                                    Icon(
                                        painter = painterResource(R.drawable.ic_volume),
                                        contentDescription = "Nghe lại đáp án",
                                        tint = DangerColor,
                                        modifier = Modifier.size(18.dp)
                                    )
                                }
                            }
                        }
                    }
                    Text(
                        text = subtitle,
                        fontSize = 13.sp,
                        color = textColor.copy(alpha = 0.85f)
                    )
                }
            }

            // PrimaryButton 3D + Optional Secondary Flat Text Button (10dp gap)
            Column(
                modifier = Modifier.fillMaxWidth(),
                verticalArrangement = Arrangement.spacedBy(10.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                LessonPrimary3DButton(
                    text = buttonText,
                    onClick = onButton,
                    modifier = Modifier.fillMaxWidth(),
                    containerColor = btnBgColor,
                    shadowColor = btnShadowColor
                )

                if (secondaryText != null && onSecondary != null) {
                    Text(
                        text = secondaryText,
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Medium,
                        color = DangerColor,
                        textAlign = TextAlign.Center,
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable(
                                interactionSource = remember { MutableInteractionSource() },
                                indication = null,
                                onClick = onSecondary
                            )
                            .padding(vertical = 4.dp)
                    )
                }
            }
        }
    }
}

