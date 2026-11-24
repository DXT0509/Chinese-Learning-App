package com.example.chineselearningapp.core.designsystem

import android.content.Context
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.size
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.PathMeasure
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.StrokeJoin
import androidx.compose.ui.graphics.asComposePath
import androidx.compose.ui.graphics.drawscope.Fill
import androidx.compose.ui.graphics.drawscope.clipPath
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.core.graphics.PathParser
import com.google.gson.Gson
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

/**
 * Parsed stroke order model for a Chinese character from Make Me a Hanzi / hanzi-writer-data.
 * Coordinates are in 1024x1024 space with inverted Y (converted by y' = 900 - y).
 */
data class CharacterStrokeData(
    val strokes: List<String>,
    val medians: List<List<List<Float>>>
) {
    val strokeCount: Int get() = strokes.size
}

object StrokeDataLoader {
    private val cache = mutableMapOf<String, CharacterStrokeData?>()
    private val gson = Gson()

    fun load(context: Context, character: String): CharacterStrokeData? {
        if (character.isEmpty()) return null
        val codePoint = character.codePointAt(0)
        val hex = Integer.toHexString(codePoint).lowercase()
        if (cache.containsKey(hex)) return cache[hex]

        return try {
            val assetPath = "strokes/$hex.json"
            context.assets.open(assetPath).use { input ->
                val json = input.bufferedReader().readText()
                val parsed = gson.fromJson(json, CharacterStrokeData::class.java)
                cache[hex] = parsed
                parsed
            }
        } catch (_: Exception) {
            cache[hex] = null
            null
        }
    }
}

/**
 * Pre-transforms an SVG path from Make Me a Hanzi (1024x1024, inverted y) into standard coords scaled to target size.
 */
internal fun transformStrokeOutline(
    svgPathString: String,
    scale: Float,
    shiftX: Float = 0f,
    shiftY: Float = 0f
): Path {
    val androidPath = try {
        PathParser.createPathFromPathData(svgPathString)
    } catch (_: Exception) {
        android.graphics.Path()
    }
    // Transform: y' = 900 - y
    val matrix = android.graphics.Matrix()
    matrix.setScale(1f, -1f)
    matrix.postTranslate(0f, 900f)
    matrix.postScale(scale, scale)
    matrix.postTranslate(shiftX, shiftY)
    androidPath.transform(matrix)
    return androidPath.asComposePath()
}

internal fun transformMedianPoints(
    rawPoints: List<List<Float>>,
    scale: Float,
    shiftX: Float = 0f,
    shiftY: Float = 0f
): List<Offset> {
    return rawPoints.map { pt ->
        val x = pt.getOrElse(0) { 0f }
        val y = pt.getOrElse(1) { 0f }
        val transformedY = 900f - y
        Offset(x * scale + shiftX, transformedY * scale + shiftY)
    }
}

/**
 * Animated StrokeOrderPlayer drawing stroke by stroke with vector accuracy.
 */
@Composable
fun StrokeOrderPlayer(
    strokeData: CharacterStrokeData,
    modifier: Modifier = Modifier,
    replayTrigger: Int = 0,
    size: Dp = 128.dp,
    activeColor: Color = Primary,
    completedColor: Color = TextPrimary,
    inactiveColor: Color = InactiveStrokeColor,
    onAnimationFinished: () -> Unit = {}
) {
    var activeStrokeIndex by remember(strokeData, replayTrigger) { mutableIntStateOf(0) }
    val strokeProgress = remember(strokeData, replayTrigger) { Animatable(0f) }

    LaunchedEffect(strokeData, replayTrigger) {
        val total = strokeData.strokes.size
        for (i in 0 until total) {
            activeStrokeIndex = i
            strokeProgress.snapTo(0f)
            strokeProgress.animateTo(
                targetValue = 1f,
                animationSpec = tween(durationMillis = 700, easing = FastOutSlowInEasing)
            )
            if (i < total - 1) {
                delay(100)
            }
        }
        activeStrokeIndex = total // all completed
        onAnimationFinished()
    }

    // Scale calculation: base coordinate is 1024x1024
    Canvas(modifier = modifier.size(size)) {
        val canvasSize = this.size.minDimension
        val scale = canvasSize / 1024f
        val strokeWidth = 84f * scale // thick median stroke (~80 original units)
        val shiftX = (this.size.width - canvasSize) / 2f
        val shiftY = (this.size.height - canvasSize) / 2f

        // Parse and render strokes
        strokeData.strokes.forEachIndexed { index, svgStroke ->
            val outlinePath = transformStrokeOutline(svgStroke, scale, shiftX, shiftY)
            val medianRaw = strokeData.medians.getOrNull(index) ?: emptyList()
            val medianPoints = transformMedianPoints(medianRaw, scale, shiftX, shiftY)

            when {
                index < activeStrokeIndex -> {
                    // Fully completed stroke
                    val fullMedianPath = Path().apply {
                        if (medianPoints.isNotEmpty()) {
                            moveTo(medianPoints[0].x, medianPoints[0].y)
                            for (p in 1 until medianPoints.size) {
                                lineTo(medianPoints[p].x, medianPoints[p].y)
                            }
                        }
                    }
                    clipPath(outlinePath) {
                        drawPath(
                            path = fullMedianPath,
                            color = completedColor,
                            style = androidx.compose.ui.graphics.drawscope.Stroke(
                                width = strokeWidth,
                                cap = StrokeCap.Round,
                                join = StrokeJoin.Round
                            )
                        )
                    }
                }
                index == activeStrokeIndex -> {
                    // Currently animating stroke
                    // Draw inactive background first so stroke shape is visible
                    clipPath(outlinePath) {
                        drawRect(color = inactiveColor)
                    }

                    // Animate along median
                    if (medianPoints.isNotEmpty()) {
                        val fullMedianPath = Path().apply {
                            moveTo(medianPoints[0].x, medianPoints[0].y)
                            for (p in 1 until medianPoints.size) {
                                lineTo(medianPoints[p].x, medianPoints[p].y)
                            }
                        }
                        val measure = PathMeasure()
                        measure.setPath(fullMedianPath, forceClosed = false)
                        val length = measure.length
                        val segmentPath = Path()
                        measure.getSegment(0f, length * strokeProgress.value, segmentPath, startWithMoveTo = true)

                        clipPath(outlinePath) {
                            drawPath(
                                path = segmentPath,
                                color = activeColor,
                                style = androidx.compose.ui.graphics.drawscope.Stroke(
                                    width = strokeWidth,
                                    cap = StrokeCap.Round,
                                    join = StrokeJoin.Round
                                )
                            )
                        }
                    }
                }
                else -> {
                    // Not yet reached stroke - subtle ghost #e3e8e5
                    clipPath(outlinePath) {
                        drawRect(color = inactiveColor)
                    }
                }
            }
        }
    }
}

/**
 * Renders faint vector guide character on canvas (for 3A or hint).
 */
@Composable
fun StrokeGuideGhost(
    strokeData: CharacterStrokeData,
    modifier: Modifier = Modifier,
    alpha: Float = 0.08f,
    color: Color = TextPrimary
) {
    Canvas(modifier = modifier) {
        val canvasSize = this.size.minDimension
        val scale = canvasSize / 1024f
        val shiftX = (this.size.width - canvasSize) / 2f
        val shiftY = (this.size.height - canvasSize) / 2f

        strokeData.strokes.forEach { svgStroke ->
            val outlinePath = transformStrokeOutline(svgStroke, scale, shiftX, shiftY)
            drawPath(
                path = outlinePath,
                color = color.copy(alpha = alpha),
                style = Fill
            )
        }
    }
}

