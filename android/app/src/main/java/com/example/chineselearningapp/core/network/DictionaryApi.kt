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
    @SerializedName("entry_id") val entryId: String, val simplified: String, val traditional: String?,
    @SerializedName("primary_pinyin") val pinyin: String,
    @SerializedName("short_vi_meaning") val shortVietnameseMeaning: String?,
    @SerializedName("available_languages") val availableLanguages: List<String>, val source: String
)
data class DictionaryPageDto(val items: List<DictionarySuggestionDto>, @SerializedName("next_offset") val nextOffset: Int?)
data class DictionarySenseDto(@SerializedName("sense_number") val number: Int, val gloss: String)
data class DictionarySourceDto(
    val source: String, @SerializedName("source_url") val sourceUrl: String,
    val license: String, @SerializedName("license_url") val licenseUrl: String,
    val attribution: String, val changes: String
)
data class CharacterEnrichmentDto(
    val scope: String, val form: String, val positions: List<Int>,
    @SerializedName("traditional_positions") val traditionalPositions: List<Int>, val pinyin: String,
    @SerializedName("sino_vietnamese") val sinoVietnamese: String?,
    @SerializedName("vietnamese_gloss") val vietnameseGloss: String?,
    @SerializedName("matches_entry_pronunciation") val matchesEntryPronunciation: Boolean?,
    val provenance: DictionarySourceDto
)
data class DictionaryEntryDto(
    @SerializedName("entry_id") val entryId: String, val simplified: String, val traditional: String?,
    @SerializedName("primary_pinyin") val pinyin: String,
    @SerializedName("short_vi_meaning") val shortVietnameseMeaning: String?,
    @SerializedName("available_languages") val availableLanguages: List<String>, val source: String,
    @SerializedName("citation_pinyin") val citationPinyin: String,
    val meanings: Map<String, List<DictionarySenseDto>>,
    @SerializedName("sino_vietnamese") val sinoVietnamese: String?,
    @SerializedName("character_enrichments") val characters: List<CharacterEnrichmentDto>,
    val provenance: DictionarySourceDto
)
