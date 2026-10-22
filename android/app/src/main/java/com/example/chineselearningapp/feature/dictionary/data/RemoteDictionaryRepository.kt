package com.example.chineselearningapp.feature.dictionary.data

import com.example.chineselearningapp.core.network.*
import com.example.chineselearningapp.domain.model.*
import com.example.chineselearningapp.domain.repository.DictionaryRepository
import com.example.chineselearningapp.feature.auth.data.RemoteSessionRepository
import javax.inject.Inject

class RemoteDictionaryRepository @Inject constructor(
    private val api: DictionaryApi, private val session: RemoteSessionRepository
) : DictionaryRepository {
    override suspend fun search(query: String, offset: Int) = session.authorized {
        api.search(it, query, offset = offset)
    }.let { DictionaryPage(it.items.map(DictionarySuggestionDto::domain), it.nextOffset) }
    override suspend fun detail(entryId: String) = session.authorized { api.detail(it, entryId) }.domain()
}
internal fun DictionarySuggestionDto.domain() = DictionarySuggestion(
    entryId, simplified, traditional, pinyin, shortVietnameseMeaning, availableLanguages, source)
internal fun DictionarySourceDto.domain() = DictionarySource(source, sourceUrl, license, licenseUrl, attribution, changes)
internal fun DictionaryEntryDto.domain() = DictionaryEntry(
    DictionarySuggestion(entryId, simplified, traditional, pinyin, shortVietnameseMeaning, availableLanguages, source),
    citationPinyin, meanings.mapValues { (_, senses) -> senses.map { DictionarySense(it.number, it.gloss) } },
    sinoVietnamese, characters.map { CharacterEnrichment(it.scope, it.form, it.positions, it.traditionalPositions,
        it.pinyin, it.sinoVietnamese, it.vietnameseGloss, it.matchesEntryPronunciation, it.provenance.domain()) },
    provenance.domain())
