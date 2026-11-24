package com.example.chineselearningapp

import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Movie
import android.media.MediaPlayer
import androidx.activity.ComponentActivity
import androidx.compose.foundation.layout.Column
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.test.platform.app.InstrumentationRegistry
import com.example.chineselearningapp.core.network.RoadmapLessonDto
import com.example.chineselearningapp.domain.model.RoadmapMedia
import com.example.chineselearningapp.feature.roadmap.*
import com.example.chineselearningapp.ui.theme.ChineseLearningAppTheme
import com.google.gson.Gson
import org.junit.Assert.*
import org.junit.Rule
import org.junit.Test
import java.io.File
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit

/** Pending-review real assets in a separate test package; no learner API or microphone capture. */
class Hsk0PackUiTest {
    @get:Rule val compose = createAndroidComposeRule<ComponentActivity>()
    private val context get() = InstrumentationRegistry.getInstrumentation().context
    private fun lessons() = Gson().fromJson(context.assets.open("hsk0-lessons.json").bufferedReader().use { it.readText() },
        Array<RoadmapLessonDto>::class.java).map { it.domain() }
    @Test fun realRecordingsPrepareAndAllGifFramesDecodeOnDevice() {
        for (stem in listOf("wo", "ni", "hao")) {
            val file = File(InstrumentationRegistry.getInstrumentation().targetContext.cacheDir, "$stem.ogg")
            file.writeBytes(context.assets.open("$stem.ogg").use { it.readBytes() })
            val player = MediaPlayer()
            try {
                player.setDataSource(file.absolutePath); player.prepare()
                assertTrue(player.duration in 500..2000)
                val completed = CountDownLatch(1)
                player.setOnCompletionListener { completed.countDown() }
                player.setVolume(0f, 0f)
                player.start()
                assertTrue("Recording must decode and play to completion", completed.await(5, TimeUnit.SECONDS))
            } finally { player.release(); file.delete() }
            @Suppress("DEPRECATION") val movie = Movie.decodeStream(context.assets.open("$stem.gif"))
            assertNotNull(movie); assertEquals(100, movie.width()); assertEquals(100, movie.height())
            assertTrue(movie.duration() > 1000)
            val bitmap = Bitmap.createBitmap(100, 100, Bitmap.Config.ARGB_8888)
            val canvas = Canvas(bitmap)
            var changed = false
            var previous = 0
            for (i in 0..31) {
                canvas.drawColor(android.graphics.Color.WHITE)
                movie.setTime(i * (movie.duration() - 1) / 31); movie.draw(canvas, 0f, 0f)
                val pixels = IntArray(10000); bitmap.getPixels(pixels, 0, 100, 0, 0, 100, 100)
                val hash = pixels.contentHashCode()
                if (i > 0 && hash != previous) changed = true
                previous = hash
            }
            assertTrue("Animation must change frames", changed); bitmap.recycle()
        }
    }
    @Test fun realWordDisplaysChinesePinyinMeaningAndSinoVietnamese() {
        val lesson = lessons().first()
        compose.setContent { ChineseLearningAppTheme {
            WordIntroductionScreen(lesson.words.single(), true, {})
        } }
        repeat(4) { compose.onNodeWithText("Tiếp tục").performClick() }
        compose.onNodeWithText("我").assertIsDisplayed()
        compose.onNodeWithText("wǒ").assertIsDisplayed()
        compose.onNodeWithText("Hán Việt: ngã").assertIsDisplayed()
        compose.onNodeWithText("tôi; mình").assertIsDisplayed()
    }
    @Test fun validStrokeAssetReportsRenderedAfterDecode() {
        val lesson = lessons()[1]
        var acknowledged = false
        val bytes = context.assets.open("ni.gif").use { it.readBytes() }
        compose.setContent { ChineseLearningAppTheme {
            ReviewedAsset(lesson.strokeOrder, { RoadmapMedia(bytes, "image/gif") }, animationControls = true,
                onRendered = { acknowledged = it })
        } }
        compose.waitUntil(5000) { acknowledged }
        compose.runOnIdle { assertTrue(acknowledged) }
    }
    @Test fun realToneQuizRequiresExplicitChoiceAndSubmission() {
        val quiz = lessons()[2].activities.first { it.kind == "QUIZ" }
        var selected: Int? = null
        compose.setContent { ChineseLearningAppTheme {
            MultipleChoiceScreen(quiz, null, true, { selected = it }, {}, {}, {})
        } }
        compose.onNodeWithText("Trả lời").assertIsNotEnabled()
        compose.onNodeWithText(quiz.options[0]).performClick()
        compose.runOnIdle { assertNull(selected) }
        compose.onNodeWithText("Trả lời").assertIsEnabled().performClick()
        compose.runOnIdle { assertEquals(0, selected) }
    }
    @Test fun realPronunciationHasReferenceAudioAndNoAutomaticRecording() {
        val lesson = lessons().first()
        var submitted = false
        compose.setContent { ChineseLearningAppTheme {
            PronunciationScreen(lesson.words.single().simplified, LessonState(), true,
                { _, _ -> submitted = true }, {}, {}) {
                RoadmapAudio(lesson.audio) { RoadmapMedia(context.assets.open("wo.ogg").use { it.readBytes() }, "audio/ogg") }
            }
        } }
        compose.onNodeWithText("Nghe phát âm").assertExists()
        compose.onNodeWithText("Tiếp tục").assertIsNotEnabled()
        compose.runOnIdle { assertFalse(submitted) }
    }
}
