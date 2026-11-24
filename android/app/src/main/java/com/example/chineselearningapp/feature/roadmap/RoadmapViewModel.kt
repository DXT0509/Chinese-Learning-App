package com.example.chineselearningapp.feature.roadmap

import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.chineselearningapp.R
import com.example.chineselearningapp.domain.model.*
import com.example.chineselearningapp.domain.repository.RoadmapRepository
import com.example.chineselearningapp.feature.auth.data.SessionExpired
import com.example.chineselearningapp.feature.dictionary.handwriting.*
import com.google.gson.Gson
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.util.UUID
import retrofit2.HttpException

data class RoadmapSubmissionResult(val evidence: RoadmapEvidence, val accepted: Boolean)

data class RoadmapState(
    val loading: Boolean = false, val busy: Boolean = false, val error: Int? = null, val expired: Boolean = false,
    val catalog: List<Roadmap> = emptyList(), val catalogNext: Int? = null, val selected: Roadmap? = null,
    val nodes: List<RoadmapNode> = emptyList(), val next: Int? = null, val current: Int? = null,
    val sections: Map<String, Int> = emptyMap(), val scrollTarget: Int? = null,
    val lesson: RoadmapLesson? = null, val opening: Boolean = false, val run: RoadmapRun? = null,
    val accepted: Map<String, Set<Int>> = emptyMap(), val feedback: Boolean? = null,
    val completion: RoadmapCompletion? = null, val strokes: List<HandwritingStroke> = emptyList(),
    val candidates: List<String> = emptyList(), val recognizing: Boolean = false, val drawing: Boolean = false,
    val wordIndex: Int = 0, val activityIndex: Int? = null,
    val deliveryPending: Boolean = false,
    val writingResult: Boolean? = null,
    val writingFeedbackId: Int = 0,
    val lastSubmission: RoadmapSubmissionResult? = null,
    val flowRunId: String? = null,
    val writingFeedbackToken: String? = null,
    val writingSuccessToken: String? = null,
) {
    val activity: RoadmapActivity? get() = lesson?.activities?.getOrNull(activityIndex ?: nextActivityIndex())
    fun nextActivityIndex() = lesson?.activities?.indexOfFirst { a -> (accepted[a.id]?.size ?: 0) < a.repetitions }?.takeIf { it >= 0 } ?: -1
    val ready: Boolean get() = lesson?.activities?.filter { it.required }?.all { (accepted[it.id]?.size ?: 0) >= it.repetitions } == true
}

/** Graph-scoped: pages survive detail navigation/rotation and are discarded at logout. */
class RoadmapViewModel(private val repository: RoadmapRepository, private val saved: SavedStateHandle,
    owner: String, private val recognizer: HandwritingRecognizer? = null) : ViewModel() {
    private val prefix = "roadmap.$owner."
    private val gson = Gson()
    private val mutable = MutableStateFlow(RoadmapState())
    val state = mutable.asStateFlow()
    private var pending: RoadmapEvidence? = saved.get<String>(prefix + "evidence")?.let { gson.fromJson(it, RoadmapEvidence::class.java) }
    private var retryAction: (() -> Unit)? = null
    private var sequentialFlow = saved.get<Boolean>(prefix + "sequentialFlow") ?: false
    fun useSequentialFlow() { sequentialFlow = true; saved[prefix + "sequentialFlow"] = true }
    val handwritingRecognizer: HandwritingRecognizer? get() = recognizer
    private val lessonCache = linkedMapOf<String, RoadmapLesson>()
    private val mediaCache = linkedMapOf<String, RoadmapMedia>()
    private val mediaMutex = kotlinx.coroutines.sync.Mutex()
    var scrollIndex: Int
        get() = saved[prefix + "scrollIndex"] ?: 0
        set(value) { saved[prefix + "scrollIndex"] = value }
    var scrollOffset: Int
        get() = saved[prefix + "scrollOffset"] ?: 0
        set(value) { saved[prefix + "scrollOffset"] = value }
    fun saveScroll(index: Int, offset: Int) {
        scrollIndex = index; scrollOffset = offset
        state.value.nodes.getOrNull((index - 1).coerceAtLeast(0))?.let { saved[prefix + "anchor"] = it.position }
    }
    init {
        load()
    }
    private fun change(block: (RoadmapState) -> RoadmapState) { mutable.value = block(mutable.value) }
    private fun task(retry: () -> Unit, block: suspend () -> Unit) {
        if (state.value.busy || state.value.loading) return
        retryAction = retry
        change { it.copy(busy = true, error = null) }
        viewModelScope.launch {
            try { block(); retryAction = null }
            catch (cancelled: CancellationException) { throw cancelled }
            catch (_: SessionExpired) { change { it.copy(expired = true) } }
            catch (failure: HttpException) {
                val versionChanged = failure.code() == 409 && failure.response()?.errorBody()?.string()?.contains("VERSION_UNAVAILABLE") == true
                if (versionChanged) retryAction = ::refreshActive
                change { it.copy(error = if (versionChanged) R.string.roadmap_version_changed else R.string.roadmap_network_error) }
            }
            catch (_: Exception) { change { it.copy(error = R.string.roadmap_network_error) } }
            finally { change { it.copy(busy = false, loading = false) } }
        }
    }
    fun retry() { retryAction?.invoke() ?: load() }
    private fun refreshActive() {
        saveDraft()
        saved.remove<String>(prefix + "node")
        draftFields.forEach { saved.remove<Any>(prefix + it) }
        pending = null
        change { it.copy(lesson = null, run = null, completion = null) }
        load()
    }
    fun load() = task(::load) {
        change { it.copy(loading = true) }
        val page = repository.catalog()
        val selected = page.items.firstOrNull { it.id == saved.get<String>(prefix + "roadmap") } ?: page.items.firstOrNull()
        change { it.copy(catalog = page.items, catalogNext = page.nextOffset, selected = selected) }
        if (selected != null) {
            val pageNodes = repository.nodes(selected)
            setPage(pageNodes, false)
            val anchor = saved.get<Int>(prefix + "anchor") ?: pageNodes.currentPosition
            if (anchor != null && anchor >= 50) setPage(repository.nodes(selected, (anchor - 5).coerceAtLeast(0) - 1), false)
            val node = saved.get<String>(prefix + "node")
            if (node != null) restoreLesson(node)
            else change { it.copy(scrollTarget = anchor) }
        } else change { it.copy(nodes = emptyList(), next = null) }
    }
    fun moreCatalog() {
        val next = state.value.catalogNext ?: return
        task(::moreCatalog) {
            val page = repository.catalog(next)
            change { it.copy(catalog = (it.catalog + page.items).distinctBy { r -> r.versionId }, catalogNext = page.nextOffset) }
        }
    }
    fun select(roadmap: Roadmap) {
        if (roadmap == state.value.selected) return
        task({ select(roadmap) }) {
            saved[prefix + "roadmap"] = roadmap.id
            saved.remove<Int>(prefix + "anchor")
            scrollIndex = 0; scrollOffset = 0
            val page = repository.nodes(roadmap)
            change { it.copy(selected = roadmap) }
            setPage(page, false)
            if ((page.currentPosition ?: 0) >= 50) setPage(repository.nodes(roadmap, page.currentPosition!! - 6), false)
            change { it.copy(scrollTarget = page.currentPosition) }
        }
    }
    private fun setPage(page: RoadmapPage, append: Boolean) {
        require(page.versionId == state.value.selected?.versionId)
        change { it.copy(nodes = (if (append) it.nodes + page.items else page.items).distinctBy { n -> n.versionId }.sortedBy { n -> n.position },
            next = page.nextPosition, current = page.currentPosition, sections = page.sections) }
    }
    fun more() {
        val after = state.value.next ?: return
        val selected = state.value.selected ?: return
        task(::more) { setPage(repository.nodes(selected, after), true) }
    }
    fun jump(position: Int? = state.value.current) {
        position ?: return
        if (state.value.nodes.any { it.position == position }) { change { it.copy(scrollTarget = position) }; return }
        val selected = state.value.selected ?: return
        task({ jump(position) }) {
            setPage(repository.nodes(selected, (position - 5).coerceAtLeast(0) - 1), false)
            change { it.copy(scrollTarget = position) }
        }
    }
    fun scrolled(position: Int?) { saved[prefix + "anchor"] = position; change { it.copy(scrollTarget = null) } }
    fun open(node: RoadmapNode) {
        if (!node.canOpen || state.value.opening || state.value.lesson != null) return
        task({ reopen(node.versionId) }) {
            change { it.copy(opening = true) }
            saveDraft()
            saved[prefix + "node"] = node.versionId
            if (node.status == "COMPLETED") {
                draftFields.forEach { saved.remove<Any>(prefix + "draft.${node.versionId}.$it") }
                draftFields.forEach { saved.remove<Any>(prefix + it) }
                saved[prefix + "replay"] = UUID.randomUUID().toString()
            } else {
                restoreDraft(node.versionId)
            }
            try { restoreLesson(node.versionId) } finally { change { it.copy(opening = false) } }
        }
    }
    private fun reopen(nodeId: String): Unit = task({ reopen(nodeId) }) { restoreLesson(nodeId) }
    private suspend fun restoreLesson(nodeId: String) {
        val lesson = lessonCache[nodeId] ?: repository.lesson(nodeId)
        cacheLesson(lesson)
        val savedCompletion = saved.get<String>(prefix + "completion")?.let { gson.fromJson(it, RoadmapCompletion::class.java) }
        if (savedCompletion != null) {
            change { it.copy(lesson = lesson, run = null, completion = savedCompletion, flowRunId = saved[prefix + "flowRunId"]) }
            return
        }
        val replayKey: String? = saved[prefix + "replay"]
        var run = repository.start(nodeId, replayKey)
        if (run.completed && replayKey == null) {
            val key = UUID.randomUUID().toString()
            saved[prefix + "replay"] = key
            run = repository.start(nodeId, key)
        }
        saved[prefix + "flowRunId"] = run.id
        val completion = if (run.completed) RoadmapCompletion("COMPLETED", 0) else null
        val strokes = saved.get<String>(prefix + "ink")?.let {
            gson.fromJson(it, Array<Array<DoubleArray>>::class.java).map { points ->
                HandwritingStroke(points.map { point -> HandwritingPoint(point[0].toFloat(), point[1].toFloat(), point[2].toLong()) })
            }
        }.orEmpty()
        change { it.copy(lesson = lesson, run = run, flowRunId = run.id, accepted = run.accepted, completion = completion,
            strokes = strokes, feedback = null, deliveryPending = pending != null,
            activityIndex = saved[prefix + "activity"], wordIndex = saved[prefix + "word"] ?: 0) }
        // Recover an uncertain delivery using the exact original body, even when start already
        // reports this repetition accepted. No new evidence or request key is synthesized.
        pending?.let { evidence ->
            val accepted = repository.submit(run.id, evidence)
            pending = null; saved.remove<String>(prefix + "evidence")
            change { it.copy(deliveryPending = false) }
            change { it.copy(lastSubmission = RoadmapSubmissionResult(evidence, accepted)) }
            if (accepted) {
                clearInk()
                if (!sequentialFlow) saved.remove<Int>(prefix + "activity")
                change { it.copy(accepted = it.accepted + (evidence.activityId to
                    (it.accepted[evidence.activityId].orEmpty() + evidence.repetition)),
                    activityIndex = if (sequentialFlow) it.activityIndex else null, feedback = true) }
            } else change { it.copy(feedback = false) }
        }
        val position = state.value.nodes.firstOrNull { it.versionId == nodeId }?.position
        val next = state.value.nodes.firstOrNull { position != null && it.position > position && it.canOpen }
        if (next != null && next.versionId !in lessonCache) viewModelScope.launch {
            try { cacheLesson(repository.lesson(next.versionId)) }
            catch (cancelled: CancellationException) { throw cancelled }
            catch (_: Exception) { /* Optional prefetch never discards the current owned run. */ }
        }
    }
    private fun cacheLesson(lesson: RoadmapLesson) {
        lessonCache[lesson.nodeVersionId] = lesson
        while (lessonCache.size > 2) lessonCache.remove(lessonCache.keys.first())
    }
    fun replay() {
        if (state.value.busy || state.value.lesson == null || state.value.completion?.status != "COMPLETED") return
        saved[prefix + "replay"] = UUID.randomUUID().toString()
        startReplay()
    }
    private fun startReplay() {
        val lesson = state.value.lesson ?: return
        task(::startReplay) {
            saved.remove<String>(prefix + "completion")
            clearInk()
            saved.remove<Int>(prefix + "activity")
            saved.remove<Int>(prefix + "word")
            change { it.copy(completion = null, activityIndex = null, wordIndex = 0) }
            restoreLesson(lesson.nodeVersionId)
        }
    }
    fun chooseActivity(index: Int) {
        if (state.value.busy || pending != null ||
            index !in state.value.lesson?.activities.orEmpty().indices || state.value.activityIndex == index) return
        saved[prefix + "activity"] = index
        clearInk()
        change { it.copy(activityIndex = index, feedback = null) }
    }
    fun word(index: Int) {
        if (state.value.busy || pending != null || state.value.drawing) return
        saved[prefix + "word"] = index
        change { it.copy(wordIndex = index) }
    }
    fun acknowledge() = submit("ACKNOWLEDGE")
    fun choice(index: Int) = submit("CHOICE", choice = index)
    fun speaking(durationMs: Int) = submit("SPEAKING", duration = durationMs)
    fun handwriting() {
        val strokes = state.value.strokes
        if (strokes.isEmpty() || state.value.drawing) return
        val duration = strokes.sumOf { (it.points.last().timeMillis - it.points.first().timeMillis).coerceAtLeast(0) }
        if (duration < 1000) { change { it.copy(error = R.string.roadmap_write_more) }; return }
        // Split long gestures at shared original points, without snapping or synthesizing coordinates.
        val evidence = strokes.flatMap { stroke ->
            stroke.points.windowed(1000, 999, partialWindows = true).filter { it.size >= 2 }.map { points ->
                points.map { RoadmapPoint((it.x / 1000).coerceIn(0f, 1f), (it.y / 1000).coerceIn(0f, 1f)) }
            }
        }
        if (evidence.size > 100) { change { it.copy(error = R.string.roadmap_ink_limit) }; return }
        submit("FREEHAND", strokes = evidence, duration = duration.coerceAtMost(300000).toInt())
    }
    private fun submit(kind: String, choice: Int? = null, strokes: List<List<RoadmapPoint>> = emptyList(), duration: Int = 0) {
        val state = state.value
        val activity = state.activity ?: return
        val run = state.run ?: return
        if (state.busy || state.completion != null) return
        val repetition = (0 until activity.repetitions).firstOrNull { it !in state.accepted[activity.id].orEmpty() } ?: return
        if (pending == null) {
            pending = RoadmapEvidence(UUID.randomUUID().toString(), activity.id, kind, repetition, choice, strokes, duration)
            saved[prefix + "evidence"] = gson.toJson(pending)
            change { it.copy(deliveryPending = true) }
        }
        val evidence = checkNotNull(pending)
        task({ retrySubmission() }) {
            val accepted = repository.submit(run.id, evidence)
            pending = null; saved.remove<String>(prefix + "evidence")
            change { it.copy(feedback = accepted, deliveryPending = false, accepted = if (accepted) it.accepted +
                (evidence.activityId to (it.accepted[evidence.activityId].orEmpty() + evidence.repetition)) else it.accepted,
                lastSubmission = RoadmapSubmissionResult(evidence, accepted)) }
            if (accepted) {
                clearInk()
                if (!sequentialFlow) {
                    saved.remove<Int>(prefix + "activity")
                    change { it.copy(activityIndex = null) }
                }
            }
        }
    }
    private fun retrySubmission() {
        val evidence = pending ?: return
        submit(evidence.kind, evidence.choice, evidence.strokes, evidence.durationMs)
    }
    fun complete() {
        val run = state.value.run ?: return
        if (!state.value.ready || state.value.completion != null || pending != null) return
        task(::complete) {
            val result = repository.complete(run.id)
            saved[prefix + "completion"] = gson.toJson(result)
            change { it.copy(completion = result) }
        }
    }
    fun skip() {
        val lesson = state.value.lesson ?: return
        if (lesson.type != "NEW_WORD" || state.value.run?.completed == true || state.value.completion != null) return
        task(::skip) {
            val result = repository.skip(lesson.nodeVersionId)
            saved[prefix + "completion"] = gson.toJson(result)
            change { it.copy(completion = result) }
        }
    }
    fun markWordKnown() {
        val lesson = state.value.lesson ?: return
        if (state.value.busy) return
        task(::markWordKnown) {
            repository.skip(lesson.nodeVersionId)
            saved.remove<String>(prefix + "completion")
            leaveInternal(jumpToCurrent = true)
        }
    }
    fun leaveLesson() = leave()
    private val draftFields = listOf("replay", "completion", "activity", "word", "ink", "evidence", "flowRunId")
    private fun saveDraft() {
        val node = saved.get<String>(prefix + "node") ?: return
        val previous = saved.get<ArrayList<String>>(prefix + "draftNodes").orEmpty()
        val nodes = (previous.filter { it != node } + node).takeLast(1)
        previous.filter { it !in nodes }.forEach { old -> draftFields.forEach { saved.remove<Any>(prefix + "draft.$old.$it") } }
        saved[prefix + "draftNodes"] = ArrayList(nodes)
        draftFields.forEach { field ->
            saved.remove<Any>(prefix + "draft.$node.$field")
            saved.get<Any>(prefix + field)?.let { value ->
                // Revisiting historical results must not re-present the original positive reward.
                if (field == "completion") {
                    val completion = gson.fromJson(value as String, RoadmapCompletion::class.java)
                    if (completion.status == "COMPLETED") saved[prefix + "draft.$node.$field"] = gson.toJson(completion.copy(exp = 0))
                } else saved[prefix + "draft.$node.$field"] = value
            }
        }
    }
    private fun restoreDraft(node: String) {
        draftFields.forEach { field ->
            saved.remove<Any>(prefix + field)
            saved.get<Any>(prefix + "draft.$node.$field")?.let { saved[prefix + field] = it }
        }
        pending = saved.get<String>(prefix + "evidence")?.let { gson.fromJson(it, RoadmapEvidence::class.java) }
    }
    fun leave() = leaveInternal(false)
    fun continuePath() = leaveInternal(true)
    private fun leaveInternal(jumpToCurrent: Boolean) {
        if (state.value.busy) return
        saveDraft()
        (listOf("node") + draftFields).forEach { saved.remove<Any>(prefix + it) }
        pending = null
        change { it.copy(lesson = null, run = null, completion = null, strokes = emptyList(), feedback = null, activityIndex = null, wordIndex = 0, deliveryPending = false) }
        val selected = state.value.selected ?: return
        val first = state.value.nodes.firstOrNull()?.position ?: 0
        refreshMap(selected, first, state.value.nodes.lastOrNull()?.position ?: first, jumpToCurrent)
    }
    private fun refreshMap(selected: Roadmap, first: Int, last: Int, jumpToCurrent: Boolean) {
        task({ refreshMap(selected, first, last, jumpToCurrent) }) {
            var after = first - 1
            var initial = true
            do {
                val page = repository.nodes(selected, after)
                setPage(page, !initial); initial = false
                after = page.nextPosition ?: break
            } while (after < last)
            if (jumpToCurrent) {
                val position = state.value.current
                if (position != null && state.value.nodes.none { it.position == position })
                    setPage(repository.nodes(selected, (position - 5).coerceAtLeast(0) - 1), false)
                change { it.copy(scrollTarget = position) }
            }
        }
    }
    fun beginStroke() { change { it.copy(drawing = true, candidates = emptyList(), writingResult = null) } }
    fun endStroke(stroke: HandwritingStroke?) {
        change { it.copy(drawing = false) }
        if (stroke == null || state.value.busy || pending != null) return
        if (state.value.strokes.sumOf { it.points.size } + stroke.points.size > 3000 || state.value.strokes.size >= 100) {
            change { it.copy(error = R.string.roadmap_ink_limit) }; return
        }
        setInk(state.value.strokes + stroke)
    }
    fun undo() { if (!state.value.busy && pending == null) setInk(state.value.strokes.dropLast(1)) }
    fun clearInk() { setInk(emptyList()) }
    private fun setInk(strokes: List<HandwritingStroke>) {
        saved[prefix + "ink"] = gson.toJson(strokes.map { stroke -> stroke.points.map {
            doubleArrayOf(it.x.toDouble(), it.y.toDouble(), it.timeMillis.toDouble())
        } })
        change { it.copy(strokes = strokes, candidates = emptyList(), writingResult = null) }
    }
    fun clearWritingResult() { change { it.copy(writingResult = null) } }
    /** The existing on-device API consumes timed strokes; only its first suggestion is graded. */
    fun checkWriting() = checkWriting(true)
    fun checkWriting(submitEvidence: Boolean) {
        val snapshot = state.value
        val activity = snapshot.activity
        val ink = snapshot.strokes
        val target = snapshot.lesson?.words?.getOrNull(snapshot.wordIndex)?.simplified ?: return
        if ((submitEvidence && activity?.kind != "HANDWRITING") || snapshot.busy || snapshot.deliveryPending ||
            snapshot.recognizing || snapshot.drawing || snapshot.writingResult == true || ink.isEmpty()) return
        val engine = recognizer ?: run {
            change { it.copy(error = R.string.roadmap_recognition_error) }; return
        }
        change { it.copy(recognizing = true, writingResult = null, error = null) }
        viewModelScope.launch {
            fun stillCurrent() = state.value.lesson?.nodeVersionId == snapshot.lesson.nodeVersionId &&
                state.value.run?.id == snapshot.run?.id && state.value.activity?.id == activity?.id && state.value.strokes == ink &&
                state.value.wordIndex == snapshot.wordIndex
            try {
                engine.prepareModel {}
                val results = engine.recognize(ink)
                if (!stillCurrent()) return@launch
                val correct = results.firstOrNull() == target
                if (correct && ink.sumOf { it.points.last().timeMillis - it.points.first().timeMillis } < 1000) {
                    change { it.copy(error = R.string.roadmap_write_more) }
                    return@launch
                }
                change { it.copy(writingResult = correct, writingFeedbackId = it.writingFeedbackId + 1,
                    writingFeedbackToken = UUID.randomUUID().toString()) }
                if (correct) {
                    if (submitEvidence) {
                        kotlinx.coroutines.delay(1200)
                        if (stillCurrent()) {
                            handwriting()
                        }
                        change { it.copy(writingResult = null) }
                    } else {
                        change { it.copy(writingSuccessToken = UUID.randomUUID().toString()) }
                    }
                }
            } catch (cancelled: CancellationException) { throw cancelled }
            catch (_: Exception) {
                if (stillCurrent()) change { it.copy(error = R.string.roadmap_recognition_error, writingResult = null) }
            } finally { change { it.copy(recognizing = false) } }
        }
    }
    fun recognize() {
        val recognizer = recognizer ?: return
        val ink = state.value.strokes
        if (ink.isEmpty() || state.value.recognizing || state.value.drawing) return
        change { it.copy(recognizing = true) }
        viewModelScope.launch {
            try {
                recognizer.prepareModel {}
                val results = handwritingCandidates(recognizer.recognize(ink))
                if (state.value.strokes == ink) change { it.copy(candidates = results) }
            } catch (cancelled: CancellationException) { throw cancelled }
            catch (_: Exception) { change { it.copy(error = R.string.roadmap_recognition_error) } }
            finally { change { it.copy(recognizing = false) } }
        }
    }
    suspend fun recognizeCharacter(strokes: List<HandwritingStroke>): String? {
        val engine = checkNotNull(recognizer)
        engine.prepareModel {}
        return engine.recognize(strokes).firstOrNull()
    }
    suspend fun media(assetId: String): RoadmapMedia {
        val nodeId = checkNotNull(state.value.lesson).nodeVersionId
        val key = "$nodeId/$assetId"
        mediaMutex.lock()
        try {
            return mediaCache[key] ?: repository.media(nodeId, assetId).also { media ->
                while (mediaCache.isNotEmpty() && mediaCache.values.sumOf { it.bytes.size } + media.bytes.size > 16 * 1024 * 1024)
                    mediaCache.remove(mediaCache.keys.first())
                mediaCache[key] = media
            }
        } catch (expired: SessionExpired) { change { it.copy(expired = true) }; throw expired }
        finally { mediaMutex.unlock() }
    }
    override fun onCleared() { recognizer?.close() }
}
