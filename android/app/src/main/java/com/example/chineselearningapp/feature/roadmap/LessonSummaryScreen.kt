package com.example.chineselearningapp.feature.roadmap

import androidx.compose.animation.core.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.*
import androidx.compose.ui.graphics.drawscope.Fill
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.rotate
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.em
import androidx.compose.ui.unit.sp
import com.example.chineselearningapp.R
import com.example.chineselearningapp.core.designsystem.*
import com.example.chineselearningapp.domain.model.RoadmapCompletion
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.util.Locale
import kotlin.math.PI
import kotlin.math.cos
import kotlin.math.pow
import kotlin.math.sin

private val EaseOutExpoEasing = Easing { fraction ->
    if (fraction >= 1f) 1f else 1f - 2.0.pow(-10.0 * fraction).toFloat()
}

@Composable
internal fun LessonSummaryScreen(
    state: LessonState,
    completion: RoadmapCompletion?,
    enabled: Boolean,
    ready: Boolean,
    back: () -> Unit,
    complete: () -> Unit,
    continuePath: () -> Unit,
    resume: () -> Unit,
    hasNextWord: Boolean = false,
    replay: (() -> Unit)? = null,
    status: @Composable () -> Unit = {}
) {
    val haptic = LocalHapticFeedback.current

    val targetAccuracy = state.accuracy
    val targetSeconds = state.elapsedTime.coerceAtMost(Int.MAX_VALUE.toLong()).toInt()
    val targetCorrect = state.correctCount
    val targetAnswers = state.answerCount
    val targetXp = completion?.exp ?: state.lessonScore
    val starCount = when {
        targetAccuracy >= 100 -> 3
        targetAccuracy >= 70 -> 2
        else -> 1
    }
    val isCelebrate = targetAccuracy >= 70

    // Entrance animation animatables
    val ribbonOffsetY = remember { Animatable(-100f) }
    val ribbonScale = remember { Animatable(0.8f) }

    val tigerInScale = remember { Animatable(0f) }
    val tigerInOffsetY = remember { Animatable(30f) }

    val star1Scale = remember { Animatable(0f) }
    val star1Rotation = remember { Animatable(-90f) }
    val star2Scale = remember { Animatable(0f) }
    val star2Rotation = remember { Animatable(-90f) }
    val star3Scale = remember { Animatable(0f) }
    val star3Rotation = remember { Animatable(-90f) }

    val sign1Drop = remember { Animatable(-90f) }
    val sign2Drop = remember { Animatable(-90f) }
    val sign3Drop = remember { Animatable(-90f) }
    val signNumbersProgress = remember { Animatable(0f) }

    val xpCardOffsetY = remember { Animatable(50f) }
    val xpCardAlpha = remember { Animatable(0f) }
    val xpProgress = remember { Animatable(0f) }

    val ctaAlpha = remember { Animatable(0f) }
    val ctaOffsetY = remember { Animatable(20f) }

    // Sequence orchestrator
    LaunchedEffect(Unit) {
        // 0.0s Ribbon falls
        launch {
            ribbonOffsetY.animateTo(0f, spring(dampingRatio = 0.5f, stiffness = Spring.StiffnessMediumLow))
        }
        launch {
            ribbonScale.animateTo(1f, spring(dampingRatio = 0.5f, stiffness = Spring.StiffnessMediumLow))
        }

        // 0.3s Mascot tiger jumps in
        launch {
            delay(300)
            launch { tigerInScale.animateTo(1f, spring(dampingRatio = 0.6f, stiffness = Spring.StiffnessMediumLow)) }
            launch { tigerInOffsetY.animateTo(0f, spring(dampingRatio = 0.6f, stiffness = Spring.StiffnessMediumLow)) }
        }

        // 0.5s Star 1 pops
        launch {
            delay(500)
            haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
            launch { star1Scale.animateTo(1f, spring(dampingRatio = 0.45f, stiffness = Spring.StiffnessMediumLow)) }
            launch { star1Rotation.animateTo(0f, spring(dampingRatio = 0.45f, stiffness = Spring.StiffnessMediumLow)) }
        }

        // 0.8s Star 2 pops
        launch {
            delay(800)
            haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
            launch { star2Scale.animateTo(1f, spring(dampingRatio = 0.45f, stiffness = Spring.StiffnessMediumLow)) }
            launch { star2Rotation.animateTo(0f, spring(dampingRatio = 0.45f, stiffness = Spring.StiffnessMediumLow)) }
        }

        // 1.1s Star 3 pops
        launch {
            delay(1100)
            haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
            launch { star3Scale.animateTo(1f, spring(dampingRatio = 0.45f, stiffness = Spring.StiffnessMediumLow)) }
            launch { star3Rotation.animateTo(0f, spring(dampingRatio = 0.45f, stiffness = Spring.StiffnessMediumLow)) }
        }

        // 1.2s Three wooden signs drop down sequentially (150ms stagger)
        launch {
            delay(1200)
            launch { sign1Drop.animateTo(0f, spring(dampingRatio = 0.55f, stiffness = Spring.StiffnessMediumLow)) }
            launch {
                delay(150)
                sign2Drop.animateTo(0f, spring(dampingRatio = 0.55f, stiffness = Spring.StiffnessMediumLow))
            }
            launch {
                delay(300)
                sign3Drop.animateTo(0f, spring(dampingRatio = 0.55f, stiffness = Spring.StiffnessMediumLow))
            }
            launch {
                signNumbersProgress.animateTo(1f, tween(durationMillis = 1000, easing = EaseOutExpoEasing))
            }
        }

        // 1.8s XP card slides up + counts up
        launch {
            delay(1800)
            launch { xpCardOffsetY.animateTo(0f, spring(dampingRatio = 0.65f, stiffness = Spring.StiffnessMediumLow)) }
            launch { xpCardAlpha.animateTo(1f, tween(400)) }
            launch { xpProgress.animateTo(1f, tween(1200, easing = EaseOutQuad)) }
        }

        // 2.2s CTA button fades in
        launch {
            delay(2200)
            launch { ctaOffsetY.animateTo(0f, tween(400, easing = EaseOutQuad)) }
            launch { ctaAlpha.animateTo(1f, tween(400)) }
        }
    }

    // Continuous loop animations
    val loopTransition = rememberInfiniteTransition(label = "SummaryContinuousLoops")

    // Mascot vertical jump: translateY 0 -> -12dp, cycle 1.2s (600ms each way)
    val tigerJump by loopTransition.animateFloat(
        initialValue = 0f,
        targetValue = -12f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 600, easing = EaseInOutQuad),
            repeatMode = RepeatMode.Reverse
        ),
        label = "TigerJump"
    )

    // Signs sway: pivot top center, rotate -4° <-> +4°, cycle 3s (3000ms), 0.5s phase offset
    val swayPhase by loopTransition.animateFloat(
        initialValue = 0f,
        targetValue = (2 * PI).toFloat(),
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 3000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "SwayPhase"
    )
    val swayAngle1 = 4f * sin(swayPhase)
    val swayAngle2 = 4f * sin(swayPhase - (0.5f / 3.0f * 2 * PI).toFloat())
    val swayAngle3 = 4f * sin(swayPhase - (1.0f / 3.0f * 2 * PI).toFloat())

    // XP Card shine diagonal sweep every 2.6s
    val shineProgress by loopTransition.animateFloat(
        initialValue = -1f,
        targetValue = 2.2f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 2600, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "XpShine"
    )

    // Golden glow pulse if perfect
    val glowAlpha by if (state.mistakeCount == 0) {
        loopTransition.animateFloat(
            initialValue = 0.4f,
            targetValue = 1.0f,
            animationSpec = infiniteRepeatable(
                animation = tween(durationMillis = 800, easing = EaseInOut),
                repeatMode = RepeatMode.Reverse
            ),
            label = "GlowPulse"
        )
    } else {
        remember { mutableFloatStateOf(1.0f) }
    }

    // Computed numbers
    val displaySeconds = (targetSeconds * signNumbersProgress.value).toInt()
    val displayAccuracy = (targetAccuracy * signNumbersProgress.value).toInt()
    val displayCorrect = (targetCorrect * signNumbersProgress.value).toInt()
    val displayXp = (targetXp * xpProgress.value).toInt()

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    0.0f to Color(0xFF0F5533),
                    0.38f to Color(0xFF1A7A4A),
                    1.0f to Color(0xFFE8F5EE)
                )
            )
    ) {
        // Confetti: only if accuracy >= 70%
        if (targetAccuracy >= 70) {
            ConfettiRain(modifier = Modifier.fillMaxSize())
        }

        Column(
            modifier = Modifier
                .fillMaxSize()
                .statusBarsPadding()
                .navigationBarsPadding()
                .padding(horizontal = 20.dp, vertical = 8.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // Optional status / error banner
            status()

            // 1. Ruy băng tiêu đề "Hoàn thành!"
            Spacer(Modifier.height(4.dp))
            SummaryRibbon(
                scale = ribbonScale.value,
                offsetY = ribbonOffsetY.value
            )

            Spacer(Modifier.height(10.dp))

            // 2. Sao đánh giá (3 sao)
            StarRatingRow(
                starCount = starCount,
                star1Scale = star1Scale.value,
                star1Rot = star1Rotation.value,
                star2Scale = star2Scale.value,
                star2Rot = star2Rotation.value,
                star3Scale = star3Scale.value,
                star3Rot = star3Rotation.value
            )

            Spacer(Modifier.height(8.dp))

            // 3. Mascot hổ + Sunburst
            Box(
                modifier = Modifier
                    .size(width = 160.dp, height = 96.dp),
                contentAlignment = Alignment.Center
            ) {
                SunburstBackground(
                    modifier = Modifier.size(190.dp)
                )
                TigerCanvas(
                    modifier = Modifier
                        .graphicsLayer {
                            scaleX = tigerInScale.value
                            scaleY = tigerInScale.value
                            translationY = tigerInOffsetY.value + tigerJump.dp.toPx()
                        },
                    variant = if (isCelebrate) TigerVariant.Celebrate else TigerVariant.Encourage,
                    animateIdle = false,
                    width = 68.dp,
                    height = 82.dp
                )
            }

            Spacer(Modifier.height(10.dp))

            // 4. Ba biển gỗ treo dây
            HangingWoodenSignsRow(
                sign1Drop = sign1Drop.value,
                sign2Drop = sign2Drop.value,
                sign3Drop = sign3Drop.value,
                sway1 = swayAngle1,
                sway2 = swayAngle2,
                sway3 = swayAngle3,
                timeString = String.format(Locale.getDefault(), "%d:%02d", displaySeconds / 60, displaySeconds % 60),
                accuracyString = "$displayAccuracy%",
                scoreString = if (targetAnswers > 0) "$displayCorrect/$targetAnswers" else "$displayCorrect/${displayCorrect.coerceAtLeast(1)}"
            )

            Spacer(Modifier.height(12.dp))

            // 5. Bảng XP
            XpCard(
                xp = displayXp,
                mistakeCount = state.mistakeCount,
                alpha = xpCardAlpha.value,
                offsetY = xpCardOffsetY.value,
                glowAlpha = glowAlpha,
                shineProgress = shineProgress,
                modifier = Modifier.fillMaxWidth()
            )

            Spacer(Modifier.weight(1f))

            // 6. Nút CTA
            SummaryCtaButton(
                text = "Tiếp tục học →",
                onClick = {
                    if (completion != null || hasNextWord) continuePath()
                    else if (ready) complete()
                    else resume()
                },
                enabled = enabled,
                alpha = ctaAlpha.value,
                offsetY = ctaOffsetY.value,
                modifier = Modifier.fillMaxWidth()
            )

            if (completion?.status == "COMPLETED" && replay != null) {
                TextButton(
                    onClick = replay,
                    enabled = enabled,
                    modifier = Modifier.padding(top = 2.dp)
                ) {
                    Text(
                        text = stringResource(R.string.roadmap_replay),
                        color = Color(0xFF0F5533),
                        fontSize = 13.sp,
                        fontWeight = FontWeight.Medium
                    )
                }
            }

            Spacer(Modifier.height(6.dp))
        }
    }
}

/**
 * Sunburst rays rotating 360° every 20s behind the mascot.
 */
@Composable
private fun SunburstBackground(modifier: Modifier = Modifier) {
    val sunburstTransition = rememberInfiniteTransition(label = "SunburstSpin")
    val rotation by sunburstTransition.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 20000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "SunburstAngle"
    )

    Canvas(
        modifier = modifier.graphicsLayer { rotationZ = rotation }
    ) {
        val cx = size.width / 2f
        val cy = size.height / 2f
        val maxRadius = size.minDimension / 2f
        val rayCount = 16
        val angleStep = 360f / rayCount
        val raySpan = angleStep * 0.5f

        val radialBrush = Brush.radialGradient(
            colors = listOf(
                Color.White.copy(alpha = 0.08f),
                Color.White.copy(alpha = 0.05f),
                Color.Transparent
            ),
            center = Offset(cx, cy),
            radius = maxRadius
        )

        for (i in 0 until rayCount) {
            val startAngle = i * angleStep
            val path = Path().apply {
                moveTo(cx, cy)
                val rad1 = Math.toRadians((startAngle - raySpan / 2f).toDouble())
                val rad2 = Math.toRadians((startAngle + raySpan / 2f).toDouble())
                lineTo((cx + maxRadius * cos(rad1)).toFloat(), (cy + maxRadius * sin(rad1)).toFloat())
                lineTo((cx + maxRadius * cos(rad2)).toFloat(), (cy + maxRadius * sin(rad2)).toFloat())
                close()
            }
            drawPath(path, brush = radialBrush)
        }
    }
}

/**
 * Falling confetti with 12 particles (8x12dp), colors #ffd54a / #ff7a7a / #7ad7ff / white.
 */
private data class ConfettiSpec(
    val xFraction: Float,
    val delayMs: Int,
    val durationMs: Int,
    val color: Color,
    val initialRotation: Float,
    val rotationSpeed: Float,
    val swayAmountDp: Float
)

private val ConfettiSpecs = listOf(
    ConfettiSpec(0.08f, 0, 2700, Color(0xFFFFD54A), 15f, 2.5f, 16f),
    ConfettiSpec(0.18f, 400, 3100, Color(0xFFFF7A7A), 45f, -2.0f, 20f),
    ConfettiSpec(0.28f, 900, 2800, Color(0xFF7AD7FF), 80f, 3.0f, 14f),
    ConfettiSpec(0.38f, 200, 3400, Color.White, 30f, -1.8f, 24f),
    ConfettiSpec(0.50f, 700, 2700, Color(0xFFFFD54A), 110f, 2.2f, 18f),
    ConfettiSpec(0.60f, 1200, 3200, Color(0xFFFF7A7A), 60f, -2.5f, 15f),
    ConfettiSpec(0.70f, 300, 2900, Color(0xFF7AD7FF), 95f, 2.8f, 22f),
    ConfettiSpec(0.82f, 800, 3300, Color.White, 40f, -2.2f, 16f),
    ConfettiSpec(0.92f, 150, 2750, Color(0xFFFFD54A), 130f, 3.2f, 20f),
    ConfettiSpec(0.14f, 1400, 3000, Color(0xFF7AD7FF), 70f, -2.0f, 18f),
    ConfettiSpec(0.44f, 1100, 2950, Color(0xFFFF7A7A), 25f, 2.4f, 25f),
    ConfettiSpec(0.76f, 1600, 3150, Color(0xFFFFD54A), 85f, -2.7f, 19f)
)

@Composable
private fun ConfettiRain(modifier: Modifier = Modifier) {
    val confettiTransition = rememberInfiniteTransition(label = "ConfettiLoop")
    val animTime by confettiTransition.animateFloat(
        initialValue = 0f,
        targetValue = 60000f,
        animationSpec = infiniteRepeatable(
            animation = tween(60000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "ConfettiTime"
    )

    Canvas(modifier = modifier) {
        val totalHeight = size.height + 40.dp.toPx()
        val totalWidth = size.width

        for (spec in ConfettiSpecs) {
            val elapsed = animTime + spec.delayMs
            val progress = (elapsed % spec.durationMs) / spec.durationMs.toFloat()
            val y = -20.dp.toPx() + progress * totalHeight
            val sway = sin(progress * 2 * PI.toFloat() * 2) * spec.swayAmountDp.dp.toPx()
            val x = (totalWidth * spec.xFraction) + sway
            val rotation = spec.initialRotation + (progress * 360f * spec.rotationSpeed)

            rotate(degrees = rotation, pivot = Offset(x, y)) {
                drawRoundRect(
                    color = spec.color,
                    topLeft = Offset(x - 4.dp.toPx(), y - 6.dp.toPx()),
                    size = Size(8.dp.toPx(), 12.dp.toPx()),
                    cornerRadius = androidx.compose.ui.geometry.CornerRadius(2.dp.toPx(), 2.dp.toPx())
                )
            }
        }
    }
}

/**
 * Gold header ribbon: gradient #ffd54a -> #f5a623, bottom shadow 4dp #c47a1a.
 */
@Composable
private fun SummaryRibbon(
    scale: Float,
    offsetY: Float,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .graphicsLayer {
                scaleX = scale
                scaleY = scale
                translationY = offsetY
            }
    ) {
        // Bottom shadow 4dp #c47a1a
        Box(
            modifier = Modifier
                .matchParentSize()
                .offset(y = 4.dp)
                .background(Color(0xFFC47A1A), RoundedCornerShape(10.dp))
        )
        // Ribbon front
        Box(
            modifier = Modifier
                .background(
                    Brush.horizontalGradient(
                        listOf(Color(0xFFFFD54A), Color(0xFFF5A623))
                    ),
                    RoundedCornerShape(10.dp)
                )
                .padding(horizontal = 32.dp, vertical = 9.dp),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = "Hoàn thành!",
                fontSize = 20.sp,
                fontWeight = FontWeight.Medium,
                color = Color(0xFF5A3300)
            )
        }
    }
}

/**
 * Row of 3 rating stars: Center star 50dp, side stars 40dp tilted +-12°.
 */
@Composable
private fun StarRatingRow(
    starCount: Int,
    star1Scale: Float,
    star1Rot: Float,
    star2Scale: Float,
    star2Rot: Float,
    star3Scale: Float,
    star3Rot: Float,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier,
        horizontalArrangement = Arrangement.spacedBy(14.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        // Star 1 (Left): 40dp, tilted -12°
        StarCanvas(
            size = 40.dp,
            achieved = starCount >= 1,
            scale = star1Scale,
            rotationZ = star1Rot - 12f * star1Scale
        )
        // Star 2 (Center): 50dp, upright
        StarCanvas(
            size = 50.dp,
            achieved = starCount >= 2,
            scale = star2Scale,
            rotationZ = star2Rot
        )
        // Star 3 (Right): 40dp, tilted +12°
        StarCanvas(
            size = 40.dp,
            achieved = starCount >= 3,
            scale = star3Scale,
            rotationZ = star3Rot + 12f * star3Scale
        )
    }
}

@Composable
private fun StarCanvas(
    size: Dp,
    achieved: Boolean,
    scale: Float,
    rotationZ: Float,
    modifier: Modifier = Modifier
) {
    val fillColor = if (achieved) Color(0xFFFFD54A) else Color(0xFFE6E2D6)
    val strokeColor = if (achieved) Color(0xFFC47A1A) else Color(0xFFB4B2A9)

    Canvas(
        modifier = modifier
            .size(size)
            .graphicsLayer {
                scaleX = scale
                scaleY = scale
                this.rotationZ = rotationZ
            }
    ) {
        val cx = this.size.width / 2f
        val cy = this.size.height / 2f
        val outerR = this.size.minDimension / 2f - 2.dp.toPx()
        val innerR = outerR * 0.42f

        val starPath = Path()
        for (i in 0 until 10) {
            val angle = Math.toRadians((i * 36 - 90).toDouble())
            val r = if (i % 2 == 0) outerR else innerR
            val x = (cx + r * cos(angle)).toFloat()
            val y = (cy + r * sin(angle)).toFloat()
            if (i == 0) starPath.moveTo(x, y) else starPath.lineTo(x, y)
        }
        starPath.close()

        drawPath(starPath, fillColor, style = Fill)
        drawPath(
            starPath,
            strokeColor,
            style = Stroke(width = 2.dp.toPx(), join = StrokeJoin.Round)
        )
    }
}

/**
 * Three wooden signs hanging from a horizontal rope.
 */
@Composable
private fun HangingWoodenSignsRow(
    sign1Drop: Float,
    sign2Drop: Float,
    sign3Drop: Float,
    sway1: Float,
    sway2: Float,
    sway3: Float,
    timeString: String,
    accuracyString: String,
    scoreString: String,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier.fillMaxWidth(),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // Horizontal rope: height 6dp, twisted texture #8a5a2b / #a8743a
        Canvas(
            modifier = Modifier
                .fillMaxWidth()
                .height(6.dp)
        ) {
            val w = size.width
            val h = size.height
            drawRoundRect(
                color = Color(0xFF8A5A2B),
                cornerRadius = androidx.compose.ui.geometry.CornerRadius(h / 2, h / 2)
            )
            val step = 9.dp.toPx()
            var x = 0f
            while (x < w) {
                drawLine(
                    color = Color(0xFFA8743A),
                    start = Offset(x, h * 0.15f),
                    end = Offset(x + 5.dp.toPx(), h * 0.85f),
                    strokeWidth = 2.dp.toPx(),
                    cap = StrokeCap.Round
                )
                x += step
            }
        }

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            // Sign 1: Clock / Time
            HangingWoodenSign(
                dropOffsetY = sign1Drop,
                swayAngle = sway1,
                iconKind = SignIconKind.Clock,
                value = timeString,
                label = "Thời gian",
                modifier = Modifier.weight(1f)
            )
            // Sign 2: Target / Accuracy
            HangingWoodenSign(
                dropOffsetY = sign2Drop,
                swayAngle = sway2,
                iconKind = SignIconKind.Bullseye,
                value = accuracyString,
                label = "Chính xác",
                modifier = Modifier.weight(1f)
            )
            // Sign 3: Check / Correct
            HangingWoodenSign(
                dropOffsetY = sign3Drop,
                swayAngle = sway3,
                iconKind = SignIconKind.Check,
                value = scoreString,
                label = "Câu đúng",
                modifier = Modifier.weight(1f)
            )
        }
    }
}

private enum class SignIconKind { Clock, Bullseye, Check }

@Composable
private fun HangingWoodenSign(
    dropOffsetY: Float,
    swayAngle: Float,
    iconKind: SignIconKind,
    value: String,
    label: String,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .graphicsLayer {
                transformOrigin = TransformOrigin(0.5f, 0f)
                translationY = dropOffsetY
                rotationZ = swayAngle
            },
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // 2 hanging cords from rope down to the 2 nails on the board
        Canvas(
            modifier = Modifier
                .fillMaxWidth()
                .height(13.dp)
        ) {
            val w = size.width
            val h = size.height
            val cord1X = w * 0.22f
            val cord2X = w * 0.78f
            val cordColor = Color(0xFF8A5A2B)
            val cordStroke = 1.6.dp.toPx()
            drawLine(cordColor, Offset(cord1X, 0f), Offset(cord1X, h), strokeWidth = cordStroke, cap = StrokeCap.Round)
            drawLine(cordColor, Offset(cord2X, 0f), Offset(cord2X, h), strokeWidth = cordStroke, cap = StrokeCap.Round)
        }

        // Wooden board
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(66.dp)
        ) {
            // Bottom shadow 4dp #6b4423
            Box(
                modifier = Modifier
                    .matchParentSize()
                    .offset(y = 4.dp)
                    .background(Color(0xFF6B4423), RoundedCornerShape(12.dp))
            )
            // Board body: gradient #d9a566 -> #c48a47, border 2dp #8a5a2b, corner 12dp
            Box(
                modifier = Modifier
                    .matchParentSize()
                    .background(
                        Brush.verticalGradient(
                            listOf(Color(0xFFD9A566), Color(0xFFC48A47))
                        ),
                        RoundedCornerShape(12.dp)
                    )
                    .border(2.dp, Color(0xFF8A5A2B), RoundedCornerShape(12.dp))
                    .padding(horizontal = 4.dp, vertical = 5.dp),
                contentAlignment = Alignment.Center
            ) {
                // Two rivet nails at top corners
                Canvas(modifier = Modifier.fillMaxSize()) {
                    val w = size.width
                    val nailR = 2.4.dp.toPx()
                    val nailY = 5.dp.toPx()
                    val nail1X = w * 0.22f
                    val nail2X = w * 0.78f

                    // Nail 1
                    drawCircle(Color(0xFF4A2A0C), radius = nailR, center = Offset(nail1X, nailY))
                    drawCircle(Color(0xFF8A5A2B), radius = nailR * 0.5f, center = Offset(nail1X - 0.7.dp.toPx(), nailY - 0.7.dp.toPx()))

                    // Nail 2
                    drawCircle(Color(0xFF4A2A0C), radius = nailR, center = Offset(nail2X, nailY))
                    drawCircle(Color(0xFF8A5A2B), radius = nailR * 0.5f, center = Offset(nail2X - 0.7.dp.toPx(), nailY - 0.7.dp.toPx()))
                }

                // Inner content: Icon, Value, Label
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center
                ) {
                    SignVectorIcon(iconKind)
                    Spacer(Modifier.height(1.dp))
                    Text(
                        text = value,
                        fontSize = 19.sp,
                        fontWeight = FontWeight.Medium,
                        color = Color(0xFF3B2410),
                        maxLines = 1
                    )
                    Text(
                        text = label,
                        fontSize = 10.sp,
                        fontWeight = FontWeight.Medium,
                        color = Color(0xFF6B4423),
                        maxLines = 1
                    )
                }
            }
        }
    }
}

@Composable
private fun SignVectorIcon(kind: SignIconKind) {
    Canvas(modifier = Modifier.size(15.dp)) {
        val w = size.width
        val h = size.height
        val cx = w / 2f
        val cy = h / 2f
        val color = Color(0xFF3B2410)

        when (kind) {
            SignIconKind.Clock -> {
                drawCircle(color, radius = cx - 1.dp.toPx(), style = Stroke(width = 1.4.dp.toPx()))
                drawCircle(color, radius = 1.2.dp.toPx(), center = Offset(cx, cy))
                drawLine(color, Offset(cx, cy), Offset(cx, cy - 4.dp.toPx()), strokeWidth = 1.4.dp.toPx(), cap = StrokeCap.Round)
                drawLine(color, Offset(cx, cy), Offset(cx + 3.2.dp.toPx(), cy - 1.dp.toPx()), strokeWidth = 1.4.dp.toPx(), cap = StrokeCap.Round)
            }
            SignIconKind.Bullseye -> {
                drawCircle(color, radius = cx - 1.dp.toPx(), style = Stroke(width = 1.3.dp.toPx()))
                drawCircle(color, radius = (cx - 1.dp.toPx()) * 0.55f, style = Stroke(width = 1.1.dp.toPx()))
                drawCircle(color, radius = 1.8.dp.toPx(), center = Offset(cx, cy), style = Fill)
            }
            SignIconKind.Check -> {
                val checkPath = Path().apply {
                    moveTo(w * 0.22f, h * 0.52f)
                    lineTo(w * 0.44f, h * 0.74f)
                    lineTo(w * 0.80f, h * 0.28f)
                }
                drawPath(checkPath, color, style = Stroke(width = 1.8.dp.toPx(), cap = StrokeCap.Round, join = StrokeJoin.Round))
            }
        }
    }
}

/**
 * XP Card: gradient white -> #fff7dc, border 3dp #f5a623, bo 18dp, bottom shadow 5dp #c47a1a.
 */
@Composable
private fun XpCard(
    xp: Int,
    mistakeCount: Int,
    alpha: Float,
    offsetY: Float,
    glowAlpha: Float,
    shineProgress: Float,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .graphicsLayer {
                this.alpha = alpha
                translationY = offsetY
            }
    ) {
        // Bottom shadow 5dp #c47a1a
        Box(
            modifier = Modifier
                .matchParentSize()
                .offset(y = 5.dp)
                .background(Color(0xFFC47A1A), RoundedCornerShape(18.dp))
        )
        // Card body with shine and glow border
        Box(
            modifier = Modifier
                .matchParentSize()
                .background(
                    Brush.verticalGradient(
                        listOf(Color.White, Color(0xFFFFF7DC))
                    ),
                    RoundedCornerShape(18.dp)
                )
                .border(
                    3.dp,
                    Color(0xFFF5A623).copy(alpha = glowAlpha),
                    RoundedCornerShape(18.dp)
                )
                .clip(RoundedCornerShape(18.dp))
        ) {
            // Diagonal shine sweep
            Canvas(modifier = Modifier.fillMaxSize()) {
                val w = size.width
                val h = size.height
                val shineX = shineProgress * (w + h)
                val shineBrush = Brush.linearGradient(
                    colors = listOf(
                        Color.Transparent,
                        Color.White.copy(alpha = 0.45f),
                        Color.Transparent
                    ),
                    start = Offset(shineX - 45.dp.toPx(), 0f),
                    end = Offset(shineX + 45.dp.toPx(), h)
                )
                drawRect(brush = shineBrush)
            }
        }

        // Inner text
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 20.dp, vertical = 11.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Text(
                text = "KINH NGHIỆM NHẬN ĐƯỢC",
                fontSize = 11.sp,
                letterSpacing = 0.08.em,
                fontWeight = FontWeight.Medium,
                color = Color(0xFF8A5A2B)
            )
            Spacer(Modifier.height(3.dp))
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                LightningIcon(modifier = Modifier.size(22.dp, 28.dp))
                Text(
                    text = "+$xp XP",
                    fontSize = 34.sp,
                    fontWeight = FontWeight.Medium,
                    color = Color(0xFFC47A1A)
                )
            }
            Spacer(Modifier.height(3.dp))
            Text(
                text = if (mistakeCount > 0) {
                    "$mistakeCount lỗi sai · −${mistakeCount * 10}% XP"
                } else {
                    "Hoàn hảo! Nhận đủ XP"
                },
                fontSize = 11.sp,
                color = Color(0xFF8A5A2B)
            )
        }
    }
}

@Composable
private fun LightningIcon(modifier: Modifier = Modifier) {
    Canvas(modifier = modifier) {
        val w = size.width
        val h = size.height
        val lightningPath = Path().apply {
            moveTo(w * 0.58f, 0f)
            lineTo(w * 0.16f, h * 0.54f)
            lineTo(w * 0.52f, h * 0.54f)
            lineTo(w * 0.38f, h)
            lineTo(w * 0.84f, h * 0.44f)
            lineTo(w * 0.48f, h * 0.44f)
            close()
        }
        drawPath(lightningPath, Color(0xFFC47A1A), style = Fill)
    }
}

/**
 * Primary 3D CTA Button: height 52dp, radius 16dp, bottom shadow 5dp #0f5533, translateY 4dp on press.
 */
@Composable
private fun SummaryCtaButton(
    text: String,
    onClick: () -> Unit,
    enabled: Boolean,
    alpha: Float,
    offsetY: Float,
    modifier: Modifier = Modifier
) {
    val interactionSource = remember { MutableInteractionSource() }
    val isPressed by interactionSource.collectIsPressedAsState()
    val pressOffsetY = if (isPressed) 4.dp else 0.dp
    val shadowHeight = if (isPressed) 1.dp else 5.dp

    Box(
        modifier = modifier
            .graphicsLayer {
                this.alpha = alpha
                translationY = offsetY
            }
            .fillMaxWidth()
            .height(57.dp)
    ) {
        // Bottom 3D shadow 5dp #0f5533
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(52.dp)
                .offset(y = shadowHeight)
                .background(Color(0xFF0F5533), RoundedCornerShape(16.dp))
        )
        // Button body
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(52.dp)
                .offset(y = pressOffsetY)
                .clip(RoundedCornerShape(16.dp))
                .background(if (enabled) Primary else Primary.copy(alpha = 0.5f))
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
                fontSize = 16.sp,
                fontWeight = FontWeight.Medium,
                color = Color.White
            )
        }
    }
}
