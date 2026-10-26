package com.example.chineselearningapp.feature.vocabulary.data

import com.example.chineselearningapp.core.network.*
import com.example.chineselearningapp.domain.repository.*
import com.example.chineselearningapp.feature.auth.data.RemoteSessionRepository
import javax.inject.Inject

class RemotePersonalVocabularyRepository @Inject constructor(
    private val api: PersonalVocabularyApi, private val session: RemoteSessionRepository
) : PersonalVocabularyRepository {
    override suspend fun status(entryId: String) = session.authorized { api.status(it, entryId) }.savedId
    override suspend fun save(entryId: String) = session.authorized { api.save(it, SaveWordDto(entryId)) }.domain()
    override suspend fun list(query: String, cursor: String?) = session.authorized { api.list(it, query, cursor) }
        .let { WordbookPage(it.items.map(SavedWordDto::domain), it.total, it.nextCursor) }
    override suspend fun remove(savedId: String) = session.authorized { api.remove(it, savedId) }
}
private fun SavedWordDto.domain() = SavedWord(id, entryId, simplified, pinyin, vietnamese, english, active)
