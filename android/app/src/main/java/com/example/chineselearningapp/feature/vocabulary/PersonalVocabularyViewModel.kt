package com.example.chineselearningapp.feature.vocabulary

import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.chineselearningapp.domain.repository.*
import com.example.chineselearningapp.feature.auth.data.SessionExpired
import com.example.chineselearningapp.feature.dictionary.validDictionaryQuery
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import retrofit2.HttpException

internal fun Exception.sessionExpired() = this is SessionExpired || this is HttpException && code() == 401

data class SavedEntryState(val loading: Boolean = true, val savedId: String? = null,
    val error: Boolean = false, val expired: Boolean = false, val confirmed: Boolean = false,
    val statusKnown: Boolean = false)
class SavedEntryViewModel(private val repository: PersonalVocabularyRepository,
    private val entryId: String) : ViewModel() {
    private val mutableState = MutableStateFlow(SavedEntryState())
    val state = mutableState.asStateFlow()
    private var operation: Job? = null
    init { refresh() }
    fun refresh() {
        if (state.value.loading && state.value.statusKnown) return
        perform { repository.status(entryId) }
    }
    fun save() {
        if (state.value.loading || !state.value.statusKnown || state.value.savedId != null) return
        perform(true) { repository.save(entryId).id }
    }
    private fun perform(confirmed: Boolean = false, request: suspend () -> String?) {
        if (operation?.isActive == true) return
        mutableState.value = state.value.copy(loading = true, error = false, confirmed = false)
        operation = viewModelScope.launch {
            try {
                val id = request(); ensureActive()
                mutableState.value = SavedEntryState(loading = false, savedId = id,
                    statusKnown = true, confirmed = confirmed)
            } catch (cancelled: CancellationException) { throw cancelled }
            catch (error: Exception) { mutableState.value = state.value.copy(loading = false,
                error = true, expired = error.sessionExpired()) }
        }
    }
}

data class WordbookState(val query: String = "", val items: List<SavedWord> = emptyList(),
    val total: Int = 0, val nextCursor: String? = null, val loading: Boolean = true,
    val error: Boolean = false, val invalid: Boolean = false, val expired: Boolean = false,
    val removing: String? = null, val pendingRemoval: SavedWord? = null,
    val removeError: Boolean = false, val removed: Boolean = false)
class PersonalVocabularyViewModel(private val repository: PersonalVocabularyRepository,
    private val savedState: SavedStateHandle) : ViewModel() {
    private val mutableState = MutableStateFlow(WordbookState(query = savedState["query"] ?: ""))
    val state = mutableState.asStateFlow()
    private var request: Job? = null
    private var generation = 0
    init { refresh() }
    fun edit(query: String) {
        if (query == state.value.query) return
        savedState["query"] = query
        mutableState.value = state.value.copy(query = query)
        fetch(reset = true, debounce = true)
    }
    fun refresh() = fetch(reset = true)
    fun more() { if (!state.value.loading && state.value.nextCursor != null) fetch(reset = false) }
    private fun fetch(reset: Boolean, debounce: Boolean = false) {
        request?.cancel()
        val ticket = ++generation
        val previous = state.value
        val cursor = if (reset) null else previous.nextCursor
        if (!validDictionaryQuery(previous.query)) {
            mutableState.value = previous.copy(loading = false, invalid = true, items = emptyList(), nextCursor = null)
            return
        }
        mutableState.value = previous.copy(loading = true, error = false, invalid = false,
            nextCursor = if (reset) null else previous.nextCursor,
            items = if (reset && debounce) emptyList() else previous.items)
        request = viewModelScope.launch {
            try {
                if (debounce) delay(300)
                var page = repository.list(previous.query.trim(), cursor); ensureActive()
                // Refresh the loaded window when returning from detail, preserving scroll position.
                val refreshed = page.items.toMutableList()
                val seenCursors = mutableSetOf<String>()
                while (reset && !debounce && refreshed.size < previous.items.size) {
                    val next = page.nextCursor ?: break
                    if (!seenCursors.add(next)) break
                    page = repository.list(previous.query.trim(), next); ensureActive()
                    refreshed += page.items
                }
                if (ticket == generation) mutableState.value = state.value.copy(
                    items = (if (reset) refreshed else previous.items + page.items).distinctBy { it.id },
                    total = page.total, nextCursor = page.nextCursor, loading = false)
            } catch (cancelled: CancellationException) { throw cancelled }
            catch (error: Exception) {
                if (ticket == generation) mutableState.value = state.value.copy(loading = false,
                    error = true, expired = error.sessionExpired())
            }
        }
    }
    fun askRemove(word: SavedWord) { if (state.value.removing == null) mutableState.value = state.value.copy(pendingRemoval = word, removed = false, removeError = false) }
    fun cancelRemove() { if (state.value.removing == null) mutableState.value = state.value.copy(pendingRemoval = null) }
    fun confirmRemove() {
        val word = state.value.pendingRemoval ?: return
        if (state.value.removing != null) return
        mutableState.value = state.value.copy(removing = word.id, removeError = false)
        viewModelScope.launch {
            try {
                repository.remove(word.id); ensureActive()
                mutableState.value = state.value.copy(items = state.value.items.filterNot { it.id == word.id },
                    total = (state.value.total - 1).coerceAtLeast(0), removing = null,
                    pendingRemoval = null, removed = true)
                refresh()
            } catch (cancelled: CancellationException) { throw cancelled }
            catch (error: Exception) { mutableState.value = state.value.copy(removing = null,
                removeError = true, expired = error.sessionExpired()) }
        }
    }
}
