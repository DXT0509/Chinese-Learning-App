package com.example.chineselearningapp.core.database

import androidx.room.Entity
import androidx.room.PrimaryKey

/** Public catalog cache only. User progress requires separate identity-scoped tables. */
@Entity(tableName = "cached_vocabulary")
data class CachedVocabulary(
    @PrimaryKey val id: String,
    val simplified: String,
    val pinyin: String,
    val vietnameseMeaning: String,
)
