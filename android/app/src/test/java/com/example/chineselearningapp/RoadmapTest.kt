package com.example.chineselearningapp

import androidx.lifecycle.SavedStateHandle
import com.example.chineselearningapp.core.network.*
import com.example.chineselearningapp.domain.model.*
import com.example.chineselearningapp.domain.repository.RoadmapRepository
import com.example.chineselearningapp.feature.auth.data.SessionExpired
import com.example.chineselearningapp.feature.dictionary.handwriting.*
import com.example.chineselearningapp.feature.roadmap.*
import com.google.gson.Gson
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.junit.Assert.*
import org.junit.Test
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.io.IOException

private val unavailable = LessonEnrichment("UNAVAILABLE", null, null)
private fun activity(kind: String = "INTRODUCTION", repetitions: Int = 1, required: Boolean = true) = RoadmapActivity(kind, kind, required, "Luyện tập", repetitions,
    if (kind == "QUIZ") listOf("Một", "Hai") else emptyList())
private fun lesson(activities: List<RoadmapActivity> = listOf(activity()), type: String = "NEW_WORD") = RoadmapLesson("node-v1", "lesson-v1", type, "Một từ",
    listOf(RoadmapWord("identity", 7, "一", "yī", listOf("một"), "nhất")), activities, unavailable, unavailable, unavailable, unavailable, emptyList())
private fun node(position: Int = 0, status: String = "NOT_STARTED", available: Boolean = true) = RoadmapNode("node-$position", if (position == 0) "node-v1" else "node-at-$position",
    position, "NEW_WORD", "Từ $position", "hsk-0", status, available)

private class FakeRoadmap : RoadmapRepository {
    val roadmap = Roadmap("roadmap", "version-1", "HSK 0")
    var content = lesson()
    var empty = false
    var error: Exception? = null
    var deliveryLost = false
    var finishLost = false
    var starts = 0
    var completionCalls = 0
    var skips = 0
    var detailCalls = 0
    var startKeys = mutableListOf<String?>()
    var afters = mutableListOf<Int>()
    var accepted = mutableMapOf<String, Set<Int>>()
    var receipts = mutableMapOf<String, Boolean>()
    var submissions = mutableListOf<RoadmapEvidence>()
    var completed = false
    var gate: CompletableDeferred<Unit>? = null
    var current = 0
    override suspend fun catalog(offset: Int): RoadmapCatalog { error?.let { throw it }; return RoadmapCatalog(if (empty) emptyList() else listOf(roadmap), null) }
    override suspend fun nodes(roadmap: Roadmap, after: Int): RoadmapPage {
        afters += after
        return RoadmapPage(roadmap.versionId, (after + 1..minOf(after + 50, 119)).map { node(it, available = it <= current) },
            (after + 50).takeIf { it < 119 }, current, mapOf("hsk-0" to 0, "hsk-1" to 70))
    }
    override suspend fun lesson(nodeVersionId: String): RoadmapLesson { detailCalls++; return content.copy(nodeVersionId = nodeVersionId) }
    override suspend fun start(nodeVersionId: String, replayKey: String?): RoadmapRun {
        starts++; startKeys += replayKey
        gate?.await()
        if (replayKey != null && replayKey != startKeys.dropLast(1).lastOrNull()) { accepted.clear(); completed = false }
        return RoadmapRun(replayKey ?: "owned-run", nodeVersionId, replayKey != null, completed, accepted.toMap())
    }
    override suspend fun submit(runId: String, evidence: RoadmapEvidence): Boolean {
        submissions += evidence
        gate?.await()
        val result = receipts.getOrPut(evidence.requestId) {
            val correct = evidence.kind != "CHOICE" || evidence.choice == 1
            if (correct) accepted[evidence.activityId] = accepted[evidence.activityId].orEmpty() + evidence.repetition
            correct
        }
        if (deliveryLost) { deliveryLost = false; throw IOException() }
        return result
    }
    override suspend fun complete(runId: String): RoadmapCompletion {
        completionCalls++
        val exp = if (completed || runId != "owned-run") 0 else 10
        completed = true; current = 1
        if (finishLost) { finishLost = false; throw IOException() }
        return RoadmapCompletion("COMPLETED", exp)
    }
    override suspend fun skip(nodeVersionId: String): RoadmapCompletion { skips++; current = 1; return RoadmapCompletion("SKIPPED", 0) }
    override suspend fun media(nodeVersionId: String, assetId: String) = RoadmapMedia(byteArrayOf(), "image/gif")
}

@OptIn(ExperimentalCoroutinesApi::class)
class RoadmapTest {
    private class WritingRecognizer(var results: List<String> = listOf("一")) : HandwritingRecognizer {
        var calls = 0
        var failure: Exception? = null
        var gate: CompletableDeferred<Unit>? = null
        var received: List<HandwritingStroke> = emptyList()
        override suspend fun prepareModel(onDownload: () -> Unit) = Unit
        override suspend fun recognize(strokes: List<HandwritingStroke>): List<String> {
            calls++; received = strokes; gate?.await(); failure?.let { throw it }; return results
        }
        override fun close() = Unit
    }
    private fun writingStroke() = HandwritingStroke(listOf(
        HandwritingPoint(100f, 300f, 10), HandwritingPoint(800f, 300f, 1510)))

    @Test fun sequentialFlowKeepsSelectedActivityAndExposesReceiptForStableNavigation() = check {
        val repo = FakeRoadmap().apply { content = lesson(listOf(activity(), activity("QUIZ"))) }
        val saved = SavedStateHandle()
        val vm = RoadmapViewModel(repo, saved, "writer")
        vm.useSequentialFlow()
        advanceUntilIdle(); vm.open(node()); advanceUntilIdle()
        vm.chooseActivity(0); vm.acknowledge(); advanceUntilIdle()
        assertEquals("INTRODUCTION", vm.state.value.activity?.kind)
        assertTrue(vm.state.value.lastSubmission!!.accepted)
        assertEquals(repo.submissions.single(), vm.state.value.lastSubmission!!.evidence)
        val restored = RoadmapViewModel(repo, saved, "writer")
        advanceUntilIdle()
        assertEquals(vm.state.value.flowRunId, restored.state.value.flowRunId)
        assertEquals(0, restored.state.value.activityIndex)
        vm.chooseActivity(1); vm.choice(0); advanceUntilIdle()
        assertFalse(vm.state.value.lastSubmission!!.accepted)
        assertEquals("QUIZ", vm.state.value.activity?.kind)
    }

    private fun check(block: suspend TestScope.() -> Unit) = runTest {
        Dispatchers.setMain(StandardTestDispatcher(testScheduler))
        try { block() } finally { Dispatchers.resetMain() }
    }
    @Test fun writingGradesOnlyFirstCandidateAndKeepsInkOnMismatch() = check {
        val repo = FakeRoadmap().apply { content = lesson(listOf(activity("HANDWRITING"))) }
        val recognizer = WritingRecognizer(listOf("二", "一"))
        val vm = RoadmapViewModel(repo, SavedStateHandle(), "writer", recognizer)
        advanceUntilIdle(); vm.open(node()); advanceUntilIdle()
        vm.beginStroke(); vm.endStroke(writingStroke()); vm.checkWriting(); advanceUntilIdle()
        assertEquals(false, vm.state.value.writingResult)
        assertEquals(listOf(writingStroke()), vm.state.value.strokes)
        assertEquals(vm.state.value.strokes, recognizer.received)
        assertTrue(repo.submissions.isEmpty())
        recognizer.results = emptyList(); vm.checkWriting(); advanceUntilIdle()
        assertEquals(false, vm.state.value.writingResult)
        assertEquals(2, vm.state.value.writingFeedbackId)
        assertTrue(vm.state.value.strokes.isNotEmpty())
    }
    @Test fun correctWritingShowsSuccessFor1200msThenSubmitsOnceAndAdvances() = check {
        val repo = FakeRoadmap().apply { content = lesson(listOf(activity("HANDWRITING"), activity("QUIZ"))) }
        val recognizer = WritingRecognizer()
        val vm = RoadmapViewModel(repo, SavedStateHandle(), "writer", recognizer)
        advanceUntilIdle(); vm.open(node()); advanceUntilIdle()
        vm.beginStroke(); vm.endStroke(writingStroke())
        vm.checkWriting(); vm.checkWriting(); runCurrent()
        assertEquals(true, vm.state.value.writingResult)
        assertTrue(repo.submissions.isEmpty())
        advanceTimeBy(1199); runCurrent(); assertTrue(repo.submissions.isEmpty())
        advanceTimeBy(1); runCurrent()
        assertEquals(1, recognizer.calls); assertEquals(1, repo.submissions.size)
        assertEquals("FREEHAND", repo.submissions.single().kind)
        assertEquals("QUIZ", vm.state.value.activity?.kind)
        assertTrue(vm.state.value.strokes.isEmpty())
    }
    @Test fun recognitionErrorsKeepInkAndEmptyCanvasCannotRecognize() = check {
        val repo = FakeRoadmap().apply { content = lesson(listOf(activity("HANDWRITING"))) }
        val recognizer = WritingRecognizer().apply { failure = IOException() }
        val vm = RoadmapViewModel(repo, SavedStateHandle(), "writer", recognizer)
        advanceUntilIdle(); vm.open(node()); advanceUntilIdle()
        vm.checkWriting(); advanceUntilIdle(); assertEquals(0, recognizer.calls)
        vm.beginStroke(); vm.endStroke(writingStroke()); vm.checkWriting(); advanceUntilIdle()
        assertEquals(R.string.roadmap_recognition_error, vm.state.value.error)
        assertFalse(vm.state.value.recognizing); assertNull(vm.state.value.writingResult)
        assertEquals(listOf(writingStroke()), vm.state.value.strokes)
        assertTrue(repo.submissions.isEmpty())
    }
    @Test fun correctButTooShortInkPreservesServerParticipationRequirement() = check {
        val repo = FakeRoadmap().apply { content = lesson(listOf(activity("HANDWRITING"))) }
        val vm = RoadmapViewModel(repo, SavedStateHandle(), "writer", WritingRecognizer())
        advanceUntilIdle(); vm.open(node()); advanceUntilIdle()
        val ink = HandwritingStroke(listOf(HandwritingPoint(100f, 300f, 10), HandwritingPoint(800f, 300f, 500)))
        vm.beginStroke(); vm.endStroke(ink); vm.checkWriting(); advanceUntilIdle()
        assertEquals(R.string.roadmap_write_more, vm.state.value.error)
        assertNull(vm.state.value.writingResult)
        assertEquals(listOf(ink), vm.state.value.strokes)
        assertTrue(repo.submissions.isEmpty())
    }
    @Test fun navigationDiscardsLateRecognitionAndSuccessDoesNotSubmitAfterLeaving() = check {
        val repo = FakeRoadmap().apply { content = lesson(listOf(activity("HANDWRITING"), activity("QUIZ"))) }
        val recognizer = WritingRecognizer().apply { gate = CompletableDeferred() }
        val vm = RoadmapViewModel(repo, SavedStateHandle(), "writer", recognizer)
        advanceUntilIdle(); vm.open(node()); advanceUntilIdle()
        vm.beginStroke(); vm.endStroke(writingStroke()); vm.checkWriting(); runCurrent()
        vm.chooseActivity(1); recognizer.gate?.complete(Unit); advanceUntilIdle()
        assertNull(vm.state.value.writingResult); assertTrue(repo.submissions.isEmpty())
        vm.chooseActivity(0); vm.beginStroke(); vm.endStroke(writingStroke()); vm.checkWriting(); runCurrent()
        assertEquals(true, vm.state.value.writingResult)
        vm.leave(); advanceUntilIdle(); assertTrue(repo.submissions.isEmpty())
    }
    @Test fun emptyCatalogStopsLoadingWithoutWriting() = check {
        val repo = FakeRoadmap().apply { empty = true }; val vm = RoadmapViewModel(repo, SavedStateHandle(), "alice")
        advanceUntilIdle()
        assertFalse(vm.state.value.loading); assertTrue(vm.state.value.catalog.isEmpty())
        assertEquals(0, repo.starts); assertEquals(0, repo.skips); assertTrue(repo.submissions.isEmpty())
    }
    @Test fun pagesArePinnedDeduplicatedAndLoadedInBatches() = check {
        val repo = FakeRoadmap(); val vm = RoadmapViewModel(repo, SavedStateHandle(), "alice")
        advanceUntilIdle(); vm.more(); vm.more(); advanceUntilIdle()
        assertEquals(listOf(-1, 49), repo.afters)
        assertEquals(100, vm.state.value.nodes.size)
        assertEquals("version-1", vm.state.value.selected?.versionId)
    }
    @Test fun currentNodeJumpDoesNotWalkEveryPage() = check {
        val repo = FakeRoadmap().apply { current = 100 }; val vm = RoadmapViewModel(repo, SavedStateHandle(), "alice")
        advanceUntilIdle()
        assertEquals(listOf(-1, 94), repo.afters)
        assertTrue(vm.state.value.nodes.any { it.position == 100 })
        assertEquals(100, vm.state.value.scrollTarget)
    }
    @Test fun sectionJumpUsesServerPosition() = check {
        val repo = FakeRoadmap(); val vm = RoadmapViewModel(repo, SavedStateHandle(), "alice")
        advanceUntilIdle(); vm.jump(vm.state.value.sections["hsk-1"]); advanceUntilIdle()
        assertEquals(64, repo.afters.last()); assertEquals(70, vm.state.value.scrollTarget)
    }
    @Test fun lockedNodesCannotStartButResolvedNodesCanReopen() = check {
        val repo = FakeRoadmap(); val vm = RoadmapViewModel(repo, SavedStateHandle(), "alice")
        advanceUntilIdle(); vm.open(node(1, available = false)); advanceUntilIdle(); assertEquals(0, repo.starts)
        vm.open(node(status = "SKIPPED", available = false)); vm.open(node()); advanceUntilIdle(); assertEquals(1, repo.starts)
        assertTrue(node(status = "COMPLETED", available = false).canOpen)
        assertFalse(node(2, available = false).canOpen)
    }
    @Test fun oneWordComesFromPinnedProjectionAndRequiredReceiptsGateCompletion() = check {
        val repo = FakeRoadmap(); val vm = RoadmapViewModel(repo, SavedStateHandle(), "alice")
        advanceUntilIdle(); vm.open(node()); advanceUntilIdle()
        assertEquals(7, vm.state.value.lesson?.words?.single()?.contentVersion)
        vm.complete(); advanceUntilIdle(); assertEquals(0, repo.completionCalls)
        vm.acknowledge(); advanceUntilIdle(); assertTrue(vm.state.value.ready)
        vm.complete(); vm.complete(); advanceUntilIdle(); assertEquals(10, vm.state.value.completion?.exp)
        assertEquals(1, repo.completionCalls)
    }
    @Test fun serverRepetitionsAreRestoredAndOnlyMissingRepetitionIsSubmitted() = check {
        val repo = FakeRoadmap().apply { content = lesson(listOf(activity(repetitions = 3))); accepted["INTRODUCTION"] = setOf(0, 2) }
        val vm = RoadmapViewModel(repo, SavedStateHandle(), "alice")
        advanceUntilIdle(); vm.open(node()); advanceUntilIdle(); vm.acknowledge(); advanceUntilIdle()
        assertEquals(1, repo.submissions.single().repetition); assertTrue(vm.state.value.ready)
    }
    @Test fun optionalActivityDoesNotBlockCompletion() = check {
        val repo = FakeRoadmap().apply { content = lesson(listOf(activity(), activity("COMPONENTS", required = false))); accepted["INTRODUCTION"] = setOf(0) }
        val vm = RoadmapViewModel(repo, SavedStateHandle(), "alice")
        advanceUntilIdle(); vm.open(node()); advanceUntilIdle(); assertTrue(vm.state.value.ready)
    }
    @Test fun quizSubmitsOnlySelectedIndexAndDisplaysServerFeedback() = check {
        val repo = FakeRoadmap().apply { content = lesson(listOf(activity("QUIZ"))) }
        val vm = RoadmapViewModel(repo, SavedStateHandle(), "alice")
        advanceUntilIdle(); vm.open(node()); advanceUntilIdle(); vm.choice(0); advanceUntilIdle()
        assertEquals(false, vm.state.value.feedback); assertFalse(vm.state.value.ready)
        vm.choice(1); advanceUntilIdle(); assertEquals(true, vm.state.value.feedback)
        assertTrue(vm.state.value.ready); assertNotEquals(repo.submissions[0].requestId, repo.submissions[1].requestId)
        assertEquals("CHOICE", repo.submissions.last().kind)
    }
    @Test fun retryUsesExactEvidenceAndKeyAndPreventsRapidDuplicateSubmit() = check {
        val repo = FakeRoadmap(); val vm = RoadmapViewModel(repo, SavedStateHandle(), "alice")
        advanceUntilIdle(); vm.open(node()); advanceUntilIdle()
        repo.deliveryLost = true; vm.acknowledge(); vm.acknowledge(); advanceUntilIdle()
        assertNotNull(vm.state.value.error); vm.retry(); advanceUntilIdle()
        assertEquals(2, repo.submissions.size); assertEquals(repo.submissions[0], repo.submissions[1])
        assertEquals(1, repo.receipts.size); assertTrue(vm.state.value.ready)
    }
    @Test fun uncertainEvidenceIsRecoveredAfterViewModelRecreation() = check {
        val repo = FakeRoadmap(); val saved = SavedStateHandle()
        val vm = RoadmapViewModel(repo, saved, "alice")
        advanceUntilIdle(); vm.open(node()); advanceUntilIdle(); repo.deliveryLost = true; vm.acknowledge(); advanceUntilIdle()
        val restored = RoadmapViewModel(repo, saved, "alice"); advanceUntilIdle()
        assertTrue(restored.state.value.ready); assertEquals(repo.submissions[0], repo.submissions[1])
        assertEquals(1, repo.receipts.size)
    }
    @Test fun handwritingKeepsOriginalInkAndSerializesNormalizedParticipationEvidence() = check {
        val repo = FakeRoadmap().apply { content = lesson(listOf(activity("HANDWRITING"))) }
        val saved = SavedStateHandle(); val vm = RoadmapViewModel(repo, saved, "alice")
        advanceUntilIdle(); vm.open(node()); advanceUntilIdle()
        val stroke = HandwritingStroke(listOf(HandwritingPoint(100f, 200f, 1), HandwritingPoint(800f, 900f, 1400)))
        vm.endStroke(stroke)
        assertEquals(stroke, vm.state.value.strokes.single())
        val restored = RoadmapViewModel(repo, saved, "alice"); advanceUntilIdle()
        assertEquals(stroke, restored.state.value.strokes.single())
        restored.handwriting(); advanceUntilIdle()
        val evidence = repo.submissions.single(); assertEquals("FREEHAND", evidence.kind)
        assertEquals(.1f, evidence.strokes.single().first().x); assertEquals(1399, evidence.durationMs)
        val json = Gson().toJson(evidence.dto())
        assertTrue(json.contains("\"activity_id\"")); assertFalse(json.contains("timeMillis"))
    }
    @Test fun handwritingUndoClearAndReturnToNodePreserveDraft() = check {
        val repo = FakeRoadmap().apply { content = lesson(listOf(activity("HANDWRITING"))) }
        val vm = RoadmapViewModel(repo, SavedStateHandle(), "alice")
        advanceUntilIdle(); vm.open(node()); advanceUntilIdle()
        val stroke = HandwritingStroke(listOf(HandwritingPoint(0f, 0f, 1), HandwritingPoint(1f, 1f, 1500)))
        vm.endStroke(stroke); vm.endStroke(stroke); vm.undo(); assertEquals(1, vm.state.value.strokes.size)
        vm.leave(); advanceUntilIdle(); vm.open(node()); advanceUntilIdle(); assertEquals(listOf(stroke), vm.state.value.strokes)
        vm.clearInk(); assertTrue(vm.state.value.strokes.isEmpty())
    }
    @Test fun skipHasZeroExpAndReviewNodesCannotSkip() = check {
        val repo = FakeRoadmap(); val vm = RoadmapViewModel(repo, SavedStateHandle(), "alice")
        advanceUntilIdle(); vm.open(node()); advanceUntilIdle(); vm.skip(); advanceUntilIdle()
        assertEquals("SKIPPED", vm.state.value.completion?.status); assertEquals(0, vm.state.value.completion?.exp)
        vm.leave(); advanceUntilIdle(); repo.content = lesson(type = "REVIEW")
        // A different pinned node cannot accidentally reuse cached NEW_WORD content.
        vm.open(node(1)); advanceUntilIdle(); vm.skip(); advanceUntilIdle(); assertEquals(1, repo.skips)
    }
    @Test fun replayUsesStableUuidAndNeverPresentsAnotherReward() = check {
        val repo = FakeRoadmap().apply { completed = true; accepted["INTRODUCTION"] = setOf(0) }
        val saved = SavedStateHandle(); val vm = RoadmapViewModel(repo, saved, "alice")
        advanceUntilIdle(); vm.open(node(status = "COMPLETED")); advanceUntilIdle()
        assertNull(vm.state.value.completion)
        val key = repo.startKeys.last(); java.util.UUID.fromString(key)
        assertTrue(vm.state.value.run!!.replay)
        val restored = RoadmapViewModel(repo, saved, "alice"); advanceUntilIdle(); assertEquals(key, repo.startKeys.last())
        restored.acknowledge(); advanceUntilIdle(); restored.complete(); advanceUntilIdle()
        assertEquals(0, restored.state.value.completion?.exp)
    }
    @Test fun uncertainCompletionUsesAuthoritativeZeroOnRetry() = check {
        val repo = FakeRoadmap().apply { accepted["INTRODUCTION"] = setOf(0); finishLost = true }
        val vm = RoadmapViewModel(repo, SavedStateHandle(), "alice")
        advanceUntilIdle(); vm.open(node()); advanceUntilIdle(); vm.complete(); advanceUntilIdle(); vm.retry(); advanceUntilIdle()
        assertEquals(0, vm.state.value.completion?.exp); assertEquals(2, repo.completionCalls)
    }
    @Test fun reopeningSkippedNodeResumesLearningAndDoesNotStayOnSkipResult() = check {
        val repo = FakeRoadmap(); val vm = RoadmapViewModel(repo, SavedStateHandle(), "alice")
        advanceUntilIdle(); vm.open(node()); advanceUntilIdle(); vm.skip(); advanceUntilIdle()
        vm.leave(); advanceUntilIdle(); vm.open(node(status = "SKIPPED")); advanceUntilIdle()
        assertNull(vm.state.value.completion); assertNotNull(vm.state.value.activity)
        vm.acknowledge(); advanceUntilIdle(); vm.complete(); advanceUntilIdle()
        assertEquals(10, vm.state.value.completion?.exp)
    }
    @Test fun completionSurvivesRecreationButRevisitDoesNotRepeatPositiveExp() = check {
        val repo = FakeRoadmap(); val saved = SavedStateHandle(); val vm = RoadmapViewModel(repo, saved, "alice")
        advanceUntilIdle(); vm.open(node()); advanceUntilIdle(); vm.acknowledge(); advanceUntilIdle(); vm.complete(); advanceUntilIdle()
        val restored = RoadmapViewModel(repo, saved, "alice"); advanceUntilIdle()
        assertEquals(10, restored.state.value.completion?.exp)
        restored.leave(); advanceUntilIdle(); restored.open(node(status = "COMPLETED")); advanceUntilIdle()
        assertNull(restored.state.value.completion)
        assertTrue(restored.state.value.run!!.replay)
        restored.acknowledge(); advanceUntilIdle(); restored.complete(); advanceUntilIdle()
        assertEquals(0, restored.state.value.completion?.exp); assertEquals(2, repo.completionCalls)
    }
    @Test fun eachDeliberateReplayGetsNewKeyWhileRetriesKeepIt() = check {
        val repo = FakeRoadmap().apply { completed = true; accepted["INTRODUCTION"] = setOf(0) }
        val vm = RoadmapViewModel(repo, SavedStateHandle(), "alice")
        advanceUntilIdle(); vm.open(node(status = "COMPLETED")); advanceUntilIdle()
        val first = repo.startKeys.last()
        vm.acknowledge(); advanceUntilIdle(); vm.complete(); advanceUntilIdle(); vm.replay(); advanceUntilIdle()
        assertNotEquals(first, repo.startKeys.last())
    }
    @Test fun completedNodeRelearnsFromFirstStep() = check {
        val repo = FakeRoadmap().apply { completed = true; accepted["INTRODUCTION"] = setOf(0) }
        val saved = SavedStateHandle(); val vm = RoadmapViewModel(repo, saved, "alice")
        advanceUntilIdle(); vm.open(node(status = "COMPLETED")); advanceUntilIdle()
        assertNull(vm.state.value.completion)
        assertTrue(vm.state.value.run!!.replay)
        assertEquals(0, vm.state.value.wordIndex)
        assertNotNull(vm.state.value.activity)
    }
    @Test fun identityChangeCannotRestorePrivateRunOrInk() = check {
        val repo = FakeRoadmap(); val saved = SavedStateHandle(); val alice = RoadmapViewModel(repo, saved, "alice")
        advanceUntilIdle(); alice.open(node()); advanceUntilIdle()
        val bob = RoadmapViewModel(repo, saved, "bob"); advanceUntilIdle()
        assertNull(bob.state.value.lesson); assertNull(bob.state.value.run)
    }
    @Test fun authenticationExpiryIsExplicitAndCancellationPropagates() = check {
        val expired = RoadmapViewModel(FakeRoadmap().apply { error = SessionExpired() }, SavedStateHandle(), "alice")
        advanceUntilIdle(); assertTrue(expired.state.value.expired)
        val cancelled = RoadmapViewModel(FakeRoadmap().apply { error = CancellationException() }, SavedStateHandle(), "alice")
        advanceUntilIdle(); assertNull(cancelled.state.value.error); assertFalse(cancelled.state.value.busy)
    }
    @Test fun microphoneDeniedOrUnavailableCannotProduceReceipt() {
        RoadmapMicrophoneState.entries.filter { it != RoadmapMicrophoneState.Ready }.forEach { assertFalse(canSubmitSpeaking(it, 10000)) }
        assertFalse(canSubmitSpeaking(RoadmapMicrophoneState.Ready, 999))
        assertTrue(canSubmitSpeaking(RoadmapMicrophoneState.Ready, 1000))
    }
    @Test fun allSixKindsHaveVietnameseRendererLabels() {
        val kinds = listOf("INTRODUCTION", "COMPONENTS", "STROKE_ORDER", "HANDWRITING", "QUIZ", "PRONUNCIATION")
        assertEquals(6, kinds.map(::activityTitle).toSet().size)
        assertFalse(kinds.any { activityTitle(it) == R.string.roadmap_unavailable })
    }
    @Test fun apiParsesPaginationAndUsesAuthenticatedVersionPinnedPath() = runTest {
        MockWebServer().use { server ->
            server.enqueue(MockResponse().setBody("""{"roadmap_version_id":"v1","items":[{"id":"n","node_version_id":"nv","position":3,"node_type":"REVIEW","title":"Ôn nhóm","section":"hsk-0","status":"SKIPPED","available":true}],"next_position":3,"current_position":4,"section_positions":{"hsk-0":0}}"""))
            val api = Retrofit.Builder().baseUrl(server.url("/")).addConverterFactory(GsonConverterFactory.create()).build().create(RoadmapApi::class.java)
            val page = api.nodes("Bearer fixture", "roadmap", "v1", 2)
            assertEquals("SKIPPED", page.items.single().status); assertEquals(4, page.currentPosition)
            val request = server.takeRequest(); assertEquals("Bearer fixture", request.getHeader("Authorization"))
            assertEquals("/api/v1/roadmaps/roadmap/nodes?version_id=v1&after=2", request.path)
        }
    }
    @Test fun unavailableAndUnreviewedContentIsStrippedAtMappingBoundary() {
        val raw = """{"node_version_id":"nv","lesson_version_id":"lv","definition":{"node_type":"NEW_WORD","title":"Một","lesson":{"activities":[{"id":"a","kind":"INTRODUCTION","required":true,"prompt":"Đọc","repetitions":1,"options":[]}],"audio":{"status":"UNREVIEWED","text":"secret","asset_id":"asset"},"examples":{"status":"UNAVAILABLE"},"notes":{"status":"AVAILABLE","text":"Đã duyệt"},"stroke_order":{"status":"UNAVAILABLE"},"components":[]}},"vocabulary":[{"vocabulary_id":"word","content_version":7,"simplified":"一","pinyin":"yī","vietnamese_meanings":["một"]}]}"""
        val mapped = Gson().fromJson(raw, RoadmapLessonDto::class.java).domain()
        assertNull(mapped.audio.text); assertNull(mapped.audio.assetId); assertFalse(mapped.audio.available)
        assertEquals("Đã duyệt", mapped.notes.text); assertEquals(7, mapped.words.single().contentVersion)
        assertTrue(mapped.words.single().examples.isEmpty())
    }

    @Test fun publishedExampleTriplesKeepTheirOwnSentenceReadingAndTranslation() {
        val content = RoadmapContentDto(emptyList(), RoadmapEnrichmentDto(),
            RoadmapEnrichmentDto(status = "AVAILABLE"), RoadmapEnrichmentDto(), RoadmapEnrichmentDto(), emptyList())
        val dto = RoadmapLessonDto("nv", "lv", RoadmapDefinitionDto("NEW_WORD", "你", content), listOf(
            RoadmapWordDto("word", 1, "你", "nǐ", listOf("bạn"), "nhĩ", listOf(
                RoadmapExampleDto("你喝茶吗？", "Nǐ hē chá ma?", "Bạn có uống trà không?"),
                RoadmapExampleDto("你好！", "Nǐ hǎo!", "Xin chào!")))))
        val word = dto.domain().words.single()
        assertEquals(listOf("你喝茶吗？", "你好！"), word.examples.map { it.simplified })
        assertEquals("Nǐ hē chá ma?", word.examples.first().pinyin)
        assertEquals("Bạn có uống trà không?", word.examples.first().vietnamese)
        val review = dto.copy(definition = dto.definition.copy(lesson = content.copy(examples = RoadmapEnrichmentDto())))
        assertEquals(word, review.domain().words.single())
        assertFalse(review.domain().examples.available)
    }
}
