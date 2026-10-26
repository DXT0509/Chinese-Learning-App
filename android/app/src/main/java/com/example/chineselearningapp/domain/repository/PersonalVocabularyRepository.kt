package com.example.chineselearningapp.domain.repository

data class SavedWord(val id: String, val entryId: String, val simplified: String,
    val pinyin: String, val vietnamese: String?, val english: String?,
    val active: Boolean)
data class WordbookPage(val items: List<SavedWord>, val total: Int, val nextCursor: String?)
interface PersonalVocabularyRepository {
    suspend fun status(entryId: String): String?
    suspend fun save(entryId: String): SavedWord
    suspend fun list(query: String, cursor: String? = null): WordbookPage
    suspend fun remove(savedId: String)
}
