package com.example.chineselearningapp.core.network

import com.google.gson.annotations.SerializedName
import retrofit2.http.*

interface DictionaryApi {
    @GET("api/v1/dictionary/search")
    suspend fun search(@Header("Authorization") auth: String, @Query("q") query: String,
        @Query("limit") limit: Int = 20, @Query("offset") offset: Int = 0): DictionaryPageDto
    @GET("api/v1/dictionary/entries/{id}")
    suspend fun detail(@Header("Authorization") auth: String, @Path("id") entryId: String): DictionaryEntryDto
}
data class DictionarySuggestionDto(
    @SerializedName("entry_id") val entryId: String, val simplified: String,
    @SerializedName("primary_pinyin") val pinyin: String,
    @SerializedName("short_vi_meaning") val shortVietnameseMeaning: String?,
    @SerializedName("available_languages") val availableLanguages: List<String>, val source: String
)
data class DictionaryPageDto(val items: List<DictionarySuggestionDto>, @SerializedName("next_offset") val nextOffset: Int?)
data class DictionarySenseDto(@SerializedName("sense_number") val number: Int, val gloss: String)
data class DictionaryEntryDto(
    @SerializedName("entry_id") val entryId: String, val simplified: String,
    @SerializedName("primary_pinyin") val pinyin: String,
    @SerializedName("short_vi_meaning") val shortVietnameseMeaning: String?,
    @SerializedName("available_languages") val availableLanguages: List<String>, val source: String,
    @SerializedName("citation_pinyin") val citationPinyin: String,
    val meanings: Map<String, List<DictionarySenseDto>>,
    @SerializedName("sino_vietnamese") val sinoVietnamese: String?,
    @SerializedName("review_status") val reviewStatus: String, val active: Boolean = true
)
