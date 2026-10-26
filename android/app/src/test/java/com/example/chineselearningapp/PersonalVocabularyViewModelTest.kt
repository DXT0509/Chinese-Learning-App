package com.example.chineselearningapp

import androidx.lifecycle.SavedStateHandle
import com.example.chineselearningapp.domain.repository.*
import com.example.chineselearningapp.feature.vocabulary.*
import com.example.chineselearningapp.feature.auth.data.SessionExpired
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.Assert.*
import org.junit.Test
import java.io.IOException

@OptIn(ExperimentalCoroutinesApi::class)
class PersonalVocabularyViewModelTest {
    private fun word(id: String) = SavedWord(id, id, "same Hanzi", "pinyin", null, "English", true)
    private class Repository : PersonalVocabularyRepository {
        val saved = mutableMapOf<String, SavedWord>()
        val queries = mutableListOf<Pair<String, String?>>()
        var saves = 0
        var removes = 0
        var statusCall: suspend (String) -> String? = { saved[it]?.id }
        var saveCall: suspend (String) -> SavedWord = { saved.getValue(it) }
        var listCall: suspend (String, String?) -> WordbookPage = { _, _ -> WordbookPage(saved.values.toList(), saved.size, null) }
        var removeCall: suspend (String) -> Unit = { saved.remove(it); Unit }
        override suspend fun status(entryId: String) = statusCall(entryId)
        override suspend fun save(entryId: String): SavedWord { saves++; return saveCall(entryId) }
        override suspend fun list(query: String, cursor: String?): WordbookPage { queries += query to cursor; return listCall(query, cursor) }
        override suspend fun remove(savedId: String) { removes++; removeCall(savedId) }
    }
    private fun scenario(test: suspend TestScope.(Repository) -> Unit) = runTest {
        Dispatchers.setMain(StandardTestDispatcher(testScheduler))
        try { test(Repository()) } finally { Dispatchers.resetMain() }
    }
    @Test fun saveWaitsForStatusProtectsDoubleTapAndRestoresConfirmedIdentity() = scenario { repo ->
        val gate = CompletableDeferred<Unit>()
        repo.saveCall = { id -> gate.await(); word(id).also { repo.saved[id] = it } }
        val model = SavedEntryViewModel(repo, "first")
        model.save(); assertEquals(0, repo.saves)
        advanceUntilIdle(); assertTrue(model.state.value.statusKnown)
        assertNull(model.state.value.savedId)
        model.save(); model.save(); runCurrent()
        assertTrue(model.state.value.loading); assertEquals(1, repo.saves)
        assertNull(model.state.value.savedId)
        gate.complete(Unit); advanceUntilIdle()
        assertEquals("first", model.state.value.savedId); assertTrue(model.state.value.confirmed)
        model.save(); advanceUntilIdle(); assertEquals(1, repo.saves)
        val reopened = SavedEntryViewModel(repo, "first"); advanceUntilIdle()
        assertEquals("first", reopened.state.value.savedId)
        val homograph = SavedEntryViewModel(repo, "second"); advanceUntilIdle()
        assertNull(homograph.state.value.savedId)
    }
    @Test fun failedStatusAndFailedSaveNeverClaimSuccessAndCanRetry() = scenario { repo ->
        repo.statusCall = { throw IOException() }
        val model = SavedEntryViewModel(repo, "first"); advanceUntilIdle()
        assertTrue(model.state.value.error); assertFalse(model.state.value.statusKnown)
        model.save(); advanceUntilIdle(); assertEquals(0, repo.saves)
        repo.statusCall = { null }; model.refresh(); advanceUntilIdle()
        repo.saveCall = { throw IOException() }; model.save(); advanceUntilIdle()
        assertTrue(model.state.value.error); assertNull(model.state.value.savedId)
        assertFalse(model.state.value.confirmed)
        repo.saveCall = { throw SessionExpired() }; model.save(); advanceUntilIdle()
        assertTrue(model.state.value.expired)
    }
    @Test fun emptySearchPaginationAndRefreshKeepLoadedWindow() = scenario { repo ->
        val handle = SavedStateHandle(mapOf("query" to "pinyin"))
        val model = PersonalVocabularyViewModel(repo, handle); advanceUntilIdle()
        assertTrue(model.state.value.items.isEmpty()); assertEquals(0, model.state.value.total)
        repo.listCall = { _, cursor -> if (cursor == null) WordbookPage(listOf(word("one")), 2, "next")
            else WordbookPage(listOf(word("two")), 2, null) }
        model.refresh(); advanceUntilIdle(); model.more(); model.more(); advanceUntilIdle()
        assertEquals(listOf("one", "two"), model.state.value.items.map { it.id })
        model.refresh(); advanceUntilIdle()
        assertEquals(listOf("one", "two"), model.state.value.items.map { it.id })
        assertEquals("pinyin", model.state.value.query)
        model.edit("new"); advanceUntilIdle()
        assertEquals("new", handle.get<String>("query"))
        assertEquals("new" to null, repo.queries.last())
        assertEquals(listOf("one"), model.state.value.items.map { it.id })
    }
    @Test fun cancelledSearchCannotReplaceNewerResultsAndInvalidQueryDoesNotLoad() = scenario { repo ->
        val gate = CompletableDeferred<Unit>()
        repo.listCall = { query, _ ->
            if (query == "old") withContext(NonCancellable) { gate.await() }
            WordbookPage(listOf(word(query)), 1, null)
        }
        val model = PersonalVocabularyViewModel(repo, SavedStateHandle()); advanceUntilIdle()
        model.edit("old"); runCurrent(); advanceTimeBy(300); runCurrent()
        model.edit("new"); runCurrent(); advanceTimeBy(300); runCurrent()
        gate.complete(Unit); advanceUntilIdle()
        assertEquals("new", model.state.value.items.single().id)
        val calls = repo.queries.size
        model.edit("x".repeat(65)); advanceUntilIdle()
        assertTrue(model.state.value.invalid); assertEquals(calls, repo.queries.size)
    }
    @Test fun removeRequiresConfirmationAndNetworkFailureRetainsItemUntilSuccess() = scenario { repo ->
        repo.saved["one"] = word("one")
        val model = PersonalVocabularyViewModel(repo, SavedStateHandle()); advanceUntilIdle()
        model.askRemove(word("one")); model.cancelRemove(); model.confirmRemove(); advanceUntilIdle()
        assertEquals(0, repo.removes)
        repo.removeCall = { throw IOException() }
        model.askRemove(word("one")); model.confirmRemove(); advanceUntilIdle()
        assertTrue(model.state.value.removeError); assertEquals(1, model.state.value.items.size)
        val gate = CompletableDeferred<Unit>()
        repo.removeCall = { gate.await(); repo.saved.remove(it); Unit }
        model.confirmRemove(); model.confirmRemove(); runCurrent()
        assertEquals("one", model.state.value.removing); assertEquals(2, repo.removes)
        gate.complete(Unit); advanceUntilIdle()
        assertTrue(model.state.value.items.isEmpty()); assertNull(model.state.value.pendingRemoval)
        assertTrue(model.state.value.removed)
    }
    @Test fun paginationFailureRetainsItemsAndExpiryIsExplicit() = scenario { repo ->
        repo.listCall = { _, cursor -> if (cursor != null) throw IOException()
            else WordbookPage(listOf(word("one")), 2, "next") }
        val model = PersonalVocabularyViewModel(repo, SavedStateHandle()); advanceUntilIdle()
        model.more(); advanceUntilIdle()
        assertTrue(model.state.value.error); assertEquals("one", model.state.value.items.single().id)
        assertEquals("next", model.state.value.nextCursor)
        repo.listCall = { _, _ -> throw SessionExpired() }
        model.more(); advanceUntilIdle(); assertTrue(model.state.value.expired)
    }
}
