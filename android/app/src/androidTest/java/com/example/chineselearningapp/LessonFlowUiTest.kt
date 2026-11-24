package com.example.chineselearningapp

import androidx.activity.ComponentActivity
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModelStore
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.test.platform.app.InstrumentationRegistry
import com.example.chineselearningapp.domain.model.*
import com.example.chineselearningapp.domain.repository.RoadmapRepository
import com.example.chineselearningapp.feature.dictionary.handwriting.*
import com.example.chineselearningapp.feature.roadmap.*
import com.example.chineselearningapp.ui.theme.ChineseLearningAppTheme
import org.junit.After
import org.junit.Assert.*
import org.junit.Rule
import org.junit.Test

/** Full flow against synthetic receipts. Speech callbacks and ink recognition are test doubles. */
class LessonFlowUiTest {
    @get:Rule val compose = createAndroidComposeRule<ComponentActivity>()
    private val store = ViewModelStore()
    private val unavailable = LessonEnrichment("UNAVAILABLE", null, null)
    private class Ink : HandwritingRecognizer {
        var candidate = "二"
        override suspend fun prepareModel(onDownload: () -> Unit) = Unit
        override suspend fun recognize(strokes: List<HandwritingStroke>) = listOf(candidate)
        override fun close() = Unit
    }
    private inner class Repository : RoadmapRepository {
        val roadmap = Roadmap("roadmap", "v1", "HSK 0")
        val node = RoadmapNode("node", "nv", 0, "NEW_WORD", "你", "hsk-0", "NOT_STARTED", true)
        val accepted = mutableMapOf<String, Set<Int>>()
        val submissions = mutableListOf<RoadmapEvidence>()
        var completions = 0
        val content = RoadmapLesson("nv", "lv", "NEW_WORD", "你",
            listOf(RoadmapWord("ni", 1, "你", "nǐ", listOf("bạn"), "nhĩ",
                listOf(RoadmapExample("你好！", "Nǐ hǎo!", "Xin chào!")))),
            listOf("INTRODUCTION", "STROKE_ORDER", "HANDWRITING", "PRONUNCIATION", "QUIZ").map { kind ->
                RoadmapActivity(kind, kind, true, "Chọn nghĩa của 你", if (kind == "PRONUNCIATION") 2 else 1,
                    if (kind == "QUIZ") listOf("tôi", "bạn", "anh ấy", "chúng ta") else emptyList())
            }, unavailable, LessonEnrichment("AVAILABLE", "Câu đã duyệt", null), unavailable,
            LessonEnrichment("AVAILABLE", null, "ni-gif"), emptyList())
        override suspend fun catalog(offset: Int) = RoadmapCatalog(listOf(roadmap), null)
        override suspend fun nodes(roadmap: Roadmap, after: Int) = RoadmapPage("v1", listOf(node), null, 0, emptyMap())
        override suspend fun lesson(nodeVersionId: String) = content
        override suspend fun start(nodeVersionId: String, replayKey: String?) = RoadmapRun("run", "nv", false, false, accepted)
        override suspend fun submit(runId: String, evidence: RoadmapEvidence): Boolean {
            submissions += evidence
            val correct = evidence.kind != "CHOICE" || evidence.choice == 1
            if (correct) accepted[evidence.activityId] = accepted[evidence.activityId].orEmpty() + evidence.repetition
            return correct
        }
        override suspend fun complete(runId: String): RoadmapCompletion {
            completions++
            check(content.activities.all { accepted[it.id]?.size == it.repetitions })
            return RoadmapCompletion("COMPLETED", 10)
        }
        override suspend fun skip(nodeVersionId: String) = RoadmapCompletion("SKIPPED", 0)
        override suspend fun media(nodeVersionId: String, assetId: String) = RoadmapMedia(
            InstrumentationRegistry.getInstrumentation().context.assets.open("ni.gif").use { it.readBytes() }, "image/gif")
    }
    @After fun clear() { compose.runOnUiThread { store.clear() } }

    @Test fun completeFlowKeepsScoreAndBackNeverReturnsToLegacyLessonUi() {
        val repo = Repository()
        val ink = Ink()
        lateinit var roadmap: RoadmapViewModel
        lateinit var lesson: LessonViewModel
        compose.runOnUiThread {
            roadmap = RoadmapViewModel(repo, SavedStateHandle(), "test-owner", ink)
            lesson = LessonViewModel(SavedStateHandle())
            store.put("roadmap", roadmap); store.put("lesson", lesson)
        }
        compose.waitUntil { !roadmap.state.value.busy }
        compose.runOnUiThread { roadmap.open(repo.node) }
        compose.waitUntil { roadmap.state.value.lesson != null }
        compose.setContent { ChineseLearningAppTheme {
            RoadmapLessonFlow(roadmap.state.collectAsStateWithLifecycle().value, roadmap, lesson)
        } }
        repeat(4) { compose.onNodeWithText("Tiếp tục").performClick() }
        compose.onNodeWithText("Đã nhớ ✓").performClick()
        compose.waitUntil { lesson.state.value.step == LessonStep.Structure }
        compose.onNodeWithText("Hiểu rồi, tiếp tục →").performClick()
        compose.waitUntil(10000) { compose.onAllNodes(hasText("Viết xong, tiếp tục →") and isEnabled()).fetchSemanticsNodes().isNotEmpty() }
        compose.onNodeWithText("Viết xong, tiếp tục →").performClick()
        compose.waitUntil { lesson.state.value.step == LessonStep.IndependentWriting }
        fun drawAndCheck() {
            compose.onNodeWithTag("handwriting_canvas").performTouchInput {
                swipe(Offset(width * .2f, height * .5f), Offset(width * .8f, height * .5f), 1200)
            }
            compose.onNodeWithText("Kiểm tra").performClick()
        }
        drawAndCheck()
        compose.waitUntil { lesson.mistakeCount == 1 }
        compose.runOnUiThread { ink.candidate = "你" }
        drawAndCheck()
        compose.waitUntil(10000) { lesson.state.value.step == LessonStep.Pinyin }
        compose.onNodeWithTag("lesson_pinyin").performTextInput("ni1")
        compose.onNodeWithText("Kiểm tra").performClick()
        compose.onNodeWithTag("lesson_pinyin").performTextReplacement("ni2")
        compose.onNodeWithText("Kiểm tra").performClick()
        compose.onNodeWithText("Đáp án: nǐ").assertIsDisplayed()
        compose.onNodeWithTag("lesson_pinyin").performTextReplacement("ni3")
        compose.onNodeWithText("Kiểm tra").performClick()
        compose.onNodeWithText("Tiếp tục").performClick()
        compose.runOnUiThread { lesson.speechResult("他", 1300, "你"); lesson.speechResult("你", 1300, "你") }
        compose.onNodeWithText("Tiếp tục").performClick()
        compose.waitUntil { lesson.state.value.step == LessonStep.MultipleChoice }
        compose.onNodeWithText("tôi").performClick()
        compose.onNodeWithText("Trả lời").performClick()
        compose.waitUntil { lesson.state.value.feedback == false }
        compose.onNodeWithText("bạn").performClick()
        compose.onNodeWithText("Trả lời").performClick()
        compose.waitUntil { lesson.state.value.feedback == true }
        compose.onNodeWithText("Tiếp tục").performClick()
        compose.onNodeWithTag("lesson_translation").performTextInput("他好")
        compose.onNodeWithText("Kiểm tra").performClick()
        compose.onNodeWithTag("lesson_translation").performTextReplacement("你好")
        compose.onNodeWithText("Kiểm tra").performClick()
        compose.onNodeWithText("Tiếp tục").performClick()
        compose.runOnUiThread { lesson.speechResult("你好", 1800, "你好！") }
        compose.onNodeWithText("Tiếp tục").performClick()
        compose.waitUntil { roadmap.state.value.completion != null }
        compose.runOnIdle {
            assertEquals(LessonStep.Summary, lesson.state.value.step)
            assertEquals(40, lesson.lessonScore); assertEquals(6, lesson.mistakeCount)
            assertEquals(1, repo.completions)
            assertEquals(2, repo.submissions.count { it.kind == "SPEAKING" })
        }
        compose.onNodeWithText("← Quay lại").performClick()
        compose.runOnIdle { assertEquals(LessonStep.Speaking, lesson.state.value.step) }
        compose.onNodeWithText("← Quay lại").performClick()
        compose.onNodeWithTag("lesson_translation").assertTextContains("你好")
        compose.onNodeWithText("← Quay lại").performClick()
        compose.runOnIdle {
            assertEquals(LessonStep.MultipleChoice, lesson.state.value.step)
            assertEquals(40, lesson.lessonScore); assertEquals(1, repo.completions)
        }
        compose.onNodeWithText("Tìm hiểu thêm").assertDoesNotExist()
        compose.onNodeWithText("Đã luyện", substring = true).assertDoesNotExist()
        compose.onNodeWithText("Tập viết").assertDoesNotExist()
    }
}
