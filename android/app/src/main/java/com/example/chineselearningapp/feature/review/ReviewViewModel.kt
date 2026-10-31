package com.example.chineselearningapp.feature.review

import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.chineselearningapp.domain.repository.*
import com.example.chineselearningapp.feature.vocabulary.sessionExpired
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.*
import com.google.gson.Gson
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import retrofit2.HttpException
import java.util.UUID

enum class ReviewError { Network, Timeout, Server, Response, Expired, Invalid, Unavailable, StartUnknown, EmptyPlan }

internal fun reviewFailure(error: Exception): ReviewError = when {
    error is retrofit2.HttpException -> ReviewError.Server
    error is com.google.gson.JsonParseException || error is com.google.gson.stream.MalformedJsonException -> ReviewError.Response
    error is java.io.InterruptedIOException -> ReviewError.Timeout
    error is java.io.IOException -> ReviewError.Network
    else -> ReviewError.Response
}
data class ReviewUiState(val loading: Boolean = false, val dashboard: ReviewDashboard? = null,
    val targets: List<ReviewTarget> = emptyList(), val exclusions: List<ReviewExclusion> = emptyList(),
    val stage: ReviewStage? = null, val feedbackVisible: Boolean = false, val result: ReviewResult? = null,
    val previousMastery: Int? = null, val error: ReviewError? = null, val signedOut: Boolean = false,
    val completed: Int = 0, val sessionSize: Int = 0, val sessionOpen: Boolean = false,
    val summary: Boolean = false, val passed: Int = 0, val failed: Int = 0, val masteryChange: Int = 0,
    val skippedCount: Int = 0, val selectedStage: String? = null,
    val draftText: String = "", val draftSelections: List<String> = emptyList(),
    val queuedStages: Set<String> = emptySet(), val activeSeconds: Int = 0)

class ReviewViewModel(private val repository: ReviewRepository, private val saved: SavedStateHandle,
    owner: String, private val random: kotlin.random.Random = kotlin.random.Random.Default) : ViewModel() {
    private val mutableState = MutableStateFlow(ReviewUiState())
    val state = mutableState.asStateFlow()
    private var busy = false
    private val gson = Gson()
    private var preparation: Deferred<ReviewStage?>? = null
    private var transitionStarted: Long? = null
    private var renderStarted: Long? = null

    private var timingBusy = false
    private var timingEpoch = 0L
    internal fun timingWindow() = state.value.stage?.attemptId to timingEpoch
    private var lastInteraction = System.nanoTime()
    fun interaction() { lastInteraction = System.nanoTime() }
    suspend fun activeTick(elapsedMs: Long, window: Pair<String?, Long> = timingWindow()) {
        val current = state.value
        if (window != timingWindow() || timingBusy || current.loading || !current.sessionOpen || current.stage == null || current.error != null ||
            System.nanoTime() - lastInteraction > 30_000_000_000L || elapsedMs !in 1..6000) return
        val id = current.stage.attemptId
        val key = "active_$id"
        val total = (saved.get<Long>(key) ?: 0L) + elapsedMs
        timingBusy = true
        try {
            val accepted = repository.activeTime(id, total)
            val delta = accepted - (saved.get<Long>(key) ?: 0L)
            saved[key] = accepted
            val dashboard = state.value.dashboard
            val budget = dashboard?.dailyReview
            mutableState.value = state.value.copy(activeSeconds = (accepted / 1000).toInt(),
                dashboard = if (budget == null) dashboard else dashboard.copy(
                    dailyReview = budget.copy(activeSeconds = budget.activeSeconds + (delta / 1000).toInt())))
        } catch (cancelled: CancellationException) { throw cancelled }
        catch (_: Exception) { /* Timing failure is retryable and never grades an answer. */ }
        finally { timingBusy = false }
    }
    fun continueBeyondTarget() {
        if (busy) return
        discard()
        saved.remove<String>("planKey")
        saved["summary"] = false
        mutableState.value = state.value.copy(summary = false)
        start(true)
    }

    fun selectStage(stage: String) {
        if (stage !in listOf("HANZI", "PINYIN")) return
        saved["selectedStage"] = stage
        updateDraftState()
    }
    fun editDraft(text: String, selections: List<String>) {
        interaction()
        val stage = state.value.selectedStage ?: state.value.stage?.stage ?: return
        if (state.value.stage?.feedback?.any { it.stage == stage && it.firstCorrect != null } == true) return
        // Editing an unsent queued draft explicitly unseals the local draft.
        saved["queued_$stage"] = false
        saved["draft_$stage"] = text.take(500)
        saved["choices_$stage"] = ArrayList(selections)
        updateDraftState()
    }
    private fun updateDraftState() {
        val stage = saved.get<String>("selectedStage")?.takeIf { it in listOf("HANZI", "PINYIN") } ?: state.value.stage?.stage ?: "HANZI"
        mutableState.value = state.value.copy(selectedStage = stage,
            draftText = saved["draft_$stage"] ?: "",
            draftSelections = saved.get<ArrayList<String>>("choices_$stage").orEmpty(),
            queuedStages = listOf("HANZI", "PINYIN").filter { saved.get<Boolean>("queued_$it") == true }.toSet())
    }
    private fun clearDrafts() {
        saved.remove<String>("inkDraft")
        listOf("HANZI", "PINYIN").forEach {
            saved.remove<Any>("draft_$it"); saved.remove<Any>("choices_$it"); saved.remove<Any>("queued_$it")
        }
        saved.remove<Any>("selectedStage")
    }
    private fun accept(current: ReviewStage) {
        if (current.reviewVersion != "two-stage-v2") {
            mutableState.value = state.value.copy(stage = null, error = ReviewError.Unavailable)
            return
        }
        if (transitionStarted != null) {
            transitionStarted?.let { ReviewTiming.record("tap_to_state", it) }
            renderStarted = System.nanoTime()
        }
        mutableState.value = state.value.copy(activeSeconds = ((saved.get<Long>("active_${current.attemptId}") ?: 0L) / 1000).toInt(), stage = current, feedbackVisible = saved["feedback"] ?: false)
        updateDraftState()
    }
    fun rendered(attempt: String) {
        if (state.value.stage?.attemptId != attempt) return
        renderStarted?.let { ReviewTiming.record("state_to_frame", it); renderStarted = null }
        transitionStarted?.let { ReviewTiming.record("tap_to_interactive", it); transitionStarted = null }
    }

    init {
        if (saved.get<String>("owner") != owner) {
            saved.keys().toList().forEach { saved.remove<Any>(it) }
            saved["owner"] = owner
        }
        mutableState.value = state.value.copy(
            completed = saved["completed"] ?: 0, sessionSize = saved["size"] ?: 0,
            passed = saved["passed"] ?: 0, failed = saved["failed"] ?: 0,
            masteryChange = saved["change"] ?: 0, summary = saved["summary"] ?: false,
            skippedCount = saved["skippedCount"] ?: 0)
        retry()
    }
    private fun perform(block: suspend () -> Unit) {
        if (busy) return
        timingEpoch++
        busy = true
        mutableState.value = state.value.copy(loading = true, error = null)
        viewModelScope.launch {
            try { block() }
            catch (cancelled: CancellationException) { throw cancelled }
            catch (error: Exception) {
                ReviewTiming.failure("operation", error)
                val code = (error as? HttpException)?.code()
                mutableState.value = state.value.copy(signedOut = error.sessionExpired(), error = when {
                    saved.get<Boolean>("starting") == true && saved.get<String>("creationKey") == null -> ReviewError.StartUnknown
                    code == 410 || code == 429 -> ReviewError.Expired
                    code == 422 -> ReviewError.Invalid
                    code == 404 || code == 409 -> ReviewError.Unavailable
                    else -> reviewFailure(error)
                })
                if (code == 422) {
                    saved.get<String>("pendingStage")?.let { saved["queued_$it"] = false }
                    clearPending(); updateDraftState()
                }
            } finally { busy = false; mutableState.value = state.value.copy(loading = false) }
        }
    }
    private suspend fun dashboard() {
        val counts = state.value.dashboard ?: repository.dashboard()
        val targets = if (counts.dailyReview != null) ReviewTargets(
            if (counts.due > 0 || counts.dailyReview.pendingCount > 0) listOf(ReviewTarget("planner", true)) else emptyList(), emptyList())
            else repository.targets()
        val queue = saved.get<ArrayList<String>>("queue")
        mutableState.value = state.value.copy(dashboard = counts,
            targets = targets.items.filter { it.due && (queue == null || it.savedId in queue) }, exclusions = targets.excluded)
    }
    fun refresh() { if (!state.value.sessionOpen) perform {
        // Completed/empty plans must not pin future starts to an old response.
        if (!hasAttempt() && saved.get<ArrayList<String>>("queue").isNullOrEmpty()) saved.remove<String>("planKey")
        mutableState.value = state.value.copy(dashboard = null)
        dashboard()
    } }
    fun onResume() {
        if (!state.value.sessionOpen) refresh()
        else if (state.value.result == null && (state.value.stage == null || state.value.error != null ||
                pending() != null || state.value.stage?.let(::expired) == true)) retry()
    }
    fun retry() = perform {
        if (state.value.dashboard == null) mutableState.value = state.value.copy(dashboard = repository.dashboard())
        if (saved.get<Boolean>("summary") == true) {
            mutableState.value = state.value.copy(sessionOpen = true, summary = true)
            return@perform
        }
        if (saved.get<Boolean>("starting") == true) {
            val key = saved.get<String>("creationKey")
            mutableState.value = state.value.copy(sessionOpen = true)
            if (key == null) mutableState.value = state.value.copy(error = ReviewError.StartUnknown)
            else createAttempt(checkNotNull(saved["savedId"]), key)
            return@perform
        }
        saved.get<String>("result")?.let {
            mutableState.value = state.value.copy(sessionOpen = true, result = gson.fromJson(it, ReviewResult::class.java))
            prepareNext()
            return@perform
        }
        val id = saved.get<String>("attempt")
        if (id == null) {
            if (!saved.get<ArrayList<String>>("queue").isNullOrEmpty()) {
                beginNext()
                return@perform
            }
            mutableState.value = state.value.copy(sessionOpen = false)
            dashboard()
        } else {
            mutableState.value = state.value.copy(sessionOpen = true)
            val pending = pending()
            if (pending != null) { send(id, pending); flushDrafts(id) } else { reconcile(id); flushDrafts(id) }
        }
    }
    fun start(beyond: Boolean = false) {
        if (busy || state.value.sessionOpen || hasAttempt()) return
        perform {
            val planKey = saved.get<String>("planKey") ?: UUID.randomUUID().toString().also { saved["planKey"] = it }
            val selected = repository.dailyPlan(planKey, beyond).items.filter { it.due }.map { it.savedId }.distinct()
            val queue = if (state.value.dashboard?.dailyReview == null) selected.shuffled(random) else selected
            saved["queue"] = ArrayList(queue)
            saved["size"] = queue.size; saved["completed"] = 0
            saved["passed"] = 0; saved["failed"] = 0; saved["change"] = 0; saved["summary"] = false
            saved["skippedCount"] = 0
            mutableState.value = state.value.copy(sessionSize = queue.size, completed = 0, passed = 0,
                failed = 0, masteryChange = 0, summary = false, skippedCount = 0)
            if (queue.isEmpty()) {
                saved.remove<Any>("queue")
                saved.remove<String>("planKey")
                mutableState.value = state.value.copy(dashboard = null)
                dashboard()
                mutableState.value = state.value.copy(error = ReviewError.EmptyPlan)
            } else beginNext()
        }
    }
    private fun startNext() = perform { beginNext() }
    private suspend fun beginNext() {
        val savedId = saved.get<ArrayList<String>>("queue")?.firstOrNull()
        if (savedId == null) {
            saved.remove<String>("planKey")
            saved["summary"] = true
            mutableState.value = state.value.copy(sessionOpen = true, summary = true)
            return
        }
        val preparedId = saved.get<String>("nextSavedId")
        saved["savedId"] = savedId
        clearDrafts()
        mutableState.value = state.value.copy(previousMastery = null, sessionOpen = true,
            stage = null, result = null, feedbackVisible = false, selectedStage = "HANZI",
            draftText = "", draftSelections = emptyList(), queuedStages = emptySet())
        if (preparedId == savedId) {
            val key = checkNotNull(saved.get<String>("nextKey"))
            saved["creationKey"] = key; saved["starting"] = true
            val ready = try {
                preparation?.await() ?: saved.get<String>("nextQuestion")?.let { gson.fromJson(it, ReviewStage::class.java) }
            } catch (cancelled: CancellationException) { throw cancelled }
            catch (_: Exception) { null }
            clearPreparation()
            if (ready != null && !expired(ready)) {
                saved["attempt"] = ready.attemptId; saved["starting"] = false; accept(ready)
            } else createAttempt(savedId, key)
        } else {
            val key = UUID.randomUUID().toString()
            saved["creationKey"] = key; saved["starting"] = true
            createAttempt(savedId, key)
        }
    }
    private fun expired(stage: ReviewStage): Boolean = runCatching {
        val normalized = stage.expiresAt.replace(Regex("\\.\\d+"), "")
        val parser = java.text.SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ssXXX", java.util.Locale.ROOT)
        checkNotNull(parser.parse(normalized)).time <= System.currentTimeMillis()
    }.getOrDefault(false)
    private fun clearPreparation() {
        preparation = null
        listOf("nextSavedId", "nextKey", "nextQuestion").forEach { saved.remove<Any>(it) }
    }
    private fun prepareNext() {
        val next = saved.get<ArrayList<String>>("queue")?.firstOrNull() ?: return
        if (preparation != null || saved.get<String>("nextQuestion") != null) return
        if (saved.get<String>("nextSavedId") != next) {
            saved["nextSavedId"] = next; saved["nextKey"] = UUID.randomUUID().toString()
        }
        val key = checkNotNull(saved.get<String>("nextKey"))
        preparation = viewModelScope.async {
            val startedAt = System.nanoTime()
            try {
                val started = repository.start(next, key)
                check(started.gradingAvailable)
                repository.question(started.attemptId).also { saved["nextQuestion"] = gson.toJson(it) }
            } catch (cancelled: CancellationException) { throw cancelled }
            catch (_: Exception) { null }
            finally { ReviewTiming.record("next_preparation", startedAt) }
        }
        // Deferred failures are consumed on Continue; never create an unhandled launch failure.
    }
    private suspend fun createAttempt(savedId: String, key: String) {
        val started = try { repository.start(savedId, key) }
        catch (error: Exception) {
            // Retain the creation key through ambiguous network/server failures.
            if (error is HttpException && error.code() in 400..499 || error.sessionExpired()) saved["starting"] = false
            throw error
        }
        saved["attempt"] = started.attemptId
        saved["starting"] = false
        if (!started.gradingAvailable) {
            mutableState.value = state.value.copy(error = ReviewError.Unavailable)
        } else reconcile(started.attemptId)
    }
    fun submit(text: String, selections: List<String>, handwriting: ReviewInkEvidence? = null) {
        val current = state.value.stage ?: return
        val stage = state.value.selectedStage ?: current.stage ?: return
        val question = current.draftQuestions[stage] ?: current.question?.takeIf { current.stage == stage } ?: return
        if (busy || pending() != null || state.value.error != null || current.feedback.any { it.stage == stage && it.firstCorrect != null }) return
        if (text.isBlank() || stage == "HANZI" && handwriting == null) return
        if (stage == "HANZI") saved["inkDraft"] = gson.toJson(handwriting)
        saved["selectedStage"] = stage
        editDraft(text, selections)
        saved["queued_$stage"] = true
        updateDraftState()
        if (stage == current.stage) perform { flushDrafts(checkNotNull(saved["attempt"])) }
    }
    private suspend fun flushDrafts(id: String) {
        while (true) {
            val current = state.value.stage ?: return
            val stage = current.stage ?: return
            if (saved.get<Boolean>("queued_$stage") != true) return
            val question = current.question ?: return
            val pos = question.inputMode != "TEXT"
            val body = ReviewSubmission(UUID.randomUUID().toString(), stage,
                if (pos) null else saved["draft_$stage"],
                if (pos) saved.get<ArrayList<String>>("choices_$stage")?.filter { it in question.options } else null,
                if (stage == "HANZI") saved.get<String>("inkDraft")?.let { gson.fromJson(it, ReviewInkEvidence::class.java) } else null)
            saved["key"] = body.key; saved["pendingStage"] = stage
            saved["text"] = body.text; saved["selections"] = body.selections?.let { ArrayList(it) }
            send(id, body)
            if (state.value.stage?.stage == stage) return
        }
    }
    private fun pending(): ReviewSubmission? = saved.get<String>("key")?.let {
        ReviewSubmission(it, checkNotNull(saved["pendingStage"]), saved["text"], saved.get<ArrayList<String>>("selections"),
            (saved.get<String>("pendingInk") ?: saved.get<String>("inkDraft")?.takeIf { saved.get<String>("pendingStage") == "HANZI" })?.let { json -> gson.fromJson(json, ReviewInkEvidence::class.java) })
    }
    private fun clearPending() {
        listOf("key", "pendingStage", "text", "selections", "pendingInk").forEach { saved.remove<Any>(it) }
    }
    private suspend fun send(id: String, body: ReviewSubmission) {
        try { accept(repository.submitAndQuestion(id, body)) }
        catch (error: HttpException) {
            if (error.code() != 409) throw error
            clearPending(); reconcile(id); return
        }
        saved["queued_${body.stage}"] = false
        clearPending()
        updateDraftState()
        saved["feedback"] = true
        mutableState.value = state.value.copy(feedbackVisible = true)
    }
    private suspend fun reconcile(id: String) {
        val current = repository.question(id)
        accept(current)
        if (current.status == "COMPLETED") finish(id)
    }
    fun continueReview() {
        if (busy) return
        saved["feedback"] = false
        mutableState.value = state.value.copy(feedbackVisible = false)
        if (state.value.stage?.status in listOf("READY_TO_FINALIZE", "COMPLETED")) perform { finish(checkNotNull(saved["attempt"])) }
        else state.value.stage?.stage?.let { selectStage(it) }
    }
    private suspend fun finish(id: String) {
        val startedAt = System.nanoTime()
        val result = try { repository.finalize(id) } finally { ReviewTiming.record("finalize", startedAt) }
        saved["result"] = gson.toJson(result)
        if (saved.get<String>("counted") != id) {
            saved["completed"] = state.value.completed + 1
            val pass = result.outcome == "PASS"
            saved["passed"] = state.value.passed + if (pass) 1 else 0
            saved["failed"] = state.value.failed + if (pass) 0 else 1
            saved["change"] = state.value.masteryChange + if (result.schedulingApplied && result.previousMastery != null)
                result.mastery - result.previousMastery else 0
            saved["counted"] = id
        }
        saved.get<ArrayList<String>>("queue")?.let { queue ->
            saved["queue"] = ArrayList(queue.filterNot { it == saved.get<String>("savedId") })
        }
        mutableState.value = state.value.copy(result = result, previousMastery = result.previousMastery,
            stage = null, feedbackVisible = false,
            completed = saved["completed"] ?: 0, passed = saved["passed"] ?: 0,
            failed = saved["failed"] ?: 0, masteryChange = saved["change"] ?: 0)
        prepareNext()
    }
    fun leave() {
        if (busy) return
        // Leaving an unfinished attempt retains its identity; dashboard offers resume.
        mutableState.value = state.value.copy(sessionOpen = false)
        if (state.value.summary) {
            saved["summary"] = false
            mutableState.value = state.value.copy(summary = false)
        }
        if (!hasAttempt()) saved.remove<Any>("queue")
        refresh()
    }
    fun resume() { mutableState.value = state.value.copy(sessionOpen = true); retry() }
    fun hasAttempt() = saved.get<String>("attempt") != null || saved.get<Boolean>("starting") == true
    fun restart() {
        if (busy) return
        perform {
        saved.get<String>("attempt")?.let { repository.defer(it) }
        discard()
        val queue = saved.get<ArrayList<String>>("queue")
        if (queue != null && state.value.sessionSize > 0) {
            saved["queue"] = ArrayList(queue.filterNot { it == saved.get<String>("savedId") })
            saved["skippedCount"] = state.value.skippedCount + 1
            mutableState.value = state.value.copy(skippedCount = saved["skippedCount"] ?: 0)
            beginNext()
            return@perform
        }
        saved.remove<Any>("queue")
        dashboard()
        }
    }
    private fun discard() {
        listOf("attempt", "starting", "creationKey", "feedback", "mastery", "result").forEach { saved.remove<Any>(it) }
        clearPending()
        mutableState.value = state.value.copy(sessionOpen = false, stage = null, result = null, error = null)
    }
    fun next() {
        if (busy || state.value.result == null) return
        val budget = state.value.dashboard?.dailyReview
        if (budget != null && budget.activeSeconds >= budget.targetSeconds) {
            saved["summary"] = true
            mutableState.value = state.value.copy(summary = true, result = null)
            return
        }
        transitionStarted = System.nanoTime()
        discard(); startNext()
    }
}
