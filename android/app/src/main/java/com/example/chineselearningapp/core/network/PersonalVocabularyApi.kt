package com.example.chineselearningapp.core.network

import com.google.gson.annotations.SerializedName
import retrofit2.http.*

interface PersonalVocabularyApi {
    @GET("api/v1/me/vocabulary")
    suspend fun list(@Header("Authorization") auth: String, @Query("q") query: String,
        @Query("cursor") cursor: String?): WordbookPageDto
    @GET("api/v1/me/vocabulary/status")
    suspend fun status(@Header("Authorization") auth: String,
        @Query("dictionary_entry_id") entryId: String): SavedStatusDto
    @POST("api/v1/me/vocabulary")
    suspend fun save(@Header("Authorization") auth: String, @Body body: SaveWordDto): SavedWordDto
    @DELETE("api/v1/me/vocabulary/{id}")
    suspend fun remove(@Header("Authorization") auth: String, @Path("id") savedId: String)
}
data class SaveWordDto(@SerializedName("dictionary_entry_id") val entryId: String)
data class SavedStatusDto(@SerializedName("saved_id") val savedId: String?)
data class SavedWordDto(val id: String, @SerializedName("dictionary_entry_id") val entryId: String,
    val simplified: String, val pinyin: String,
    @SerializedName("short_vi_meaning") val vietnamese: String?,
    @SerializedName("short_en_meaning") val english: String?, val active: Boolean)
data class WordbookPageDto(val items: List<SavedWordDto>, val total: Int,
    @SerializedName("next_cursor") val nextCursor: String?)
