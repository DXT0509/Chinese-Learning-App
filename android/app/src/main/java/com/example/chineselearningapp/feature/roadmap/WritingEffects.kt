package com.example.chineselearningapp.feature.roadmap

import android.annotation.SuppressLint
import android.content.Context
import android.media.AudioManager
import android.media.ToneGenerator
import android.os.Build
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.rotate
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlin.math.cos
import kotlin.math.sin
import kotlin.random.Random

/**
 * Haptic and Sound feedback helper for Writing scene results.
 */
class WritingFeedbackPlayer(private val context: Context, private val volumeSupplier: () -> Float) {
    private val vibrator: Vibrator? = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
        val manager = context.getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as? VibratorManager
        manager?.defaultVibrator
    } else {
        @Suppress("DEPRECATION")
        context.getSystemService(Context.VIBRATOR_SERVICE) as? Vibrator
    }

    private var toneGen: ToneGenerator? = try {
        ToneGenerator(AudioManager.STREAM_MUSIC, 100)
    } catch (_: Exception) {
        null
    }

    @SuppressLint("MissingPermission")
    fun playCorrect() {
        val vol = volumeSupplier()
        // Haptic: 2 short pulses (20ms on, 40ms off, 20ms on)
        if (vibrator?.hasVibrator() == true) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                val timings = longArrayOf(0, 20, 40, 20)
                val amplitudes = intArrayOf(0, 180, 0, 220)
                vibrator.vibrate(VibrationEffect.createWaveform(timings, amplitudes, -1))
            } else {
                @Suppress("DEPRECATION")
                vibrator.vibrate(longArrayOf(0, 20, 40, 20), -1)
            }
        }
        // Sound: upbeat "ting" respecting volume
        if (vol > 0.05f) {
            try {
                toneGen?.startTone(ToneGenerator.TONE_PROP_PROMPT, (150 * vol).toInt().coerceAtLeast(40))
            } catch (_: Exception) {}
        }
    }

    @SuppressLint("MissingPermission")
    fun playIncorrect() {
        val vol = volumeSupplier()
        // Haptic: 1 strong pulse 60ms
        if (vibrator?.hasVibrator() == true) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                vibrator.vibrate(VibrationEffect.createOneShot(60, VibrationEffect.DEFAULT_AMPLITUDE))
            } else {
                @Suppress("DEPRECATION")
                vibrator.vibrate(60)
            }
        }
        // Sound: gentle non-jarring "buzz"
        if (vol > 0.05f) {
            try {
                toneGen?.startTone(ToneGenerator.TONE_PROP_BEEP2, (120 * vol).toInt().coerceAtLeast(30))
            } catch (_: Exception) {}
        }
    }

    fun release() {
        toneGen?.release()
        toneGen = null
    }
}

@Composable
fun rememberWritingFeedbackPlayer(volumeSupplier: () -> Float): WritingFeedbackPlayer {
    val context = LocalContext.current.applicationContext
    val player = remember(context) { WritingFeedbackPlayer(context, volumeSupplier) }
    DisposableEffect(player) {
        onDispose { player.release() }
    }
    return player
}

/**
 * Confetti particle state.
 * 30-36 small rectangles (9x13dp), colors: #ffd54a, #ff7a7a, #7ad7ff, #34c478, #ffffff, #c9a0ff.
 * Parabolas radiating outward from center, rotating, fading out over 1.4-1.9s.
 */
private data class ConfettiParticle(
    val color: Color,
    val velocityX: Float, // px/s
    val initialVelocityY: Float, // negative = upward
    val gravity: Float,
    val initialRotation: Float,
    val rotationSpeed: Float,
    val durationSeconds: Float,
    val sizeWidth: Float,
    val sizeHeight: Float
)

@Composable
fun ConfettiOverlay(
    trigger: Int,
    originCenter: Offset,
    modifier: Modifier = Modifier
) {
    if (trigger <= 0) return

    val density = LocalDensity.current
    val pWidth = with(density) { 9.dp.toPx() }
    val pHeight = with(density) { 13.dp.toPx() }

    val colors = listOf(
        Color(0xFFFFD54A),
        Color(0xFFFF7A7A),
        Color(0xFF7AD7FF),
        Color(0xFF34C478),
        Color(0xFFFFFFFF),
        Color(0xFFC9A0FF)
    )

    val particles = remember(trigger) {
        val count = Random.nextInt(32, 37)
        List(count) {
            val angle = Random.nextFloat() * 2f * Math.PI.toFloat()
            val speed = Random.nextFloat() * 450f + 250f
            val vx = cos(angle) * speed
            val vy = -kotlin.math.abs(sin(angle) * speed) - 200f // always burst upwards
            ConfettiParticle(
                color = colors[Random.nextInt(colors.size)],
                velocityX = vx,
                initialVelocityY = vy,
                gravity = 650f, // pulls down
                initialRotation = Random.nextFloat() * 360f,
                rotationSpeed = (Random.nextFloat() * 400f - 200f),
                durationSeconds = Random.nextFloat() * 0.5f + 1.4f, // 1.4 - 1.9s
                sizeWidth = pWidth,
                sizeHeight = pHeight
            )
        }
    }

    val progress = remember(trigger) { Animatable(0f) }
    LaunchedEffect(trigger) {
        progress.snapTo(0f)
        progress.animateTo(1f, animationSpec = tween(durationMillis = 1800, easing = LinearEasing))
    }

    if (progress.value < 1f) {
        Canvas(modifier = modifier.fillMaxSize()) {
            val tTotal = progress.value * 1.8f // current elapsed seconds approx
            particles.forEach { p ->
                val pProgress = (tTotal / p.durationSeconds).coerceIn(0f, 1f)
                if (pProgress < 1f) {
                    val t = pProgress * p.durationSeconds
                    val currentX = originCenter.x + p.velocityX * t
                    val currentY = originCenter.y + p.initialVelocityY * t + 0.5f * p.gravity * t * t
                    val currentAlpha = (1f - pProgress).coerceIn(0f, 1f)
                    val currentRot = p.initialRotation + p.rotationSpeed * t

                    rotate(degrees = currentRot, pivot = Offset(currentX, currentY)) {
                        drawRect(
                            color = p.color.copy(alpha = currentAlpha),
                            topLeft = Offset(currentX - p.sizeWidth / 2f, currentY - p.sizeHeight / 2f),
                            size = Size(p.sizeWidth, p.sizeHeight)
                        )
                    }
                }
            }
        }
    }
}
