package com.example.chineselearningapp.core.network

import com.google.gson.annotations.SerializedName
import okhttp3.ResponseBody
import retrofit2.http.*

interface RoadmapApi {
    @GET("api/v1/roadmaps") suspend fun catalog(@Header("Authorization") auth: String, @Query("offset") offset: Int): RoadmapCatalogDto
    @GET("api/v1/roadmaps/{id}/nodes") suspend fun nodes(@Header("Authorization") auth: String,
        @Path("id") id: String, @Query("version_id") version: String, @Query("after") after: Int): RoadmapPageDto
    @GET("api/v1/roadmap-nodes/{id}") suspend fun lesson(@Header("Authorization") auth: String, @Path("id") id: String): RoadmapLessonDto
    @POST("api/v1/roadmap-nodes/{id}/start") suspend fun start(@Header("Authorization") auth: String, @Path("id") id: String, @Body body: RoadmapStartDto): RoadmapRunDto
    @POST("api/v1/roadmap-nodes/{id}/skip") suspend fun skip(@Header("Authorization") auth: String, @Path("id") id: String): RoadmapCompletionDto
    @POST("api/v1/roadmap-runs/{id}/activities") suspend fun submit(@Header("Authorization") auth: String, @Path("id") id: String, @Body body: RoadmapEvidenceDto): RoadmapReceiptDto
    @POST("api/v1/roadmap-runs/{id}/complete") suspend fun complete(@Header("Authorization") auth: String, @Path("id") id: String): RoadmapCompletionDto
    @GET("api/v1/roadmap-nodes/{id}/assets/{asset}") suspend fun media(@Header("Authorization") auth: String, @Path("id") id: String, @Path("asset") asset: String): ResponseBody
}
data class RoadmapDto(val id: String, @SerializedName("version_id") val versionId: String, val title: String)
data class RoadmapCatalogDto(val items: List<RoadmapDto>, @SerializedName("next_offset") val nextOffset: Int?)
data class RoadmapNodeDto(val id: String, @SerializedName("node_version_id") val versionId: String, val position: Int,
    @SerializedName("node_type") val type: String, val title: String, val section: String, val status: String, val available: Boolean)
data class RoadmapPageDto(@SerializedName("roadmap_version_id") val versionId: String, val items: List<RoadmapNodeDto>,
    @SerializedName("next_position") val nextPosition: Int?, @SerializedName("current_position") val currentPosition: Int?,
    @SerializedName("section_positions") val sections: Map<String, Int>?)
data class RoadmapEnrichmentDto(val status: String = "UNAVAILABLE", val text: String? = null, @SerializedName("asset_id") val assetId: String? = null)
data class RoadmapComponentDto(@SerializedName("character_position") val position: Int, val component: String, val role: String, val explanation: RoadmapEnrichmentDto)
data class RoadmapActivityDto(val id: String, val kind: String, val required: Boolean, val prompt: String, val repetitions: Int, val options: List<String>)
data class RoadmapWordDto(@SerializedName("vocabulary_id") val id: String, @SerializedName("content_version") val version: Int,
    val simplified: String, val pinyin: String, @SerializedName("vietnamese_meanings") val meanings: List<String>,
    @SerializedName("sino_vietnamese") val sinoVietnamese: String?, val examples: List<RoadmapExampleDto>? = null)

data class RoadmapExampleDto(val simplified: String, val pinyin: String, val vietnamese: String)
data class ExerciseItemDto(
    @SerializedName("answer") val answer: String? = null,
    @SerializedName("distractors") val distractors: List<String>? = null
)
data class ListeningExerciseDto(
    @SerializedName("items") val items: List<ExerciseItemDto>? = null,
    @SerializedName("skipSecond") val skipSecond: Boolean = false
)
data class LessonExercisesDto(
    @SerializedName("listening") val listening: ListeningExerciseDto? = null,
    @SerializedName("skipSecond") val skipSecond: Boolean = false
)

data class RoadmapDefinitionDto(@SerializedName("node_type") val type: String, val title: String, val lesson: RoadmapContentDto)
data class RoadmapContentDto(val activities: List<RoadmapActivityDto>, val audio: RoadmapEnrichmentDto, val examples: RoadmapEnrichmentDto,
    val notes: RoadmapEnrichmentDto, @SerializedName("stroke_order") val strokeOrder: RoadmapEnrichmentDto, val components: List<RoadmapComponentDto>,
    val exercises: LessonExercisesDto? = null)
data class RoadmapLessonDto(@SerializedName("node_version_id") val nodeVersionId: String, @SerializedName("lesson_version_id") val lessonVersionId: String,
    val definition: RoadmapDefinitionDto, val vocabulary: List<RoadmapWordDto>)
data class RoadmapStartDto(val replay: Boolean, @SerializedName("request_id") val requestId: String?)
data class RoadmapRunDto(val id: String, @SerializedName("node_version_id") val nodeVersionId: String, val replay: Boolean,
    @SerializedName("completed_at") val completedAt: String?, @SerializedName("accepted_repetitions") val accepted: Map<String, List<Int>>?)
data class RoadmapPointDto(val x: Float, val y: Float)
data class RoadmapEvidenceDto(@SerializedName("request_id") val requestId: String, @SerializedName("activity_id") val activityId: String,
    val kind: String, val repetition: Int, val choice: Int?, val strokes: List<List<RoadmapPointDto>>, @SerializedName("duration_ms") val durationMs: Int)
data class RoadmapReceiptDto(val accepted: Boolean)
data class RoadmapCompletionDto(val status: String, @SerializedName("exp_awarded") val exp: Int)
