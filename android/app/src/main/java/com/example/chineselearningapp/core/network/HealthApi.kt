package com.example.chineselearningapp.core.network

import com.google.gson.annotations.SerializedName
import retrofit2.http.GET

data class HealthDto(
    @SerializedName("status") val status: String?,
    @SerializedName("service") val service: String?,
    @SerializedName("version") val version: String?,
)

interface HealthApi {
    @GET("api/v1/health")
    suspend fun health(): HealthDto
}
