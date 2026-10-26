package com.example.chineselearningapp

import com.example.chineselearningapp.core.network.*
import com.example.chineselearningapp.feature.auth.data.RemoteSessionRepository
import com.example.chineselearningapp.feature.auth.data.SessionExpired
import com.example.chineselearningapp.feature.vocabulary.data.RemotePersonalVocabularyRepository
import kotlinx.coroutines.test.runTest
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.junit.Assert.*
import org.junit.Test
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

class PersonalVocabularyRepositoryTest {
    private class Store : SessionTokenStore {
        var tokens: TokensDto? = TokensDto("access", "refresh")
        override fun read() = tokens
        override fun write(tokens: TokensDto) { this.tokens = tokens }
        override fun clear() { tokens = null }
    }
    private fun repository(server: MockWebServer, store: Store = Store()): RemotePersonalVocabularyRepository {
        val retrofit = Retrofit.Builder().baseUrl(server.url("/"))
            .addConverterFactory(GsonConverterFactory.create()).build()
        return RemotePersonalVocabularyRepository(retrofit.create(PersonalVocabularyApi::class.java),
            RemoteSessionRepository(retrofit.create(SessionApi::class.java), store))
    }
    private val word = """{"id":"saved-id","dictionary_entry_id":"exact-entry","simplified":"word",
        "pinyin":"pinyin","short_vi_meaning":null,
        "short_en_meaning":"English meaning","active":false}"""
    @Test fun saveStatusListAndRemoveUsePrivateContractsAndExactIdentity() = runTest {
        MockWebServer().use { server ->
            val repo = repository(server)
            server.enqueue(MockResponse().setBody(word))
            val saved = repo.save("exact-entry")
            val post = server.takeRequest()
            assertEquals("POST", post.method)
            assertEquals("/api/v1/me/vocabulary", post.path)
            assertEquals("Bearer access", post.getHeader("Authorization"))
            assertEquals("""{"dictionary_entry_id":"exact-entry"}""", post.body.readUtf8())
            assertEquals("exact-entry", saved.entryId); assertFalse(saved.active)
            assertNull(saved.vietnamese); assertEquals("English meaning", saved.english)
            server.enqueue(MockResponse().setBody("""{"saved_id":"saved-id"}"""))
            assertEquals("saved-id", repo.status("exact-entry"))
            assertEquals("exact-entry", server.takeRequest().requestUrl!!.queryParameter("dictionary_entry_id"))
            server.enqueue(MockResponse().setBody("""{"items":[$word],"total":42,"next_cursor":"next"}"""))
            val page = repo.list("pinyin", "cursor")
            assertEquals(42, page.total); assertEquals("next", page.nextCursor)
            val get = server.takeRequest()
            assertEquals("/api/v1/me/vocabulary", get.requestUrl!!.encodedPath)
            assertEquals("pinyin", get.requestUrl!!.queryParameter("q"))
            assertEquals("cursor", get.requestUrl!!.queryParameter("cursor"))
            server.enqueue(MockResponse().setResponseCode(204))
            repo.remove("saved-id")
            val delete = server.takeRequest()
            assertEquals("DELETE", delete.method); assertEquals("/api/v1/me/vocabulary/saved-id", delete.path)
        }
    }
    @Test fun saveReusesRefreshAndRetriesSameEntryOnly() = runTest {
        MockWebServer().use { server ->
            val store = Store()
            server.enqueue(MockResponse().setResponseCode(401))
            server.enqueue(MockResponse().setBody("""{"access_token":"new","refresh_token":"rotated"}"""))
            server.enqueue(MockResponse().setBody(word))
            assertEquals("saved-id", repository(server, store).save("exact-entry").id)
            val first = server.takeRequest()
            assertEquals("/api/v1/auth/refresh", server.takeRequest().path)
            val retried = server.takeRequest()
            assertEquals(first.body.readUtf8(), retried.body.readUtf8())
            assertEquals("Bearer new", retried.getHeader("Authorization"))
        }
    }
    @Test fun expiredWordbookSessionClearsExistingCredentials() = runTest {
        MockWebServer().use { server ->
            val store = Store()
            server.enqueue(MockResponse().setResponseCode(401)); server.enqueue(MockResponse().setResponseCode(401))
            try { repository(server, store).list(""); fail("Expected expiry") }
            catch (_: SessionExpired) { assertNull(store.tokens) }
        }
    }
}
