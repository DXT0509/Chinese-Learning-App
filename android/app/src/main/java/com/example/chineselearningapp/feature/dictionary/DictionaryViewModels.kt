package com.example.chineselearningapp.feature.dictionary

import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.chineselearningapp.domain.model.*
import com.example.chineselearningapp.domain.repository.DictionaryRepository
import com.example.chineselearningapp.feature.auth.data.SessionExpired
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import retrofit2.HttpException

const val DICTIONARY_SEARCH_ROUTE = "dictionary"
const val DICTIONARY_DETAIL_ROUTE = "dictionary/{entryId}"
fun dictionaryDetailRoute(entryId: String): String = "dictionary/${java.util.UUID.fromString(entryId)}"

enum class DictionaryPhase { Empty, Typing, Loading, Results, NoResults, Error, Invalid, Expired, NotFound }
data class DictionarySearchState(
    val query: String = "", val phase: DictionaryPhase = DictionaryPhase.Empty,
    val items: List<DictionarySuggestion> = emptyList(), val nextOffset: Int? = null,
    val loadingMore: Boolean = false, val pageError: Boolean = false
)

/** Validate the raw input before trimming, matching the API's 64 Unicode code point limit. */
internal fun validDictionaryQuery(text: String): Boolean = text.codePointCount(0, text.length) <= 64 &&
    text.codePoints().noneMatch { Character.getType(it) in setOf(
        Character.CONTROL.toInt(), Character.FORMAT.toInt(), Character.SURROGATE.toInt(),
        Character.PRIVATE_USE.toInt(), Character.UNASSIGNED.toInt()) }

class DictionarySearchViewModel(private val repository: DictionaryRepository,
    private val savedState: SavedStateHandle) : ViewModel() {
    private val mutableState = MutableStateFlow(DictionarySearchState(query = savedState["query"] ?: ""))
    val state = mutableState.asStateFlow()
    private var operation: Job? = null
    private var generation = 0
    private var composing = false
    init { schedule() }

    // Keyboard, paste and future handwriting insertion all enter this same pipeline.
    fun edit(text: String, isComposing: Boolean = false) {
        if (text == state.value.query && isComposing == composing) return
        val previous = state.value.query
        val wasComposing = composing
        composing = isComposing
        savedState["query"] = text
        mutableState.value = state.value.copy(query = text)
        // Cursor changes and equivalent surrounding whitespace do not repeat requests.
        if (!isComposing && !wasComposing && previous.trim() == text.trim() &&
            validDictionaryQuery(text) && validDictionaryQuery(previous)) return
        schedule()
    }
    private fun schedule(immediate: Boolean = false) {
        operation?.cancel()
        val ticket = ++generation
        val raw = state.value.query
        val query = raw.trim()
        val phase = when {
            query.isEmpty() -> DictionaryPhase.Empty
            !validDictionaryQuery(raw) -> DictionaryPhase.Invalid
            else -> DictionaryPhase.Typing
        }
        mutableState.value = DictionarySearchState(raw, phase)
        if (phase != DictionaryPhase.Typing || composing) return
        operation = viewModelScope.launch {
            if (!immediate) delay(300)
            if (ticket != generation) return@launch
            mutableState.value = state.value.copy(phase = DictionaryPhase.Loading)
            try {
                val page = repository.search(query)
                ensureActive()
                if (ticket == generation) mutableState.value = state.value.copy(
                    phase = if (page.items.isEmpty()) DictionaryPhase.NoResults else DictionaryPhase.Results,
                    items = page.items, nextOffset = page.nextOffset)
            } catch (cancelled: CancellationException) { throw cancelled }
            catch (error: Exception) {
                if (ticket == generation) mutableState.value = state.value.copy(phase = error.phase())
            }
        }
    }
    fun retry() { if (!composing) schedule(immediate = true) }
    fun loadMore() {
        val current = state.value
        val offset = current.nextOffset ?: return
        if (offset !in 0..1000 || current.loadingMore || current.phase != DictionaryPhase.Results) return
        val ticket = generation
        mutableState.value = current.copy(loadingMore = true, pageError = false)
        operation = viewModelScope.launch {
            try {
                val page = repository.search(current.query.trim(), offset)
                ensureActive()
                if (ticket == generation) mutableState.value = state.value.copy(
                    items = (current.items + page.items).distinctBy { it.entryId },
                    nextOffset = page.nextOffset?.takeIf { it > offset && it <= 1000 }, loadingMore = false)
            } catch (cancelled: CancellationException) { throw cancelled }
            catch (error: Exception) {
                if (ticket == generation) mutableState.value = state.value.copy(loadingMore = false,
                    pageError = true, phase = if (error.phase() == DictionaryPhase.Expired) DictionaryPhase.Expired else DictionaryPhase.Results)
            }
        }
    }
}

data class DictionaryDetailState(val phase: DictionaryPhase = DictionaryPhase.Loading, val entry: DictionaryEntry? = null)
class DictionaryDetailViewModel(private val repository: DictionaryRepository,
    savedState: SavedStateHandle) : ViewModel() {
    private val entryId: String = checkNotNull(savedState["entryId"])
    private val mutableState = MutableStateFlow(DictionaryDetailState())
    val state = mutableState.asStateFlow()
    private var operation: Job? = null
    init { retry() }
    fun retry() {
        operation?.cancel()
        mutableState.value = DictionaryDetailState()
        operation = viewModelScope.launch {
            try {
                val entry = repository.detail(entryId)
                ensureActive()
                mutableState.value = DictionaryDetailState(DictionaryPhase.Results, entry)
            } catch (cancelled: CancellationException) { throw cancelled }
            catch (error: Exception) { mutableState.value = DictionaryDetailState(error.phase()) }
        }
    }
}
private fun Exception.phase() = when {
    this is SessionExpired || this is HttpException && code() == 401 -> DictionaryPhase.Expired
    this is HttpException && code() == 404 -> DictionaryPhase.NotFound
    this is HttpException && code() == 422 -> DictionaryPhase.Invalid
    else -> DictionaryPhase.Error
}
