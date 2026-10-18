package com.example.chineselearningapp.core.database

import androidx.room.Database
import androidx.room.RoomDatabase

@Database(entities = [CachedVocabulary::class], version = 1, exportSchema = true)
abstract class LearningDatabase : RoomDatabase() {
    abstract fun vocabularyDao(): VocabularyDao
}
