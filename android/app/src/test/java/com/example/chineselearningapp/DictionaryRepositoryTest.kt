package com.example.chineselearningapp

import com.example.chineselearningapp.core.network.*
import com.example.chineselearningapp.feature.auth.data.RemoteSessionRepository
import com.example.chineselearningapp.feature.auth.data.SessionExpired
import com.example.chineselearningapp.feature.dictionary.data.RemoteDictionaryRepository
import kotlinx.coroutines.test.runTest
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.junit.Assert.*
import org.junit.Test
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

class DictionaryRepositoryTest {
    private class Store : SessionTokenStore {
        var tokens: TokensDto? = TokensDto("access", "refresh")
        override fun read() = tokens
        override fun write(tokens: TokensDto) { this.tokens = tokens }
        override fun clear() { tokens = null }
    }
    private fun repository(server: MockWebServer, store: Store = Store()): RemoteDictionaryRepository {
        val retrofit = Retrofit.Builder().baseUrl(server.url("/"))
            .addConverterFactory(GsonConverterFactory.create()).build()
        return RemoteDictionaryRepository(retrofit.create(DictionaryApi::class.java),
            RemoteSessionRepository(retrofit.create(SessionApi::class.java), store))
    }
    private val id = "f15eec42-512e-4a48-9c2f-045264b2e119"
    private val suggestion = """"entry_id":"$id","simplified":"家","traditional":"傢",
        "primary_pinyin":"jiā","short_vi_meaning":"nhà","available_languages":["vi","en"],"source":"APP_CURATED""""
    private val source = """{"source":"CC-CEDICT","source_url":"https://cc-cedict.org/",
        "license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/",
        "attribution":"CC-CEDICT contributors","changes":"No changes"}"""

    @Test fun searchMapsCuratedVietnameseAndUsesPagination() = runTest {
        MockWebServer().use { server ->
            server.enqueue(MockResponse().setBody("""{"items":[{$suggestion}],"next_offset":40}"""))
            val page = repository(server).search("家", 20)
            assertEquals(40, page.nextOffset)
            assertEquals(id, page.items.single().entryId)
            assertEquals("jiā", page.items.single().pinyin)
            assertEquals("nhà", page.items.single().shortVietnameseMeaning)
            assertEquals(listOf("vi", "en"), page.items.single().availableLanguages)
            val request = server.takeRequest()
            assertEquals("Bearer access", request.getHeader("Authorization"))
            assertEquals("家", request.requestUrl!!.queryParameter("q"))
            assertEquals("20", request.requestUrl!!.queryParameter("limit"))
            assertEquals("20", request.requestUrl!!.queryParameter("offset"))
        }
    }
    @Test fun detailMapsCuratedGlossesWithoutProviderEnrichment() = runTest {
        MockWebServer().use { server ->
            server.enqueue(MockResponse().setBody("""{$suggestion,"citation_pinyin":"jiā",
                "meanings":{"en":[{"sense_number":1,"gloss":"see 家庭[jia1 ting2]"}]},
                "sino_vietnamese":null,"review_status":"HUMAN_APPROVED","provenance":$source,
                "character_enrichments":[{"scope":"character","form":"家","positions":[0],
                "traditional_positions":[0],"pinyin":"jià","sino_vietnamese":"giá",
                "vietnamese_gloss":"chú giải chữ","matches_entry_pronunciation":false,"provenance":$source}]}"""))
            val entry = repository(server).detail(id)
            assertEquals("/api/v1/dictionary/entries/$id", server.takeRequest().path)
            assertEquals("see 家庭[jia1 ting2]", entry.meanings.getValue("en").single().gloss)
            assertFalse(entry.meanings.containsKey("vi"))
            assertNull(entry.sinoVietnamese)
            assertEquals("HUMAN_APPROVED", entry.reviewStatus)
            assertEquals("APP_CURATED", entry.suggestion.source)
        }
    }
    @Test fun curatedDetailWithoutLegacyProviderFieldsMapsSuccessfully() = runTest {
        MockWebServer().use { server ->
            // CuratedDetail has no provider provenance or character_enrichments.
            server.enqueue(MockResponse().setBody("""{
                "entry_id":"$id","simplified":"家","primary_pinyin":"jiā",
                "short_vi_meaning":"nhà","available_languages":["en","vi"],
                "source":"APP_CURATED","content_version":1,"learning_level":1,
                "pinyin_numbered":"jia1","citation_pinyin":"jiā",
                "meanings":{"vi":[{"sense_number":1,"gloss":"nhà"}],
                    "en":[{"sense_number":1,"gloss":"home"}]},
                "sino_vietnamese":null,"part_of_speech":"noun","examples":[],
                "review_status":"LOCAL_CODEX_REVIEWED","active":true
            }"""))
            val entry = repository(server).detail(id)
            assertEquals("家", entry.suggestion.simplified)
            assertEquals("jiā", entry.citationPinyin)
            assertEquals("nhà", entry.meanings.getValue("vi").single().gloss)
            assertEquals(listOf("vi", "en"), entry.meaningGroups.map { it.key })
            assertEquals("LOCAL_CODEX_REVIEWED", entry.reviewStatus)
            assertTrue(entry.active)
        }
    }
    @Test fun dictionaryReusesRefreshAndRetriesWithRotatedAccess() = runTest {
        MockWebServer().use { server ->
            val store = Store()
            server.enqueue(MockResponse().setResponseCode(401))
            server.enqueue(MockResponse().setBody("""{"access_token":"new","refresh_token":"rotated"}"""))
            server.enqueue(MockResponse().setBody("""{"items":[],"next_offset":null}"""))
            assertTrue(repository(server, store).search("家").items.isEmpty())
            assertEquals("Bearer access", server.takeRequest().getHeader("Authorization"))
            assertEquals("/api/v1/auth/refresh", server.takeRequest().path)
            assertEquals("Bearer new", server.takeRequest().getHeader("Authorization"))
            assertEquals("rotated", store.tokens?.refresh)
        }
    }
    @Test fun rejectedRefreshClearsExistingSession() = runTest {
        MockWebServer().use { server ->
            val store = Store()
            server.enqueue(MockResponse().setResponseCode(401))
            server.enqueue(MockResponse().setResponseCode(401))
            try { repository(server, store).search("家"); fail("Expected expired session") }
            catch (_: SessionExpired) { assertNull(store.tokens) }
        }
    }
}
