package com.example.chineselearningapp.core.designsystem

import androidx.compose.animation.Crossfade
import androidx.compose.animation.core.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Fill
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

// Tiger Color Palette
private val FurOrange = Color(0xFFF5A623)
private val BellyCream = Color(0xFFFCE8C0)
private val InnerEarPink = Color(0xFFF9C0B0)
private val NoseOrange = Color(0xFFE8864A)
private val TigerStripe = Color(0xFFC47A1A)
private val EyeBlack = Color(0xFF1A1A18)
private val PawPadColor = Color(0xFFC47A1A)
private val WhiskerColor = Color(0x66C47A1A)
private val MouthColor = Color(0xFF8B4513)

enum class TigerVariant {
    Normal,
    Celebrate,
    Encourage,
    Happy,
    Sad
}

/**
 * Pure Canvas Tiger Mascot avatar.
 * Size: 54dp x 66dp
 * Idle animation: sway -3° ↔ +3°, translateY 0 ↔ -3dp, cycle 3s (EaseInOut).
 */
@Composable
fun TigerCanvas(
    modifier: Modifier = Modifier,
    variant: TigerVariant = TigerVariant.Normal,
    animateIdle: Boolean = true,
    width: Dp = 54.dp,
    height: Dp = 66.dp
) {
    val infiniteTransition = rememberInfiniteTransition(label = "TigerIdle")
    val idleRotation by infiniteTransition.animateFloat(
        initialValue = -3f,
        targetValue = 3f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 1500, easing = EaseInOut),
            repeatMode = RepeatMode.Reverse
        ),
        label = "TigerRotation"
    )
    val idleTranslateY by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = -3f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 1500, easing = EaseInOut),
            repeatMode = RepeatMode.Reverse
        ),
        label = "TigerTranslateY"
    )
    val rotation = if (animateIdle) idleRotation else 0f
    val translateY = if (animateIdle) idleTranslateY else 0f

    Canvas(
        modifier = modifier
            .size(width = width, height = height)
            .graphicsLayer {
                rotationZ = rotation
                translationY = translateY.dp.toPx()
            }
    ) {
        val w = size.width
        val h = size.height

        // 1. Tail (curving out behind to the left)
        val tailPath = Path().apply {
            moveTo(w * 0.22f, h * 0.78f)
            cubicTo(
                w * 0.02f, h * 0.82f,
                w * 0.00f, h * 0.60f,
                w * 0.08f, h * 0.52f
            )
        }
        drawPath(
            path = tailPath,
            color = FurOrange,
            style = Stroke(width = 4.5.dp.toPx(), cap = StrokeCap.Round)
        )
        // Tail tip / stripe
        drawCircle(
            color = TigerStripe,
            radius = 2.dp.toPx(),
            center = Offset(w * 0.08f, h * 0.52f)
        )

        // 2. Ears (triangles with inner pink)
        // Left Ear
        val leftEarOuter = Path().apply {
            moveTo(w * 0.16f, h * 0.24f)
            lineTo(w * 0.22f, h * 0.05f)
            lineTo(w * 0.38f, h * 0.18f)
            close()
        }
        drawPath(leftEarOuter, FurOrange, style = Fill)
        val leftEarInner = Path().apply {
            moveTo(w * 0.20f, h * 0.21f)
            lineTo(w * 0.24f, h * 0.09f)
            lineTo(w * 0.34f, h * 0.18f)
            close()
        }
        drawPath(leftEarInner, InnerEarPink, style = Fill)

        // Right Ear
        val rightEarOuter = Path().apply {
            moveTo(w * 0.62f, h * 0.18f)
            lineTo(w * 0.78f, h * 0.05f)
            lineTo(w * 0.84f, h * 0.24f)
            close()
        }
        drawPath(rightEarOuter, FurOrange, style = Fill)
        val rightEarInner = Path().apply {
            moveTo(w * 0.66f, h * 0.18f)
            lineTo(w * 0.76f, h * 0.09f)
            lineTo(w * 0.80f, h * 0.21f)
            close()
        }
        drawPath(rightEarInner, InnerEarPink, style = Fill)

        // 3. Plump Body (oval)
        val bodyWidth = w * 0.76f
        val bodyHeight = h * 0.48f
        drawOval(
            color = FurOrange,
            topLeft = Offset((w - bodyWidth) / 2f, h * 0.44f),
            size = Size(bodyWidth, bodyHeight)
        )

        // 4. Cream Belly
        val bellyWidth = w * 0.52f
        val bellyHeight = h * 0.34f
        drawOval(
            color = BellyCream,
            topLeft = Offset((w - bellyWidth) / 2f, h * 0.52f),
            size = Size(bellyWidth, bellyHeight)
        )

        // 5. Body Stripes (sides)
        val leftBodyStripe = Path().apply {
            moveTo(w * 0.16f, h * 0.60f)
            quadraticTo(w * 0.24f, h * 0.61f, w * 0.28f, h * 0.63f)
        }
        drawPath(leftBodyStripe, TigerStripe, style = Stroke(width = 2.dp.toPx(), cap = StrokeCap.Round))
        val rightBodyStripe = Path().apply {
            moveTo(w * 0.84f, h * 0.60f)
            quadraticTo(w * 0.76f, h * 0.61f, w * 0.72f, h * 0.63f)
        }
        drawPath(rightBodyStripe, TigerStripe, style = Stroke(width = 2.dp.toPx(), cap = StrokeCap.Round))

        // 6. Short Rounded Paws with Darker Paw Pads
        when (variant) {
            TigerVariant.Normal, TigerVariant.Sad -> {
                // Left paw
                drawOval(
                    color = FurOrange,
                    topLeft = Offset(w * 0.22f, h * 0.84f),
                    size = Size(w * 0.22f, h * 0.13f)
                )
                drawOval(
                    color = PawPadColor,
                    topLeft = Offset(w * 0.26f, h * 0.87f),
                    size = Size(w * 0.14f, h * 0.08f)
                )
                // Right paw
                drawOval(
                    color = FurOrange,
                    topLeft = Offset(w * 0.56f, h * 0.84f),
                    size = Size(w * 0.22f, h * 0.13f)
                )
                drawOval(
                    color = PawPadColor,
                    topLeft = Offset(w * 0.60f, h * 0.87f),
                    size = Size(w * 0.14f, h * 0.08f)
                )
            }
            TigerVariant.Celebrate, TigerVariant.Happy -> {
                // Hind feet at bottom
                drawOval(
                    color = FurOrange,
                    topLeft = Offset(w * 0.22f, h * 0.84f),
                    size = Size(w * 0.22f, h * 0.13f)
                )
                drawOval(
                    color = PawPadColor,
                    topLeft = Offset(w * 0.26f, h * 0.87f),
                    size = Size(w * 0.14f, h * 0.08f)
                )
                drawOval(
                    color = FurOrange,
                    topLeft = Offset(w * 0.56f, h * 0.84f),
                    size = Size(w * 0.22f, h * 0.13f)
                )
                drawOval(
                    color = PawPadColor,
                    topLeft = Offset(w * 0.60f, h * 0.87f),
                    size = Size(w * 0.14f, h * 0.08f)
                )
                // Hai tay giơ cao (raised front paws cheering!)
                drawOval(
                    color = FurOrange,
                    topLeft = Offset(w * 0.08f, h * 0.18f),
                    size = Size(w * 0.20f, h * 0.16f)
                )
                drawOval(
                    color = PawPadColor,
                    topLeft = Offset(w * 0.11f, h * 0.21f),
                    size = Size(w * 0.13f, h * 0.10f)
                )
                drawOval(
                    color = FurOrange,
                    topLeft = Offset(w * 0.72f, h * 0.18f),
                    size = Size(w * 0.20f, h * 0.16f)
                )
                drawOval(
                    color = PawPadColor,
                    topLeft = Offset(w * 0.76f, h * 0.21f),
                    size = Size(w * 0.13f, h * 0.10f)
                )
            }
            TigerVariant.Encourage -> {
                // Hind feet at bottom
                drawOval(
                    color = FurOrange,
                    topLeft = Offset(w * 0.22f, h * 0.84f),
                    size = Size(w * 0.22f, h * 0.13f)
                )
                drawOval(
                    color = PawPadColor,
                    topLeft = Offset(w * 0.26f, h * 0.87f),
                    size = Size(w * 0.14f, h * 0.08f)
                )
                drawOval(
                    color = FurOrange,
                    topLeft = Offset(w * 0.56f, h * 0.84f),
                    size = Size(w * 0.22f, h * 0.13f)
                )
                drawOval(
                    color = PawPadColor,
                    topLeft = Offset(w * 0.60f, h * 0.87f),
                    size = Size(w * 0.14f, h * 0.08f)
                )
                // Tay chống hông (hands on hips)
                drawOval(
                    color = FurOrange,
                    topLeft = Offset(w * 0.12f, h * 0.55f),
                    size = Size(w * 0.18f, h * 0.14f)
                )
                drawOval(
                    color = PawPadColor,
                    topLeft = Offset(w * 0.15f, h * 0.58f),
                    size = Size(w * 0.11f, h * 0.08f)
                )
                drawOval(
                    color = FurOrange,
                    topLeft = Offset(w * 0.70f, h * 0.55f),
                    size = Size(w * 0.18f, h * 0.14f)
                )
                drawOval(
                    color = PawPadColor,
                    topLeft = Offset(w * 0.74f, h * 0.58f),
                    size = Size(w * 0.11f, h * 0.08f)
                )
            }
        }

        // 7. Head (Horizontal Oval)
        val headWidth = w * 0.88f
        val headHeight = h * 0.44f
        drawOval(
            color = FurOrange,
            topLeft = Offset((w - headWidth) / 2f, h * 0.12f),
            size = Size(headWidth, headHeight)
        )

        // 8. Stripes on Head & Forehead (King mark 王)
        // Center vertical stripe
        drawLine(
            color = TigerStripe,
            start = Offset(w * 0.5f, h * 0.14f),
            end = Offset(w * 0.5f, h * 0.24f),
            strokeWidth = 2.2.dp.toPx(),
            cap = StrokeCap.Round
        )
        // Top horizontal stripe
        drawLine(
            color = TigerStripe,
            start = Offset(w * 0.42f, h * 0.16f),
            end = Offset(w * 0.58f, h * 0.16f),
            strokeWidth = 1.8.dp.toPx(),
            cap = StrokeCap.Round
        )
        // Middle horizontal stripe
        drawLine(
            color = TigerStripe,
            start = Offset(w * 0.44f, h * 0.20f),
            end = Offset(w * 0.56f, h * 0.20f),
            strokeWidth = 1.8.dp.toPx(),
            cap = StrokeCap.Round
        )
        // Cheek side stripes
        // Left cheek stripes
        drawLine(
            color = TigerStripe,
            start = Offset(w * 0.10f, h * 0.30f),
            end = Offset(w * 0.20f, h * 0.31f),
            strokeWidth = 1.8.dp.toPx(),
            cap = StrokeCap.Round
        )
        drawLine(
            color = TigerStripe,
            start = Offset(w * 0.12f, h * 0.37f),
            end = Offset(w * 0.22f, h * 0.37f),
            strokeWidth = 1.8.dp.toPx(),
            cap = StrokeCap.Round
        )
        // Right cheek stripes
        drawLine(
            color = TigerStripe,
            start = Offset(w * 0.90f, h * 0.30f),
            end = Offset(w * 0.80f, h * 0.31f),
            strokeWidth = 1.8.dp.toPx(),
            cap = StrokeCap.Round
        )
        drawLine(
            color = TigerStripe,
            start = Offset(w * 0.88f, h * 0.37f),
            end = Offset(w * 0.78f, h * 0.37f),
            strokeWidth = 1.8.dp.toPx(),
            cap = StrokeCap.Round
        )

        // 9. Eyes & Cheeks
        if (variant == TigerVariant.Celebrate || variant == TigerVariant.Happy) {
            // Mắt cong cười (^ ^)
            val eyeStroke = Stroke(width = 2.4.dp.toPx(), cap = StrokeCap.Round)
            val leftEyeCurve = Path().apply {
                moveTo(w * 0.26f, h * 0.35f)
                quadraticTo(w * 0.34f, h * 0.27f, w * 0.42f, h * 0.35f)
            }
            drawPath(leftEyeCurve, EyeBlack, style = eyeStroke)
            val rightEyeCurve = Path().apply {
                moveTo(w * 0.58f, h * 0.35f)
                quadraticTo(w * 0.66f, h * 0.27f, w * 0.74f, h * 0.35f)
            }
            drawPath(rightEyeCurve, EyeBlack, style = eyeStroke)

            // Má hồng (blush)
            drawOval(
                color = Color(0xFFFF7A7A).copy(alpha = 0.45f),
                topLeft = Offset(w * 0.16f, h * 0.36f),
                size = Size(w * 0.13f, h * 0.07f)
            )
            drawOval(
                color = Color(0xFFFF7A7A).copy(alpha = 0.45f),
                topLeft = Offset(w * 0.71f, h * 0.36f),
                size = Size(w * 0.13f, h * 0.07f)
            )
        } else if (variant == TigerVariant.Sad) {
            // Lông mày xệ (slanted sad eyebrows)
            drawLine(
                color = TigerStripe,
                start = Offset(w * 0.27f, h * 0.26f),
                end = Offset(w * 0.41f, h * 0.29f),
                strokeWidth = 2.dp.toPx(),
                cap = StrokeCap.Round
            )
            drawLine(
                color = TigerStripe,
                start = Offset(w * 0.73f, h * 0.26f),
                end = Offset(w * 0.59f, h * 0.29f),
                strokeWidth = 2.dp.toPx(),
                cap = StrokeCap.Round
            )
            // Mắt tròn to buồn
            val eyeRadius = w * 0.075f
            val leftEyeCenter = Offset(w * 0.34f, h * 0.34f)
            drawCircle(color = EyeBlack, radius = eyeRadius, center = leftEyeCenter)
            drawCircle(
                color = Color.White,
                radius = eyeRadius * 0.35f,
                center = Offset(leftEyeCenter.x + eyeRadius * 0.25f, leftEyeCenter.y - eyeRadius * 0.25f)
            )

            val rightEyeCenter = Offset(w * 0.66f, h * 0.34f)
            drawCircle(color = EyeBlack, radius = eyeRadius, center = rightEyeCenter)
            drawCircle(
                color = Color.White,
                radius = eyeRadius * 0.35f,
                center = Offset(rightEyeCenter.x + eyeRadius * 0.25f, rightEyeCenter.y - eyeRadius * 0.25f)
            )

            // Giọt nước mắt xanh nhạt rơi bên mắt phải
            val tearColor = Color(0xFF7AD7FF)
            val tearPath = Path().apply {
                moveTo(w * 0.76f, h * 0.37f)
                cubicTo(
                    w * 0.79f, h * 0.41f,
                    w * 0.81f, h * 0.44f,
                    w * 0.77f, h * 0.46f
                )
                cubicTo(
                    w * 0.73f, h * 0.46f,
                    w * 0.74f, h * 0.41f,
                    w * 0.76f, h * 0.37f
                )
                close()
            }
            drawPath(tearPath, tearColor, style = Fill)
        } else {
            // Big Cute Eyes with Highlights (Normal & Encourage)
            val eyeRadius = w * 0.082f
            // Left Eye
            val leftEyeCenter = Offset(w * 0.34f, h * 0.33f)
            drawCircle(color = EyeBlack, radius = eyeRadius, center = leftEyeCenter)
            drawCircle(
                color = Color.White,
                radius = eyeRadius * 0.42f,
                center = Offset(leftEyeCenter.x + eyeRadius * 0.28f, leftEyeCenter.y - eyeRadius * 0.28f)
            )
            drawCircle(
                color = Color.White,
                radius = eyeRadius * 0.20f,
                center = Offset(leftEyeCenter.x - eyeRadius * 0.32f, leftEyeCenter.y + eyeRadius * 0.30f)
            )

            // Right Eye
            val rightEyeCenter = Offset(w * 0.66f, h * 0.33f)
            drawCircle(color = EyeBlack, radius = eyeRadius, center = rightEyeCenter)
            drawCircle(
                color = Color.White,
                radius = eyeRadius * 0.42f,
                center = Offset(rightEyeCenter.x + eyeRadius * 0.28f, rightEyeCenter.y - eyeRadius * 0.28f)
            )
            drawCircle(
                color = Color.White,
                radius = eyeRadius * 0.20f,
                center = Offset(rightEyeCenter.x - eyeRadius * 0.32f, rightEyeCenter.y + eyeRadius * 0.30f)
            )
        }

        // 10. Small Oval Nose (#e8864a)
        drawOval(
            color = NoseOrange,
            topLeft = Offset(w * 0.45f, h * 0.38f),
            size = Size(w * 0.10f, h * 0.055f)
        )

        // 11. Mouth
        when (variant) {
            TigerVariant.Celebrate, TigerVariant.Happy -> {
                // Miệng há (open happy mouth)
                val openMouthPath = Path().apply {
                    moveTo(w * 0.43f, h * 0.43f)
                    quadraticTo(w * 0.50f, h * 0.45f, w * 0.57f, h * 0.43f)
                    quadraticTo(w * 0.50f, h * 0.53f, w * 0.43f, h * 0.43f)
                    close()
                }
                drawPath(openMouthPath, Color(0xFF8B2500), style = Fill)
                // Cute Tongue
                val tonguePath = Path().apply {
                    moveTo(w * 0.46f, h * 0.48f)
                    quadraticTo(w * 0.50f, h * 0.46f, w * 0.54f, h * 0.48f)
                    quadraticTo(w * 0.50f, h * 0.53f, w * 0.46f, h * 0.48f)
                    close()
                }
                drawPath(tonguePath, Color(0xFFFF8B8B), style = Fill)
                drawPath(openMouthPath, MouthColor, style = Stroke(width = 1.4.dp.toPx(), cap = StrokeCap.Round))
            }
            TigerVariant.Sad -> {
                // Miệng mếu (frowning mouth)
                val sadMouthPath = Path().apply {
                    moveTo(w * 0.43f, h * 0.47f)
                    quadraticTo(w * 0.50f, h * 0.43f, w * 0.57f, h * 0.47f)
                }
                drawPath(sadMouthPath, MouthColor, style = Stroke(width = 1.8.dp.toPx(), cap = StrokeCap.Round))
            }
            TigerVariant.Encourage -> {
                // Miệng cười nhẹ (gentle smile)
                val smilePath = Path().apply {
                    moveTo(w * 0.43f, h * 0.44f)
                    quadraticTo(w * 0.50f, h * 0.48f, w * 0.57f, h * 0.44f)
                }
                drawPath(smilePath, MouthColor, style = Stroke(width = 1.6.dp.toPx(), cap = StrokeCap.Round))
            }
            TigerVariant.Normal -> {
                // W-shaped Smiling Mouth
                val mouthPath = Path().apply {
                    moveTo(w * 0.43f, h * 0.44f)
                    quadraticTo(w * 0.465f, h * 0.475f, w * 0.50f, h * 0.445f)
                    quadraticTo(w * 0.535f, h * 0.475f, w * 0.57f, h * 0.44f)
                }
                drawPath(
                    path = mouthPath,
                    color = MouthColor,
                    style = Stroke(width = 1.4.dp.toPx(), cap = StrokeCap.Round)
                )
            }
        }

        // 12. Faint Whiskers on Both Sides
        // Left whiskers
        drawLine(
            color = WhiskerColor,
            start = Offset(w * 0.22f, h * 0.40f),
            end = Offset(w * 0.04f, h * 0.38f),
            strokeWidth = 0.8.dp.toPx(),
            cap = StrokeCap.Round
        )
        drawLine(
            color = WhiskerColor,
            start = Offset(w * 0.22f, h * 0.43f),
            end = Offset(w * 0.05f, h * 0.45f),
            strokeWidth = 0.8.dp.toPx(),
            cap = StrokeCap.Round
        )
        // Right whiskers
        drawLine(
            color = WhiskerColor,
            start = Offset(w * 0.78f, h * 0.40f),
            end = Offset(w * 0.96f, h * 0.38f),
            strokeWidth = 0.8.dp.toPx(),
            cap = StrokeCap.Round
        )
        drawLine(
            color = WhiskerColor,
            start = Offset(w * 0.78f, h * 0.43f),
            end = Offset(w * 0.95f, h * 0.45f),
            strokeWidth = 0.8.dp.toPx(),
            cap = StrokeCap.Round
        )
    }
}

/**
 * TigerMascot composable:
 * Layout: Row [TigerCanvas 54x66dp] + [bubble chat rounded 12 12 12 4dp, bg Surface2, border 0.5dp Border, text 13sp]
 */
@Composable
fun TigerMascot(
    message: String,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(10.dp)
    ) {
        TigerCanvas()
        Surface(
            modifier = Modifier.weight(1f),
            shape = RoundedCornerShape(
                topStart = 12.dp,
                topEnd = 12.dp,
                bottomEnd = 12.dp,
                bottomStart = 4.dp
            ),
            color = Surface2,
            border = BorderStroke(0.5.dp, Border),
            shadowElevation = 1.dp
        ) {
            Crossfade(
                targetState = message,
                animationSpec = tween(200),
                label = "tiger mascot message"
            ) { text ->
                Text(
                    text = text,
                    modifier = Modifier.padding(horizontal = 14.dp, vertical = 10.dp),
                    fontSize = 13.sp,
                    lineHeight = 18.sp,
                    color = TextPrimary
                )
            }
        }
    }
}

