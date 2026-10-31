package com.example.chineselearningapp.feature.review

import com.example.chineselearningapp.core.network.*
import com.example.chineselearningapp.domain.repository.*
import com.example.chineselearningapp.feature.auth.data.RemoteSessionRepository
import javax.inject.Inject

class RemoteReviewRepository @Inject constructor(private val api: ReviewApi, private val session: RemoteSessionRepository) : ReviewRepository {
    override suspend fun defer(attemptId: String) { session.authorized { api.defer(it, attemptId) } }
    override suspend fun dailyPlan(requestId: String, beyond: Boolean) = session.authorized { api.dailyPlan(it, ReviewPlanBody(requestId, beyond)) }.let {
        ReviewTargets(it.items.map { item -> ReviewTarget(item.savedId, item.due) }, emptyList())
    }
    override suspend fun activeTime(attemptId: String, activeMs: Long) = session.authorized {
        api.activeTime(it, attemptId, ReviewTimeBody(activeMs))
    }.activeMs
    override suspend fun dashboard() = session.authorized { api.dashboard(it) }.let { ReviewDashboard(it.available, it.due, it.suspended, it.gradingAvailable,
        it.masteryDistribution?.map { bucket -> ReviewMasteryCount(bucket.level, bucket.count) },
        it.dailyReview?.let { budget -> DailyReviewBudget(budget.targetSeconds, budget.activeSeconds,
            budget.overdueCount, budget.pendingCount, budget.estimatedBacklogSeconds) }) }
    override suspend fun due() = session.authorized { api.due(it) }.items.map { it.domain() }
    override suspend fun progress(savedId: String) = session.authorized { api.progress(it, savedId) }.domain()
    override suspend fun targets(): ReviewTargets {
        val items = mutableListOf<ReviewTarget>(); val excluded = mutableListOf<ReviewExclusion>()
        var offset = 0
        do {
            val page = session.authorized { api.targets(it, offset) }
            // Dashboard needs availability, not an unbounded private catalog in memory.
            items += page.items.filter { it.due }.take((20 - items.size).coerceAtLeast(0)).map { ReviewTarget(it.savedId, it.due) }
            excluded += page.excluded.take((100 - excluded.size).coerceAtLeast(0)).map { ReviewExclusion(it.savedId, it.reason) }
            offset += 100
        } while (page.items.size + page.excluded.size == 100)
        return ReviewTargets(items, excluded)
    }
    override suspend fun start(savedId: String, requestId: String) = timed("create_request") {
        session.authorized { api.start(it, ReviewStartBody(savedId, requestId)) }.let { ReviewStart(it.attemptId, it.gradingAvailable) }
    }
    override suspend fun question(attemptId: String) = timed("question_request") {
        session.authorized { api.question(it, attemptId) }.domain()
    }
    override suspend fun submitAndQuestion(attemptId: String, submission: ReviewSubmission): ReviewStage {
        suspend fun send() = timed("submit_request") {
            session.authorized { auth ->
                try { api.submit(auth, attemptId, ReviewSubmissionDto(submission.key, submission.stage,
                    submission.selections ?: checkNotNull(submission.text), submission.handwriting)) }
                catch (failure: java.io.IOException) {
                    if (failure is com.google.gson.stream.MalformedJsonException) throw failure
                    throw SubmissionDeliveryUnknown(failure)
                }
            }.domain()
        }
        val result = try { send() }
        catch (cancelled: kotlinx.coroutines.CancellationException) { throw cancelled }
        catch (failure: SubmissionDeliveryUnknown) {
            // Only API transport failures qualify; credential-vault IO must not replay refresh.
            // The first request may already have committed. Read before replaying anything.
            val current = question(attemptId)
            if (current.feedback.any { it.stage == submission.stage && it.firstCorrect != null }) {
                current
            } else if (current.status == "IN_PROGRESS" && current.stage == submission.stage) {
                // One bounded replay, with the exact original key/body. A second failure
                // propagates; the VM keeps its pending submission for explicit retry.
                send()
            } else {
                throw failure
            }
        }
        return if (result.feedback.any { it.stage == submission.stage && it.firstCorrect != null }) result
            else question(attemptId)
    }
    override suspend fun submit(attemptId: String, submission: ReviewSubmission) {
        session.authorized { api.submit(it, attemptId, ReviewSubmissionDto(submission.key, submission.stage,
            submission.selections ?: checkNotNull(submission.text), submission.handwriting)) }
        // Compatibility method for clients that fetch their own current question.
    }
    private suspend fun <T> timed(event: String, block: suspend () -> T): T {
        val startedAt = System.nanoTime()
        try { return block() }
        catch (cancelled: kotlinx.coroutines.CancellationException) { throw cancelled }
        catch (error: Exception) { ReviewTiming.failure(event, error); throw error }
        finally { ReviewTiming.record(event, startedAt) }
    }
    override suspend fun finalize(attemptId: String) = session.authorized { api.finalize(it, attemptId) }.let {
        ReviewResult(it.outcome, it.resultingMastery ?: it.state.mastery, it.state.nextReviewAt, it.schedulingApplied, it.previousMastery)
    }
}
private fun ReviewProgressDto.domain() = ReviewProgress(savedId, mastery, nextReviewAt)

private fun ReviewQuestionDto.domain() = ReviewQuestion(inputMode, prompt, simplified, options.orEmpty(), characterCount)
private fun ReviewStageDto.domain() = ReviewStage(attemptId, stage, status, expiresAt, question?.domain(),
    feedback.map { ReviewFeedback(it.stage, it.firstCorrect, it.assisted, it.correctAnswer.orEmpty(), it.toneMismatches.orEmpty(), it.syllableMismatches.orEmpty()) },
    skipped.mapNotNull { it["reason"] }, draftQuestions.orEmpty().mapValues { it.value.domain() }, reviewVersion ?: "three-stage-v1")

/** Marks API delivery failures separately from credential-vault or response-format errors. */
private class SubmissionDeliveryUnknown(cause: java.io.IOException) : java.io.IOException(cause)
