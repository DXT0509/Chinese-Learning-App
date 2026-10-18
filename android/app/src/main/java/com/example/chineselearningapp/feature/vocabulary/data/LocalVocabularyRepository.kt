package com.example.chineselearningapp.feature.vocabulary.data

import com.example.chineselearningapp.core.database.CachedVocabulary
import com.example.chineselearningapp.core.database.VocabularyDao
import com.example.chineselearningapp.domain.model.VocabularyEntry
import com.example.chineselearningapp.domain.repository.VocabularyRepository
import javax.inject.Inject
import kotlinx.coroutines.flow.map

class LocalVocabularyRepository @Inject constructor(private val dao: VocabularyDao) : VocabularyRepository {
    override fun observeCachedVocabulary() = dao.observeAll().map { entries ->
        entries.map { VocabularyEntry(it.id, it.simplified, it.pinyin, it.vietnameseMeaning) }
    }

    override suspend fun cacheVocabulary(entries: List<VocabularyEntry>) {
        dao.upsertAll(entries.map { CachedVocabulary(it.id, it.simplified, it.pinyin, it.vietnameseMeaning) })
    }
}
