package com.example.chineselearningapp.core.database

import androidx.room.Dao
import androidx.room.Query
import androidx.room.Upsert
import kotlinx.coroutines.flow.Flow

@Dao
interface VocabularyDao {
    @Query("SELECT * FROM cached_vocabulary ORDER BY simplified, id")
    fun observeAll(): Flow<List<CachedVocabulary>>

    @Upsert
    suspend fun upsertAll(entries: List<CachedVocabulary>)
}
