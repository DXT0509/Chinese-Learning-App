package com.example.chineselearningapp.core.network

import com.google.gson.JsonObject
import com.google.gson.annotations.SerializedName
import retrofit2.http.*

data class CredentialsDto(val email: String, val password: String)
data class RefreshDto(@SerializedName("refresh_token") val token: String)
data class TokensDto(
    @SerializedName("access_token") val access: String,
    @SerializedName("refresh_token") val refresh: String
)
data class AccountDto(val id: String, val email: String?, @SerializedName("display_name") val displayName: String? = null)
data class LessonDto(@SerializedName("lesson_version_id") val versionId: String, val title: String, val version: Int = 1)
data class StartDto(
    @SerializedName("lesson_version_id") val versionId: String,
    @SerializedName("request_id") val requestId: String,
    @SerializedName("allow_preview") val allowPreview: Boolean = true
)
data class CheckpointDto(@SerializedName("scene_key") val key: String, val page: Int)
data class PageDto(val page: Int)
data class RunDto(val id: String, @SerializedName("lesson_version_id") val versionId: String, val checkpoints: List<CheckpointDto>, @SerializedName("current_scene_key") val currentSceneKey: String? = null)

interface SessionApi {
    @POST("api/v1/auth/register") suspend fun register(@Body data: CredentialsDto): TokensDto
    @POST("api/v1/auth/login") suspend fun login(@Body data: CredentialsDto): TokensDto
    @POST("api/v1/auth/refresh") suspend fun refresh(@Body data: RefreshDto): TokensDto
    @POST("api/v1/auth/logout") suspend fun logout(@Body data: RefreshDto)
    @GET("api/v1/auth/me") suspend fun me(@Header("Authorization") auth: String): AccountDto
    @GET("api/v1/lessons") suspend fun catalog(@Header("Authorization") auth: String): List<LessonDto>
    @GET("api/v1/learning-runs") suspend fun runs(@Header("Authorization") auth: String): List<RunDto>
    @POST("api/v1/learning-runs") suspend fun start(@Header("Authorization") auth: String, @Body data: StartDto): RunDto
    @GET("api/v1/learning-runs/{id}") suspend fun resume(@Header("Authorization") auth: String, @Path("id") id: String): RunDto
    @GET("api/v1/lesson-versions/{id}/bundle?allow_preview=true") suspend fun bundle(@Header("Authorization") auth: String, @Path("id") id: String): JsonObject
    @GET("api/v1/lesson-versions/{id}/assets/{asset}") suspend fun asset(@Header("Authorization") auth: String, @Path("id") id: String, @Path("asset") asset: String): okhttp3.ResponseBody
    @PUT("api/v1/learning-runs/{id}/scenes/{key}") suspend fun checkpoint(@Header("Authorization") auth: String, @Path("id") id: String, @Path("key") key: String, @Body data: PageDto): RunDto
}
