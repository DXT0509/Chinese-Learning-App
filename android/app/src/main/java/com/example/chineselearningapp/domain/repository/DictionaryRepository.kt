package com.example.chineselearningapp.domain.repository

import com.example.chineselearningapp.domain.model.*

interface DictionaryRepository {
    suspend fun search(query: String, offset: Int = 0): DictionaryPage
    suspend fun detail(entryId: String): DictionaryEntry
}
