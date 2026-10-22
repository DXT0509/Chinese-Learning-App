package com.example.chineselearningapp.domain.model

data class DictionarySuggestion(
    val entryId: String, val simplified: String, val traditional: String?, val pinyin: String,
    val shortVietnameseMeaning: String?, val availableLanguages: List<String>, val source: String
)
data class DictionaryPage(val items: List<DictionarySuggestion>, val nextOffset: Int?)
data class DictionarySense(val number: Int, val gloss: String)
data class DictionarySource(
    val source: String, val sourceUrl: String, val license: String, val licenseUrl: String,
    val attribution: String, val changes: String
)
data class CharacterEnrichment(
    val scope: String, val form: String, val positions: List<Int>, val traditionalPositions: List<Int>,
    val pinyin: String, val sinoVietnamese: String?, val vietnameseGloss: String?,
    val matchesEntryPronunciation: Boolean?, val provenance: DictionarySource
)
data class DictionaryEntry(
    val suggestion: DictionarySuggestion, val citationPinyin: String,
    val meanings: Map<String, List<DictionarySense>>, val sinoVietnamese: String?,
    val characters: List<CharacterEnrichment>, val provenance: DictionarySource
) {
    val meaningGroups get() = meanings.entries.filter { it.value.isNotEmpty() }
        .sortedWith(compareBy { when (it.key) { "vi" -> 0; "en" -> 1; else -> 2 } })
}
