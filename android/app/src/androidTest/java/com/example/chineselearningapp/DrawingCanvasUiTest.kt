package com.example.chineselearningapp

import android.graphics.Bitmap
import android.graphics.Color
import androidx.activity.ComponentActivity
import androidx.compose.foundation.layout.size
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.unit.dp
import com.example.chineselearningapp.core.designsystem.DrawingCanvas
import com.example.chineselearningapp.core.designsystem.exportDrawing
import com.example.chineselearningapp.feature.dictionary.handwriting.HandwritingPoint
import com.example.chineselearningapp.feature.dictionary.handwriting.HandwritingStroke
import com.example.chineselearningapp.ui.theme.ChineseLearningAppTheme
import org.junit.Assert.*
import org.junit.Rule
import org.junit.Test

class DrawingCanvasUiTest {
    @get:Rule val compose = createAndroidComposeRule<ComponentActivity>()

    @Test fun exportPreservesCoordinatesAndRendersStationaryTaps() {
        val ink = listOf(
            HandwritingStroke(listOf(HandwritingPoint(100f, 250f, 0), HandwritingPoint(900f, 250f, 10))),
            HandwritingStroke(listOf(HandwritingPoint(500f, 750f, 20))),
        )
        val bitmap = exportDrawing(ink, 200, 400, 4f, Color.BLACK)
        assertEquals(Color.BLACK, bitmap.getPixel(100, 100))
        assertEquals(Color.BLACK, bitmap.getPixel(100, 300))
        assertEquals(Color.WHITE, bitmap.getPixel(0, 0))
        assertEquals(Color.WHITE, bitmap.getPixel(100, 200))
        bitmap.recycle()
    }

    @Test fun exportIsExplicitAndExcludesGuidesAndClearedInk() {
        var strokes by mutableStateOf(emptyList<HandwritingStroke>())
        var request by mutableIntStateOf(0)
        var added = 0
        val exports = mutableListOf<Bitmap>()
        compose.setContent { ChineseLearningAppTheme {
            DrawingCanvas(strokes, true, {}, { stroke -> if (stroke != null) strokes = strokes + stroke },
                guideCharacter = "你", showGrid = true, modifier = Modifier.size(240.dp),
                onStrokeAdded = { added++ }, exportRequest = request, onCanvasExport = { exports.add(it) })
        } }
        compose.runOnIdle { assertTrue(exports.isEmpty()); request++ }
        compose.waitUntil { exports.size == 1 }
        compose.runOnIdle {
            val blank = exports.last()
            val pixels = IntArray(blank.width * blank.height)
            blank.getPixels(pixels, 0, blank.width, 0, 0, blank.width, blank.height)
            assertTrue(pixels.all { it == Color.WHITE })
        }
        compose.onNodeWithTag("handwriting_canvas").performTouchInput {
            swipe(Offset(width * .2f, height * .5f), Offset(width * .8f, height * .5f))
        }
        compose.runOnIdle {
            assertEquals(1, added)
            assertEquals(1, strokes.size)
            assertEquals(1, exports.size)
            request++
        }
        compose.waitUntil { exports.size == 2 }
        compose.runOnIdle {
            val ink = exports.last()
            assertNotEquals(Color.WHITE, ink.getPixel(ink.width / 2, ink.height / 2))
            strokes = emptyList()
            request++
        }
        compose.waitUntil { exports.size == 3 }
        compose.runOnIdle {
            val cleared = exports.last()
            assertEquals(Color.WHITE, cleared.getPixel(cleared.width / 2, cleared.height / 2))
            exports.forEach(Bitmap::recycle)
        }
    }
}
