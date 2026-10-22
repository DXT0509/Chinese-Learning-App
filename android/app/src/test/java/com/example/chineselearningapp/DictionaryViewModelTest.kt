package com.example.chineselearningapp

import androidx.lifecycle.SavedStateHandle
import com.example.chineselearningapp.domain.model.*
import com.example.chineselearningapp.domain.repository.DictionaryRepository
import com.example.chineselearningapp.feature.dictionary.*
import com.example.chineselearningapp.feature.auth.data.SessionExpired
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.Assert.*
import org.junit.Test
import java.io.IOException

@OptIn(ExperimentalCoroutinesApi::class)
class DictionaryViewModelTest {
    private class Repository : DictionaryRepository {
        val queries = mutableListOf<Pair<String, Int>>()
        val details = mutableListOf<String>()
        var searchCall: suspend (String, Int) -> DictionaryPage = { _, _ -> DictionaryPage(emptyList(), null) }
        var detailCall: suspend (String) -> DictionaryEntry = { throw IOException() }
        override suspend fun search(query: String, offset: Int): DictionaryPage {
            queries += query to offset; return searchCall(query, offset)
        }
        override suspend fun detail(entryId: String): DictionaryEntry { details += entryId; return detailCall(entryId) }
    }
    private fun scenario(test: suspend TestScope.(Repository) -> Unit) = runTest {
        Dispatchers.setMain(StandardTestDispatcher(testScheduler))
        try { test(Repository()) } finally { Dispatchers.resetMain() }
    }
    private fun suggestion(id: String) = DictionarySuggestion(id, "\u5bb6", "\u50a2", "ji\u0101", null, listOf("en"), "CC-CEDICT")

    @Test fun debounceCancelsTypingAndDoesNotRepeatForCursorOrWhitespace() = scenario { repo ->
        val vm = DictionarySearchViewModel(repo, SavedStateHandle())
        vm.edit("\u5b66"); runCurrent(); advanceTimeBy(200)
        vm.edit("\u5b66\u751f"); runCurrent(); advanceTimeBy(299); runCurrent()
        assertTrue(repo.queries.isEmpty())
        advanceTimeBy(1); runCurrent()
        assertEquals(listOf("\u5b66\u751f" to 0), repo.queries)
        assertEquals(DictionaryPhase.NoResults, vm.state.value.phase)
        vm.edit("\u5b66\u751f"); vm.edit(" \u5b66\u751f "); advanceUntilIdle()
        assertEquals(1, repo.queries.size)
        assertEquals(" \u5b66\u751f ", vm.state.value.query)
    }
    @Test fun compositionWaitsUntilCommittedAndEmptyOrInvalidNeverCallsApi() = scenario { repo ->
        val vm = DictionarySearchViewModel(repo, SavedStateHandle())
        vm.edit("\u5b66", true); advanceUntilIdle(); assertTrue(repo.queries.isEmpty())
        vm.edit("\u5b66\u751f", true); advanceUntilIdle(); assertTrue(repo.queries.isEmpty())
        vm.edit("\u5b66\u751f", false); advanceUntilIdle(); assertEquals(1, repo.queries.size)
        vm.edit(" "); advanceUntilIdle(); assertEquals(DictionaryPhase.Empty, vm.state.value.phase)
        vm.edit("\u5b66".repeat(65)); advanceUntilIdle(); assertEquals(DictionaryPhase.Invalid, vm.state.value.phase)
        vm.edit("\u5b66\u200B"); advanceUntilIdle(); assertEquals(DictionaryPhase.Invalid, vm.state.value.phase)
        assertEquals(1, repo.queries.size)
    }
    @Test fun cancelledNonCooperativeRequestCannotReplaceNewerResult() = scenario { repo ->
        val gate = CompletableDeferred<Unit>()
        repo.searchCall = { q, _ ->
            if (q == "old") withContext(NonCancellable) { gate.await() }
            DictionaryPage(listOf(suggestion(q)), null)
        }
        val vm = DictionarySearchViewModel(repo, SavedStateHandle())
        vm.edit("old"); runCurrent(); advanceTimeBy(300); runCurrent()
        vm.edit("new"); runCurrent(); advanceTimeBy(300); runCurrent()
        assertEquals("new", vm.state.value.items.single().entryId)
        gate.complete(Unit); advanceUntilIdle()
        assertEquals("new", vm.state.value.items.single().entryId)
    }
    @Test fun failurePreservesQueryAndManualRetryAndSessionExpiryAreExplicit() = scenario { repo ->
        repo.searchCall = { _, _ -> throw IOException() }
        val vm = DictionarySearchViewModel(repo, SavedStateHandle())
        vm.edit("\u5b66"); advanceUntilIdle()
        assertEquals(DictionaryPhase.Error, vm.state.value.phase); assertEquals("\u5b66", vm.state.value.query)
        repo.searchCall = { _, _ -> throw SessionExpired() }
        vm.retry(); advanceUntilIdle(); assertEquals(DictionaryPhase.Expired, vm.state.value.phase)
        repo.searchCall = { _, _ -> DictionaryPage(emptyList(), null) }
        vm.retry(); advanceUntilIdle(); assertEquals(DictionaryPhase.NoResults, vm.state.value.phase)
    }
    @Test fun restoresQueryAndPreservesBackendOrderAndDistinctIdentitiesWithSameHanzi() = scenario { repo ->
        repo.searchCall = { _, offset -> DictionaryPage(
            if (offset == 0) listOf(suggestion("b"), suggestion("a")) else listOf(suggestion("c")),
            if (offset == 0) 20 else null) }
        val handle = SavedStateHandle(mapOf("query" to "\u5b66"))
        val vm = DictionarySearchViewModel(repo, handle); advanceUntilIdle()
        assertEquals(listOf("b", "a"), vm.state.value.items.map { it.entryId })
        assertNull(vm.state.value.items.first().shortVietnameseMeaning)
        vm.loadMore(); advanceUntilIdle()
        assertEquals(listOf("b", "a", "c"), vm.state.value.items.map { it.entryId })
        assertEquals(listOf("\u5b66" to 0, "\u5b66" to 20), repo.queries)
        vm.edit("\u5b66"); assertEquals("\u5b66", handle.get<String>("query")); advanceUntilIdle()
    }
    @Test fun pageFailureKeepsResultsAndRetryUsesSameOffset() = scenario { repo ->
        var failPage = true
        repo.searchCall = { _, offset ->
            if (offset == 20 && failPage) throw IOException()
            DictionaryPage(listOf(suggestion(offset.toString())), if (offset == 0) 20 else null)
        }
        val vm = DictionarySearchViewModel(repo, SavedStateHandle(mapOf("query" to "\u5b66")))
        advanceUntilIdle(); vm.loadMore(); advanceUntilIdle()
        assertTrue(vm.state.value.pageError); assertEquals("0", vm.state.value.items.single().entryId)
        failPage = false; vm.loadMore(); advanceUntilIdle()
        assertFalse(vm.state.value.pageError); assertEquals(2, vm.state.value.items.size)
    }
    @Test fun stableUuidRouteAndDetailSavedArgument() = scenario { repo ->
        val id = "f15eec42-512e-4a48-9c2f-045264b2e119"
        assertEquals("dictionary/$id", dictionaryDetailRoute(id))
        val model = DictionaryDetailViewModel(repo, SavedStateHandle(mapOf("entryId" to id)))
        advanceUntilIdle(); assertEquals(listOf(id), repo.details)
        assertEquals(DictionaryPhase.Error, model.state.value.phase)
        repo.detailCall = { throw SessionExpired() }
        model.retry(); advanceUntilIdle(); assertEquals(DictionaryPhase.Expired, model.state.value.phase)
    }
    @Test fun supplementaryHanziCountAsOneCharacter() {
        assertTrue(validDictionaryQuery("\uD840\uDC00".repeat(64)))
        assertFalse(validDictionaryQuery("\uD840\uDC00".repeat(65)))
    }

    @Test fun serverValidationNotFoundAndUnavailableAreMappedAndDetailCanRetry() = scenario { repo ->
        fun http(code: Int) = retrofit2.HttpException(retrofit2.Response.error<Any>(code,
            okhttp3.ResponseBody.create(null, "")))
        val search = DictionarySearchViewModel(repo, SavedStateHandle())
        repo.searchCall = { _, _ -> throw http(422) }
        search.edit("学"); advanceUntilIdle()
        assertEquals(DictionaryPhase.Invalid, search.state.value.phase)
        repo.searchCall = { _, _ -> throw http(503) }
        search.retry(); advanceUntilIdle()
        assertEquals(DictionaryPhase.Error, search.state.value.phase)
        repo.detailCall = { throw http(404) }
        val detail = DictionaryDetailViewModel(repo, SavedStateHandle(mapOf("entryId" to "id")))
        advanceUntilIdle(); assertEquals(DictionaryPhase.NotFound, detail.state.value.phase)
        val origin = DictionarySource("source", "https://example.com", "license", "https://example.com", "credit", "")
        repo.detailCall = { DictionaryEntry(suggestion("id"), "jiā",
            linkedMapOf("en" to listOf(DictionarySense(1, "family")),
                "vi" to listOf(DictionarySense(1, "gia đình"))), null, emptyList(), origin) }
        detail.retry(); advanceUntilIdle()
        assertEquals(DictionaryPhase.Results, detail.state.value.phase)
        assertEquals(listOf("vi", "en"), detail.state.value.entry!!.meaningGroups.map { it.key })
        assertTrue(detail.state.value.entry!!.characters.isEmpty())
    }
}
