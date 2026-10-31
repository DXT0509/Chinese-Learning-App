package com.example.chineselearningapp.domain.repository

data class ReviewMasteryCount(val level: Int, val count: Int)
data class ReviewDashboard(val available: Int, val due: Int, val suspended: Int, val gradingAvailable: Boolean,
    val masteryDistribution: List<ReviewMasteryCount>? = null, val dailyReview: DailyReviewBudget? = null)

data class DailyReviewBudget(val targetSeconds: Int = 1200, val activeSeconds: Int = 0,
    val overdueCount: Int = 0, val pendingCount: Int = 0, val estimatedBacklogSeconds: Int = 0)
data class ReviewInkPoint(val x: Float, val y: Float, val t: Long)
data class ReviewInkCharacter(val strokes: List<List<ReviewInkPoint>>, val candidates: List<String>, val selected: String)
data class ReviewInkEvidence(val recognizer: String = "MLKIT_DIGITAL_INK_ZH_HANS_V1", val characters: List<ReviewInkCharacter>)
data class ReviewTarget(val savedId: String, val due: Boolean)
data class ReviewExclusion(val savedId: String, val reason: String)
data class ReviewTargets(val items: List<ReviewTarget>, val excluded: List<ReviewExclusion>)
data class ReviewProgress(val savedId: String, val mastery: Int, val nextReviewAt: String)
data class ReviewStart(val attemptId: String, val gradingAvailable: Boolean)
data class ReviewQuestion(val inputMode: String, val prompt: String?, val simplified: String?, val options: List<String>,
    val characterCount: Int? = null)
data class ReviewFeedback(val stage: String, val firstCorrect: Boolean?, val assisted: Boolean, val correctAnswer: List<String>,
    val toneMismatches: List<Int> = emptyList(), val syllableMismatches: List<Int> = emptyList())
data class ReviewStage(val attemptId: String, val stage: String?, val status: String, val expiresAt: String,
    val question: ReviewQuestion?, val feedback: List<ReviewFeedback>, val skipped: List<String>,
    val draftQuestions: Map<String, ReviewQuestion> = emptyMap(), val reviewVersion: String = "two-stage-v2")
data class ReviewSubmission(val key: String, val stage: String, val text: String?, val selections: List<String>?,
    val handwriting: ReviewInkEvidence? = null)
data class ReviewResult(val outcome: String, val mastery: Int, val nextReviewAt: String, val schedulingApplied: Boolean,
    val previousMastery: Int? = null)

interface ReviewRepository {
    suspend fun dashboard(): ReviewDashboard
    suspend fun due(): List<ReviewProgress>
    suspend fun targets(): ReviewTargets
    suspend fun sessionTargets(): ReviewTargets = targets()
    suspend fun dailyPlan(requestId: String, beyond: Boolean): ReviewTargets = sessionTargets()
    suspend fun defer(attemptId: String) = Unit
    suspend fun activeTime(attemptId: String, activeMs: Long): Long = activeMs
    suspend fun progress(savedId: String): ReviewProgress
    suspend fun start(savedId: String, requestId: String): ReviewStart
    suspend fun question(attemptId: String): ReviewStage
    suspend fun submit(attemptId: String, submission: ReviewSubmission)
    suspend fun submitAndQuestion(attemptId: String, submission: ReviewSubmission): ReviewStage {
        submit(attemptId, submission)
        return question(attemptId)
    }
    suspend fun finalize(attemptId: String): ReviewResult
}
