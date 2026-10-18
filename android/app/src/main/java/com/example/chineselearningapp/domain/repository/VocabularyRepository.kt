package com.example.chineselearningapp.domain.repository

import com.example.chineselearningapp.domain.model.VocabularyEntry
import kotlinx.coroutines.flow.Flow

interface VocabularyRepository {
    fun observeCachedVocabulary(): Flow<List<VocabularyEntry>>
    suspend fun cacheVocabulary(entries: List<VocabularyEntry>)
}
