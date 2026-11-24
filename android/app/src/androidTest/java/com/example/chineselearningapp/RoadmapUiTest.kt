package com.example.chineselearningapp

import androidx.activity.ComponentActivity
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.size
import androidx.compose.ui.Modifier
import androidx.compose.runtime.Composable
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.unit.dp
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.example.chineselearningapp.domain.model.*
import com.example.chineselearningapp.domain.repository.RoadmapRepository
import com.example.chineselearningapp.feature.roadmap.*
import com.example.chineselearningapp.ui.theme.ChineseLearningAppTheme
import org.junit.Assert.*
import org.junit.Rule
import org.junit.Test

/** Synthetic transport fixtures only. Does not publish content or reach a real backend. */
class RoadmapUiTest {
    @get:Rule val compose = createAndroidComposeRule<ComponentActivity>()
    private val unavailable = LessonEnrichment("UNAVAILABLE", null, null)
    private val word = RoadmapWord("fixture-word", 9, "一", "yī", listOf("một"), "nhất")
    private fun lesson(kind: String) = RoadmapLesson("fixture-node", "fixture-lesson-v9", "NEW_WORD", "Bài mẫu thử",
        listOf(word), listOf(RoadmapActivity("fixture-activity", kind, true, "Luyện tập", 1,
            if (kind == "QUIZ") listOf("Lựa chọn A", "Lựa chọn B") else emptyList())), unavailable, unavailable, unavailable, unavailable,
        if (kind == "COMPONENTS") listOf(LessonComponent(0, "一", "STRUCTURAL", LessonEnrichment("AVAILABLE", "Giải thích mẫu thử", null))) else emptyList())
    private inner class Repository(private val content: RoadmapLesson) : RoadmapRepository {
        val roadmap = Roadmap("fixture-roadmap", "fixture-version", "HSK 0")
        val node = RoadmapNode("fixture-node", content.nodeVersionId, 0, content.type, content.title, "hsk-0", "NOT_STARTED", true)
        var submissions = 0
        override suspend fun catalog(offset: Int) = RoadmapCatalog(listOf(roadmap), null)
        override suspend fun nodes(roadmap: Roadmap, after: Int) = RoadmapPage(roadmap.versionId, listOf(node), null, 0, mapOf("hsk-0" to 0))
        override suspend fun lesson(nodeVersionId: String) = content
        override suspend fun start(nodeVersionId: String, replayKey: String?) = RoadmapRun("fixture-run", nodeVersionId, false, false, emptyMap())
        override suspend fun submit(runId: String, evidence: RoadmapEvidence): Boolean { submissions++; return evidence.choice == 1 || evidence.kind != "CHOICE" }
        override suspend fun complete(runId: String) = RoadmapCompletion("COMPLETED", 10)
        override suspend fun skip(nodeVersionId: String) = RoadmapCompletion("SKIPPED", 0)
        override suspend fun media(nodeVersionId: String, assetId: String): RoadmapMedia = error("No asset in fixture")
    }
    private fun activity(kind: String, content: RoadmapLesson = lesson(kind), fullScreen: Boolean = false): Repository {
        val repo = Repository(content)
        lateinit var model: RoadmapViewModel
        compose.runOnUiThread { model = RoadmapViewModel(repo, SavedStateHandle(), "fixture") }
        compose.waitUntil { !model.state.value.busy }
        compose.runOnUiThread { model.open(repo.node) }
        compose.waitUntil { model.state.value.lesson != null && !model.state.value.busy }
        compose.setContent { ChineseLearningAppTheme {
            val state = model.state.collectAsStateWithLifecycle().value
            if (fullScreen) VocabularyRoadmapScreen(state, model)
            else RenderActivity(state, model)
        } }
        return repo
    }
    @Composable private fun RenderActivity(state: RoadmapState, model: RoadmapViewModel) {
        val content = checkNotNull(state.lesson)
        when (state.activity?.kind) {
            "INTRODUCTION" -> WordIntroductionScreen(word, !state.busy, model::acknowledge)
            "COMPONENTS" -> CharacterStructureScreen(word, content, !state.busy, {}, model::acknowledge, {}, false)
            "STROKE_ORDER", "HANDWRITING" -> WritingScreen(state, model, {})
            "QUIZ" -> MultipleChoiceScreen(state.activity, state.feedback, !state.busy, model::choice, {}, {}, {})
            "PRONUNCIATION" -> PronunciationScreen(word.simplified, LessonState(), true, { _, _ -> }, {}, {}, {})
        }
    }
    @Test fun emptyCatalogHasConciseVietnameseState() {
        compose.setContent { ChineseLearningAppTheme { RoadmapEmpty() } }
        compose.onNodeWithText("Chưa có bài học").assertIsDisplayed()
        compose.onNodeWithText("Lộ trình học sẽ sớm được cập nhật.").assertIsDisplayed()
    }
    @Test fun oneWordShowsPinnedFieldsWithoutDenseDetails() {
        compose.setContent { ChineseLearningAppTheme { WordIntroductionScreen(word, true, {}) } }
        repeat(4) { compose.onNodeWithText("Tiếp tục").performClick() }
        compose.onNodeWithText("一").assertIsDisplayed()
        compose.onNodeWithText("yī").assertIsDisplayed()
        compose.onNodeWithText("một").assertIsDisplayed()
        compose.onNodeWithText("Hán Việt: nhất").assertIsDisplayed()
        compose.onNodeWithText("Tìm hiểu thêm").assertDoesNotExist()
    }
    @Test fun introductionSendsAcknowledgementOnlyOnTap() {
        val repo = activity("INTRODUCTION")
        compose.onNodeWithText("一").assertIsDisplayed()
        compose.onNodeWithText("yī").assertDoesNotExist()
        compose.onNodeWithText("một").assertDoesNotExist()
        compose.onNodeWithText("Tiếp tục").performClick()
        compose.onNodeWithText("yī").assertIsDisplayed()
        compose.onNodeWithContentDescription("Nghe phát âm tiếng Trung").assertIsDisplayed()
        compose.onNodeWithText("một").assertDoesNotExist()
        compose.onNodeWithText("Tiếp tục").performClick()
        compose.onNodeWithText("một").assertIsDisplayed()
        compose.onNodeWithText("Hán Việt: nhất").assertDoesNotExist()
        compose.onNodeWithText("Tiếp tục").performClick()
        compose.onNodeWithText("Hán Việt: nhất").assertIsDisplayed()
        compose.onNodeWithText("Tiếp tục").performClick()
        compose.runOnIdle { assertEquals(0, repo.submissions) }
        compose.onNodeWithText("Đã nhớ ✓").performClick()
        compose.runOnIdle { assertEquals(1, repo.submissions) }
    }
    @Test fun missingReadingSkipsEmptyStepAndRestoresRevealAfterRecreation() {
        val restoration = androidx.compose.ui.test.junit4.StateRestorationTester(compose)
        var acknowledged = false
        restoration.setContent { ChineseLearningAppTheme {
            WordIntroductionScreen(word.copy(sinoVietnamese = null), true, { acknowledged = true })
        } }
        repeat(2) { compose.onNodeWithText("Tiếp tục").performClick() }
        restoration.emulateSavedInstanceStateRestore()
        compose.onNodeWithText("yī").assertIsDisplayed()
        compose.onNodeWithText("một").assertIsDisplayed()
        compose.onNodeWithText("Tiếp tục").performClick()
        compose.onNodeWithText("Đã nhớ ✓").assertIsDisplayed()
        compose.runOnIdle { assertFalse(acknowledged) }
        compose.onNodeWithText("Đã nhớ ✓").performClick()
        compose.runOnIdle { assertTrue(acknowledged) }
    }
    @Test fun rememberedWordAdvancesToComponentsOnlyAfterExplicitTap() {
        val intro = lesson("INTRODUCTION")
        val components = lesson("COMPONENTS")
        val repo = activity("INTRODUCTION", intro.copy(
            activities = intro.activities + components.activities.single().copy(id = "components"),
            components = components.components), fullScreen = true)
        compose.onNodeWithText("yī").assertDoesNotExist()
        repeat(4) { compose.onNodeWithText("Tiếp tục").performClick() }
        compose.onNodeWithText("Giải thích mẫu thử").assertDoesNotExist()
        compose.runOnIdle { assertEquals(0, repo.submissions) }
        compose.onNodeWithText("Đã nhớ ✓").performClick()
        compose.onNodeWithText("Tiếp tục").assertIsDisplayed()
        compose.runOnIdle { assertEquals(1, repo.submissions) }
    }
    @Test fun longMeaningsScrollWhileRememberButtonStaysVisible() {
        compose.setContent { ChineseLearningAppTheme {
            Box(Modifier.size(320.dp, 480.dp)) {
                WordIntroductionScreen(word.copy(meanings = List(40) { "Nghĩa tiếng Việt dài $it" }), true, {})
            }
        } }
        repeat(4) { compose.onNodeWithText("Tiếp tục").assertIsDisplayed().performClick() }
        compose.onNodeWithText("Đã nhớ ✓").assertIsDisplayed()
        compose.onNodeWithText("Hán Việt: nhất").performScrollTo().assertIsDisplayed()
        compose.onNodeWithText("Đã nhớ ✓").assertIsDisplayed()
    }
    @Test fun componentsShowReviewedRoleAndExplanation() {
        activity("COMPONENTS")
        compose.onNodeWithText("Tiếp tục").performClick()
        compose.onNodeWithText("Thành phần cấu tạo").assertIsDisplayed()
    }
    @Test fun missingStrokeAssetCannotBeAcknowledgedAsViewed() {
        val repo = activity("STROKE_ORDER")
        compose.onNodeWithText("Chưa có nội dung này.").assertIsDisplayed()
        compose.onNodeWithText("Viết xong, tiếp tục →").assertIsNotEnabled()
        compose.runOnIdle { assertEquals(0, repo.submissions) }
    }
    @Test fun handwritingUsesRealCanvasAndHasNoKeyboardReplacement() {
        activity("HANDWRITING")
        compose.onNodeWithText("Kiểm tra").assertIsNotEnabled()
        compose.onNodeWithTag("handwriting_canvas").performTouchInput { swipe(Offset(40f, 40f), Offset(180f, 180f), 1200) }
        compose.onNodeWithText("Kiểm tra").assertIsEnabled()
        compose.onNodeWithText("Xóa hết").performClick()
        compose.onNodeWithText("Kiểm tra").assertIsNotEnabled()
        compose.onNode(hasSetTextAction()).assertDoesNotExist()
    }
    @Test fun independentWritingShowsWordAndDisablesCheckAfterUndoAndClear() {
        activity("HANDWRITING")
        compose.onNodeWithTag("writing_word").assertIsDisplayed()
        compose.onNodeWithTag("writing_stroke_order").assertDoesNotExist()
        compose.onNodeWithText("Kiểm tra").assertIsDisplayed().assertIsNotEnabled()
        fun draw() {
            compose.onNodeWithTag("handwriting_canvas").performTouchInput {
                swipe(Offset(width * .2f, height * .4f), Offset(width * .8f, height * .6f), 1200)
            }
        }
        draw()
        compose.onNodeWithText("Kiểm tra").assertIsEnabled()
        compose.onNodeWithText("Hoàn tác").performClick()
        compose.onNodeWithText("Kiểm tra").assertIsNotEnabled()
        draw()
        compose.onNodeWithText("Xóa hết").performClick()
        compose.onNodeWithText("Kiểm tra").assertIsNotEnabled()
    }
    @Test fun guidedWritingShowsAnimationAreaAndRequiresAvailableMedia() {
        val repo = activity("STROKE_ORDER")
        compose.onNodeWithTag("writing_stroke_order").assertIsDisplayed()
        compose.onNodeWithTag("writing_word").assertDoesNotExist()
        compose.onNodeWithText("Viết xong, tiếp tục →").assertIsDisplayed().assertIsNotEnabled()
        compose.runOnIdle { assertEquals(0, repo.submissions) }
    }
    @Test fun quizRequiresExplicitSelectionAndSubmit() {
        val repo = activity("QUIZ")
        compose.onNodeWithText("Trả lời").assertIsNotEnabled()
        compose.onNodeWithText("Lựa chọn B").performClick()
        compose.runOnIdle { assertEquals(0, repo.submissions) }
        compose.onNodeWithText("Trả lời").performClick()
        compose.runOnIdle { assertEquals(1, repo.submissions) }
    }
    @Test fun pronunciationDoesNotRequestPermissionOrSubmitOnEntry() {
        val repo = activity("PRONUNCIATION")
        compose.onNodeWithText("Bắt đầu ghi âm").assertIsDisplayed()
        compose.onNodeWithText("Tiếp tục").assertIsNotEnabled()
        compose.runOnIdle { assertEquals(0, repo.submissions) }
    }
    @Test fun lockedAndReviewNodesExposeDifferentLabels() {
        val locked = RoadmapNode("n", "nv", 1, "REVIEW", "Ôn nhóm", "hsk-0", "NOT_STARTED", false)
        var tapped = false
        compose.setContent { ChineseLearningAppTheme { RoadmapPathNode(locked, false, true) { tapped = true } } }
        compose.onNodeWithText("Ôn nhóm · Chưa mở").assertIsDisplayed()
        compose.onNode(hasStateDescription("Chưa mở")).performClick()
        compose.runOnIdle { assertTrue(tapped) }
    }
}
