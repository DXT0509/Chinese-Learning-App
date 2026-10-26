package com.example.chineselearningapp.domain.model

data class DictionarySuggestion(
    val entryId: String, val simplified: String, val pinyin: String,
    val shortVietnameseMeaning: String?, val availableLanguages: List<String>, val source: String
)
data class DictionaryPage(val items: List<DictionarySuggestion>, val nextOffset: Int?)
data class DictionarySense(val number: Int, val gloss: String)
data class DictionaryEntry(
    val suggestion: DictionarySuggestion, val citationPinyin: String,
    val meanings: Map<String, List<DictionarySense>>, val sinoVietnamese: String?,
    val reviewStatus: String, val active: Boolean = true
) {
    val meaningGroups get() = meanings.entries.filter { it.value.isNotEmpty() }
        .sortedWith(compareBy { when (it.key) { "vi" -> 0; "en" -> 1; else -> 2 } })
}
