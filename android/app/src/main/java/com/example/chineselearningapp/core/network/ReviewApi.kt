package com.example.chineselearningapp.core.network

import com.google.gson.annotations.SerializedName
import retrofit2.http.*

interface ReviewApi {
    @POST("api/v1/me/srs/sessions/{id}/defer") suspend fun defer(@Header("Authorization") auth: String, @Path("id") id: String)
    @POST("api/v1/me/srs/daily-plans") suspend fun dailyPlan(@Header("Authorization") auth: String, @Body body: ReviewPlanBody): ReviewTargetsDto
    @POST("api/v1/me/srs/sessions/{id}/active-time") suspend fun activeTime(@Header("Authorization") auth: String, @Path("id") id: String, @Body body: ReviewTimeBody): ReviewTimeBody
    @GET("api/v1/me/srs/dashboard") suspend fun dashboard(@Header("Authorization") auth: String): ReviewDashboardDto
    @GET("api/v1/me/srs/due?limit=100") suspend fun due(@Header("Authorization") auth: String): ReviewDueDto
    @GET("api/v1/me/srs/review-targets?limit=100") suspend fun targets(@Header("Authorization") auth: String, @Query("offset") offset: Int): ReviewTargetsDto
    @GET("api/v1/me/srs/progress/{id}") suspend fun progress(@Header("Authorization") auth: String, @Path("id") id: String): ReviewProgressDto
    @POST("api/v1/me/srs/sessions") suspend fun start(@Header("Authorization") auth: String, @Body body: ReviewStartBody): ReviewStartDto
    @GET("api/v1/me/srs/sessions/{id}/question") suspend fun question(@Header("Authorization") auth: String, @Path("id") id: String): ReviewStageDto
    @POST("api/v1/me/srs/sessions/{id}/submissions") suspend fun submit(@Header("Authorization") auth: String, @Path("id") id: String, @Body body: ReviewSubmissionDto): ReviewStageDto
    @POST("api/v1/me/srs/sessions/{id}/finalize") suspend fun finalize(@Header("Authorization") auth: String, @Path("id") id: String, @Body body: Map<String, String> = emptyMap()): ReviewResultDto
}
data class ReviewDashboardDto(@SerializedName("available_count") val available: Int, @SerializedName("due_count") val due: Int,
    @SerializedName("suspended_count") val suspended: Int, @SerializedName("grading_available") val gradingAvailable: Boolean,
    @SerializedName("mastery_distribution") val masteryDistribution: List<ReviewMasteryCountDto>?,
    @SerializedName("daily_review") val dailyReview: DailyBudgetDto? = null)

data class ReviewPlanBody(@SerializedName("request_id") val requestId: String,
    @SerializedName("continue_beyond_target") val beyond: Boolean)
data class ReviewTimeBody(@SerializedName("active_ms") val activeMs: Long)
data class DailyBudgetDto(@SerializedName("target_seconds") val targetSeconds: Int,
    @SerializedName("active_seconds") val activeSeconds: Int,
    @SerializedName("overdue_count") val overdueCount: Int,
    @SerializedName("pending_count") val pendingCount: Int,
    @SerializedName("estimated_backlog_seconds") val estimatedBacklogSeconds: Int)
data class ReviewMasteryCountDto(@SerializedName("mastery_level") val level: Int, val count: Int)
data class ReviewProgressDto(@SerializedName("saved_id") val savedId: String, @SerializedName("mastery_level") val mastery: Int,
    @SerializedName("next_review_at") val nextReviewAt: String)
data class ReviewDueDto(val items: List<ReviewProgressDto>)
data class ReviewTargetDto(@SerializedName("saved_id") val savedId: String, val due: Boolean)
data class ReviewExclusionDto(@SerializedName("saved_id") val savedId: String, val reason: String)
data class ReviewTargetsDto(val items: List<ReviewTargetDto>, val excluded: List<ReviewExclusionDto>)
data class ReviewStartBody(@SerializedName("saved_id") val savedId: String, @SerializedName("request_id") val requestId: String)
data class ReviewStartDto(@SerializedName("attempt_id") val attemptId: String, @SerializedName("grading_available") val gradingAvailable: Boolean)
data class ReviewQuestionDto(@SerializedName("input_mode") val inputMode: String, @SerializedName("prompt_vi") val prompt: String?,
    val simplified: String?, val options: List<String>?, @SerializedName("character_count") val characterCount: Int?)
data class ReviewFeedbackDto(val stage: String, @SerializedName("first_correct") val firstCorrect: Boolean?, val assisted: Boolean,
    @SerializedName("correct_answer") val correctAnswer: List<String>?,
    @SerializedName("tone_mismatches") val toneMismatches: List<Int>?,
    @SerializedName("syllable_mismatches") val syllableMismatches: List<Int>?)
data class ReviewStageDto(@SerializedName("attempt_id") val attemptId: String, val stage: String?, val status: String,
    @SerializedName("expires_at") val expiresAt: String, val question: ReviewQuestionDto?, val feedback: List<ReviewFeedbackDto>,
    @SerializedName("skipped_stages") val skipped: List<Map<String, String>>,
    @SerializedName("draft_questions") val draftQuestions: Map<String, ReviewQuestionDto>?,
    @SerializedName("review_version") val reviewVersion: String? = null)
data class ReviewSubmissionDto(@SerializedName("submission_key") val key: String, val stage: String, val answer: Any,
    val handwriting: com.example.chineselearningapp.domain.repository.ReviewInkEvidence? = null)
data class ReviewStateDto(@SerializedName("mastery_level") val mastery: Int, @SerializedName("next_review_at") val nextReviewAt: String)
data class ReviewResultDto(val outcome: String, @SerializedName("state_after") val state: ReviewStateDto,
    @SerializedName("scheduling_applied") val schedulingApplied: Boolean,
    @SerializedName("previous_mastery_level") val previousMastery: Int?,
    @SerializedName("resulting_mastery_level") val resultingMastery: Int?)
