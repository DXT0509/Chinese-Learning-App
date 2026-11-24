package com.example.chineselearningapp.core.designsystem

import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Paint
import android.graphics.Path
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.layout.onSizeChanged
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.IntSize
import androidx.compose.ui.unit.dp
import com.example.chineselearningapp.feature.dictionary.handwriting.HandwritingStroke

/** Controlled ink surface: timed stroke data is retained by the caller for Digital Ink. */
@Composable
fun DrawingCanvas(
    strokes: List<HandwritingStroke>,
    enabled: Boolean,
    onBeginStroke: () -> Unit,
    onCompleteStroke: (HandwritingStroke?) -> Unit,
    guideCharacter: String?,
    showGrid: Boolean,
    modifier: Modifier = Modifier,
    strokeColor: Color = TextPrimary,
    strokeWidthDp: Float = 7f,
    backgroundColor: Color = Color.White,
    drawBorder: Boolean = true,
    onStrokeAdded: () -> Unit = {},
    exportRequest: Int = 0,
    onCanvasExport: (Bitmap) -> Unit = {},
) {
    var canvasSize by remember { mutableStateOf(IntSize.Zero) }
    val currentExport by rememberUpdatedState(onCanvasExport)
    val inkWidth = with(LocalDensity.current) { strokeWidthDp.dp.toPx() }
    // Export only on an explicit request, never on every point or recomposition.
    LaunchedEffect(exportRequest) {
        if (exportRequest > 0 && canvasSize.width > 0 && canvasSize.height > 0) {
            currentExport(exportDrawing(strokes, canvasSize.width, canvasSize.height, inkWidth, strokeColor.toArgb()))
        }
    }
    var boxModifier = modifier.onSizeChanged { canvasSize = it }
    if (backgroundColor != Color.Transparent) {
        boxModifier = boxModifier.clip(RoundedCornerShape(16.dp)).background(backgroundColor)
    }
    if (drawBorder) {
        boxModifier = boxModifier.border(1.5.dp, BorderStrong, RoundedCornerShape(16.dp))
    }
    BoxWithConstraints(boxModifier, contentAlignment = Alignment.Center) {
        if (!guideCharacter.isNullOrBlank()) {
            val fontSize = with(LocalDensity.current) { (minOf(maxWidth, maxHeight) * .8f).toSp() }
            Text(guideCharacter, fontSize = fontSize, color = TextPrimary.copy(alpha = .06f))
        }
        DrawingGridCanvas(strokes, enabled, onBeginStroke, { stroke ->
            onCompleteStroke(stroke)
            if (stroke != null) onStrokeAdded()
        }, preserveInterrupted = true, showGrid = showGrid, gridColor = TextPrimary.copy(alpha = .12f),
            strokeColor = strokeColor, strokeWidthDp = strokeWidthDp)
    }
}

/** Ink on an opaque white background; guides, border and toolbar never enter recognition. */
internal fun exportDrawing(
    strokes: List<HandwritingStroke>, width: Int, height: Int, strokeWidth: Float, inkColor: Int,
): Bitmap {
    require(width > 0 && height > 0)
    val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
    val canvas = Canvas(bitmap)
    canvas.drawColor(android.graphics.Color.WHITE)
    val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = inkColor
        this.strokeWidth = strokeWidth
        strokeCap = Paint.Cap.ROUND
        strokeJoin = Paint.Join.ROUND
    }
    strokes.forEach { stroke ->
        val points = stroke.points
        if (points.isEmpty()) return@forEach
        fun x(index: Int) = points[index].x / 1000f * width
        fun y(index: Int) = points[index].y / 1000f * height
        if (points.all { it.x == points.first().x && it.y == points.first().y }) {
            paint.style = Paint.Style.FILL
            canvas.drawCircle(x(0), y(0), strokeWidth / 2, paint)
        } else {
            val path = Path().apply {
                moveTo(x(0), y(0))
                for (index in 1 until points.size) {
                    quadTo(x(index - 1), y(index - 1), (x(index - 1) + x(index)) / 2, (y(index - 1) + y(index)) / 2)
                }
                lineTo(x(points.lastIndex), y(points.lastIndex))
            }
            paint.style = Paint.Style.STROKE
            canvas.drawPath(path, paint)
        }
    }
    return bitmap
}
