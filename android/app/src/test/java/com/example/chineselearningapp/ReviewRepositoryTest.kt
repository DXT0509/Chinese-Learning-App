package com.example.chineselearningapp

import com.example.chineselearningapp.core.network.*
import com.example.chineselearningapp.domain.repository.ReviewSubmission
import com.example.chineselearningapp.feature.auth.data.*
import com.example.chineselearningapp.feature.review.RemoteReviewRepository
import kotlinx.coroutines.test.runTest
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.junit.Assert.*
import org.junit.Test
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

class ReviewRepositoryTest {
    @Test fun contextualGrammarPromptOptionsAndSubmissionSurviveMapping() = runTest {
        MockWebServer().use { server ->
            val repo = repository(server)
            server.enqueue(MockResponse().setBody("""{"attempt_id":"attempt","stage":"POS","status":"IN_PROGRESS","expires_at":"expiry",
                "question":{"input_mode":"SINGLE_SELECT","prompt_vi":"Chọn chức năng.\nHọ【齐心协力】完成了任务。","simplified":"齐心协力","options":["subject","predicate","object","attribute","adverbial","complement","modal_modifier","independent_clause"]},"feedback":[],"skipped_stages":[]}"""))
            val question = repo.question("attempt").question!!
            assertTrue(question.prompt!!.contains("【齐心协力】"))
            assertTrue(question.prompt.contains('\n'))
            assertEquals("SINGLE_SELECT", question.inputMode)
            assertTrue(question.options.contains("adverbial"))
            server.takeRequest()
            server.enqueue(MockResponse().setBody(this@ReviewRepositoryTest.question))
            repo.submit("attempt", ReviewSubmission("key", "POS", null, listOf("adverbial")))
            assertEquals("""{"submission_key":"key","stage":"POS","answer":["adverbial"]}""", server.takeRequest().body.readUtf8())
        }
    }
    @Test fun acceptedStageUsesReturnedSafeQuestionWithoutSecondGet() = runTest {
        MockWebServer().use { server ->
            server.enqueue(MockResponse().setBody("""{"attempt_id":"attempt","stage":"PINYIN","status":"IN_PROGRESS","expires_at":"expiry",
                "question":{"input_mode":"TEXT","simplified":"sealed-hanzi"},
                "draft_questions":{"PINYIN":{"input_mode":"TEXT","prompt_vi":"meaning"}},
                "feedback":[{"stage":"HANZI","first_correct":false,"assisted":false,"correct_answer":["sealed-hanzi"]}],"skipped_stages":[]}"""))
            val result = repository(server).submitAndQuestion("attempt", ReviewSubmission("key", "HANZI", "wrong", null))
            assertEquals("PINYIN", result.stage)
            assertEquals(false, result.feedback.single().firstCorrect)
            assertEquals("meaning", result.draftQuestions.getValue("PINYIN").prompt)
            assertEquals(1, server.requestCount)
        }
    }
    @Test fun staleConnectionRecoveryReplaysExactIdempotentMutationBodies() = runTest {
        for (operation in listOf("start", "submit", "finalize")) {
            MockWebServer().use { server ->
                val repo = repository(server, recoverTransport = true)
                server.enqueue(MockResponse().setBody(question))
                repo.question("warmup"); server.takeRequest()
                // A previously pooled socket dies after receiving a mutation. Its commit is unknown.
                server.enqueue(MockResponse().setSocketPolicy(okhttp3.mockwebserver.SocketPolicy.DISCONNECT_AFTER_REQUEST))
                server.enqueue(MockResponse().setBody(when (operation) {
                    "start" -> """{"attempt_id":"original-attempt","grading_available":true}"""
                    "submit" -> question
                    else -> """{"outcome":"PASS","scheduling_applied":true,"state_after":{"mastery_level":1,"next_review_at":"server-next"}}"""
                }))
                when (operation) {
                    "start" -> assertEquals("original-attempt", repo.start("saved", "stable-key").attemptId)
                    "submit" -> repo.submit("attempt", ReviewSubmission("stable-key", "HANZI", "learner-text", null))
                    else -> assertEquals("PASS", repo.finalize("attempt").outcome)
                }
                val first = server.takeRequest(5, java.util.concurrent.TimeUnit.SECONDS)!!
                val replay = server.takeRequest(5, java.util.concurrent.TimeUnit.SECONDS)!!
                assertEquals(first.path, replay.path)
                assertEquals(first.body.readUtf8(), replay.body.readUtf8())
                assertEquals(3, server.requestCount)
            }
        }
    }
    @Test fun productionReviewClientKeepsTransportRecoveryEnabled() {
        assertTrue(com.example.chineselearningapp.core.di.AppModule.client().retryOnConnectionFailure)
    }
    private val sealedHanzi = """{"attempt_id":"attempt","stage":"PINYIN","status":"IN_PROGRESS","expires_at":"expiry",
        "question":{"input_mode":"TEXT","simplified":"sealed-hanzi"},
        "feedback":[{"stage":"HANZI","first_correct":false,"assisted":false,"correct_answer":["sealed-hanzi"]}],"skipped_stages":[]}"""
    @Test fun lostSubmissionResponseUsesSealedServerResultWithoutAnotherPost() = runTest {
        MockWebServer().use { server ->
            server.enqueue(MockResponse().setSocketPolicy(okhttp3.mockwebserver.SocketPolicy.DISCONNECT_AFTER_REQUEST))
            server.enqueue(MockResponse().setBody(sealedHanzi))
            val result = repository(server).submitAndQuestion("attempt", ReviewSubmission("same-key", "HANZI", "wrong", null))
            assertEquals(false, result.feedback.single().firstCorrect)
            assertEquals("POST", server.takeRequest().method)
            val recovery = server.takeRequest()
            assertEquals("GET", recovery.method)
            assertEquals("/api/v1/me/srs/sessions/attempt/question", recovery.path)
            assertEquals(2, server.requestCount)
        }
    }
    @Test fun unacceptedSubmissionReplaysOnceWithExactOriginalKeyAndBody() = runTest {
        MockWebServer().use { server ->
            server.enqueue(MockResponse().setSocketPolicy(okhttp3.mockwebserver.SocketPolicy.DISCONNECT_AFTER_REQUEST))
            server.enqueue(MockResponse().setBody(question))
            server.enqueue(MockResponse().setBody(sealedHanzi))
            val result = repository(server).submitAndQuestion("attempt", ReviewSubmission("same-key", "HANZI", "wrong", null))
            assertEquals(false, result.feedback.single().firstCorrect)
            val original = server.takeRequest(); assertEquals("GET", server.takeRequest().method)
            val replay = server.takeRequest()
            assertEquals(original.path, replay.path)
            assertEquals(original.body.readUtf8(), replay.body.readUtf8())
            assertEquals(3, server.requestCount)
        }
    }
    @Test fun repeatedTransportFailureStopsAfterOneReplay() = runTest {
        MockWebServer().use { server ->
            server.enqueue(MockResponse().setSocketPolicy(okhttp3.mockwebserver.SocketPolicy.DISCONNECT_AFTER_REQUEST))
            server.enqueue(MockResponse().setBody(question))
            server.enqueue(MockResponse().setSocketPolicy(okhttp3.mockwebserver.SocketPolicy.DISCONNECT_AFTER_REQUEST))
            try {
                repository(server).submitAndQuestion("attempt", ReviewSubmission("same-key", "HANZI", "wrong", null))
                fail("Expected persistent outage")
            } catch (_: java.io.IOException) { }
            assertEquals(3, server.requestCount)
        }
    }
    @Test fun invalidInputAndServerErrorsDoNotTriggerAutomaticReplay() = runTest {
        for (code in listOf(422, 500)) MockWebServer().use { server ->
            server.enqueue(MockResponse().setResponseCode(code))
            try {
                repository(server).submitAndQuestion("attempt", ReviewSubmission("same-key", "HANZI", "wrong", null))
                fail("Expected HTTP error")
            } catch (error: retrofit2.HttpException) { assertEquals(code, error.code()) }
            assertEquals(1, server.requestCount)
        }
    }
    @Test fun credentialPersistenceFailureDoesNotTriggerSubmissionRecoveryOrRefreshReplay() = runTest {
        MockWebServer().use { server ->
            val store = Store().also { it.writeError = java.io.IOException("synthetic storage failure") }
            server.enqueue(MockResponse().setResponseCode(401))
            server.enqueue(MockResponse().setBody("""{"access_token":"new","refresh_token":"rotated"}"""))
            try {
                repository(server, store).submitAndQuestion("attempt", ReviewSubmission("same-key", "HANZI", "wrong", null))
                fail("Expected storage failure")
            } catch (_: java.io.IOException) { }
            assertEquals(2, server.requestCount)
            assertEquals("/api/v1/me/srs/sessions/attempt/submissions", server.takeRequest().path)
            assertEquals("/api/v1/auth/refresh", server.takeRequest().path)
        }
    }
    private class Store : SessionTokenStore {
        var tokens: TokensDto? = TokensDto("access", "refresh")
        var writeError: java.io.IOException? = null
        override fun read() = tokens
        override fun write(tokens: TokensDto) { writeError?.let { throw it }; this.tokens = tokens }
        override fun clear() { tokens = null }
    }
    private fun repository(server: MockWebServer, store: Store = Store(), recoverTransport: Boolean = false): RemoteReviewRepository {
        // Explicit loopback avoids host-file reverse lookup of a wildcard bind address
        // when OkHttp reconnects after the deliberately dropped response.
        val retrofit = Retrofit.Builder().baseUrl(server.url("/").newBuilder().host("127.0.0.1").build()).client(okhttp3.OkHttpClient.Builder().retryOnConnectionFailure(recoverTransport).build()).addConverterFactory(GsonConverterFactory.create()).build()
        return RemoteReviewRepository(retrofit.create(ReviewApi::class.java),
            RemoteSessionRepository(retrofit.create(SessionApi::class.java), store))
    }
    private val question = """{"attempt_id":"attempt","stage":"HANZI","status":"IN_PROGRESS","expires_at":"expiry",
        "question":{"input_mode":"TEXT","prompt_vi":"Complete Vietnamese/Han-Viet/count cue"},"feedback":[],"skipped_stages":[]}"""
    @Test fun dashboardDueProgressAndFullPromptMapServerFields() = runTest {
        MockWebServer().use { server ->
            val repo = repository(server)
            server.enqueue(MockResponse().setBody("""{"available_count":12,"due_count":4,"suspended_count":2,"grading_available":true}"""))
            assertEquals(4, repo.dashboard().due)
            assertEquals("/api/v1/me/srs/dashboard", server.takeRequest().path)
            server.enqueue(MockResponse().setBody("""{"items":[{"saved_id":"saved","mastery_level":3,"next_review_at":"next"}]}"""))
            assertEquals(3, repo.due().single().mastery)
            assertEquals("/api/v1/me/srs/due?limit=100", server.takeRequest().path)
            server.enqueue(MockResponse().setBody(question))
            assertEquals("Complete Vietnamese/Han-Viet/count cue", repo.question("attempt").question!!.prompt)
            assertEquals("/api/v1/me/srs/sessions/attempt/question", server.takeRequest().path)
            server.enqueue(MockResponse().setBody("""{"saved_id":"saved","mastery_level":4,"next_review_at":"next"}"""))
            assertEquals(4, repo.progress("saved").mastery)
            assertEquals("/api/v1/me/srs/progress/saved", server.takeRequest().path)
        }
    }
    @Test fun paginationAdvancesAcrossEntirelyExcludedPage() = runTest {
        MockWebServer().use { server ->
            val exclusions = (1..100).joinToString(",") { """{"saved_id":"excluded-$it","reason":"REVIEWED_POLICY_REQUIRED"}""" }
            server.enqueue(MockResponse().setBody("""{"items":[],"excluded":[$exclusions]}"""))
            server.enqueue(MockResponse().setBody("""{"items":[{"saved_id":"due","due":true}],"excluded":[]}"""))
            val targets = repository(server).targets()
            assertEquals(100, targets.excluded.size); assertEquals("due", targets.items.single().savedId)
            assertEquals("0", server.takeRequest().requestUrl!!.queryParameter("offset"))
            assertEquals("100", server.takeRequest().requestUrl!!.queryParameter("offset"))
        }
    }
    @Test fun posAlwaysUsesArrayAndRefreshReplaysIdenticalSubmission() = runTest {
        MockWebServer().use { server ->
            server.enqueue(MockResponse().setResponseCode(401))
            server.enqueue(MockResponse().setBody("""{"access_token":"new","refresh_token":"rotated"}"""))
            server.enqueue(MockResponse().setBody(question))
            repository(server).submit("attempt", ReviewSubmission("stable-key", "POS", null, listOf("verb")))
            val first = server.takeRequest()
            assertEquals("/api/v1/me/srs/sessions/attempt/submissions", first.path)
            assertEquals("Bearer access", first.getHeader("Authorization"))
            assertEquals("/api/v1/auth/refresh", server.takeRequest().path)
            val replay = server.takeRequest()
            val body = first.body.readUtf8()
            assertEquals(body, replay.body.readUtf8())
            assertEquals("""{"submission_key":"stable-key","stage":"POS","answer":["verb"]}""", body)
            assertEquals("Bearer new", replay.getHeader("Authorization"))
        }
    }
    @Test fun startAndFinalizeUseExactOwnedIdentityAndEmptyBody() = runTest {
        MockWebServer().use { server ->
            val repo = repository(server)
            server.enqueue(MockResponse().setBody("""{"attempt_id":"attempt","grading_available":true}"""))
            assertEquals("attempt", repo.start("saved", "creation-key").attemptId)
            val start = server.takeRequest()
            assertEquals("POST", start.method); assertEquals("""{"saved_id":"saved","request_id":"creation-key"}""", start.body.readUtf8())
            server.enqueue(MockResponse().setBody("""{"outcome":"FAIL","scheduling_applied":false,"previous_mastery_level":4,"resulting_mastery_level":1,"state_after":{"mastery_level":1,"next_review_at":"server-next"}}"""))
            val result = repo.finalize("attempt")
            assertEquals(4, result.previousMastery); assertFalse(result.schedulingApplied); assertEquals(1, result.mastery); assertEquals("server-next", result.nextReviewAt)
            val finish = server.takeRequest()
            assertEquals("/api/v1/me/srs/sessions/attempt/finalize", finish.path); assertEquals("{}", finish.body.readUtf8())
        }
    }
    @Test fun rejectedRefreshClearsCredentials() = runTest {
        MockWebServer().use { server ->
            val store = Store()
            server.enqueue(MockResponse().setResponseCode(401)); server.enqueue(MockResponse().setResponseCode(401))
            try { repository(server, store).dashboard(); fail("Expected expiry") }
            catch (_: SessionExpired) { assertNull(store.tokens) }
        }
    }
    @Test fun distributionAndLegacyFinalizationMapWithoutInventingMastery() = runTest {
        MockWebServer().use { server ->
            val repo = repository(server)
            val buckets = (0..5).joinToString(",") { """{"mastery_level":$it,"count":${it + 1}}""" }
            server.enqueue(MockResponse().setBody("""{"available_count":21,"due_count":4,"suspended_count":0,"grading_available":true,"mastery_distribution":[$buckets]}"""))
            assertEquals((1..6).toList(), repo.dashboard().masteryDistribution!!.map { it.count })
            server.enqueue(MockResponse().setBody("""{"outcome":"PASS","scheduling_applied":false,"state_after":{"mastery_level":2,"next_review_at":"server-next"}}"""))
            val result = repo.finalize("attempt")
            assertNull(result.previousMastery); assertEquals(2, result.mastery)
        }
    }
    @Test fun lostCreationResponseAndAuthenticationReplayPreserveExactKey() = runTest {
        MockWebServer().use { server ->
            val repo = repository(server)
            server.enqueue(MockResponse().setSocketPolicy(okhttp3.mockwebserver.SocketPolicy.DISCONNECT_AFTER_REQUEST))
            try { repo.start("saved", "request-key"); fail("Expected lost response") } catch (_: java.io.IOException) { }
            val lost = server.takeRequest()
            server.enqueue(MockResponse().setResponseCode(401))
            server.enqueue(MockResponse().setBody("""{"access_token":"new","refresh_token":"rotated"}"""))
            server.enqueue(MockResponse().setBody("""{"attempt_id":"original-attempt","grading_available":true}"""))
            assertEquals("original-attempt", repo.start("saved", "request-key").attemptId)
            val retry = server.takeRequest()
            assertEquals("/api/v1/auth/refresh", server.takeRequest().path)
            val refreshed = server.takeRequest()
            val body = lost.body.readUtf8()
            assertEquals(body, retry.body.readUtf8()); assertEquals(body, refreshed.body.readUtf8())
            assertTrue(body.contains("\"request_id\":\"request-key\""))
        }
    }
    @Test fun sessionSelectionUsesDurableDailyPlannerEndpoint() = runTest {
        MockWebServer().use { server ->
            server.enqueue(MockResponse().setBody("""{"items":[{"saved_id":"from-beyond-first-page","due":true}],"excluded":[]}"""))
            assertEquals("from-beyond-first-page", repository(server).dailyPlan("stable-plan-key", false).items.single().savedId)
            assertEquals("/api/v1/me/srs/daily-plans", server.takeRequest().path)
        }
    }
    @Test fun structuredCharacterCountIsMappedWithoutExposingAnAnswer() = runTest {
        MockWebServer().use { server ->
            server.enqueue(MockResponse().setBody(question.replace("\"input_mode\":\"TEXT\"", "\"input_mode\":\"TEXT\",\"character_count\":3")))
            val question = repository(server).question("attempt").question!!
            assertEquals(3, question.characterCount); assertNull(question.simplified)
        }
    }
    @Test fun hanziSubmissionsSendLearnerTextUnchangedForServerGrading() = runTest {
        MockWebServer().use { server ->
            val repo = repository(server)
            for (word in listOf("学生", "错字")) {
                server.enqueue(MockResponse().setBody(question))
                repo.submit("attempt", ReviewSubmission("key-$word", "HANZI", word, null))
                val body = com.google.gson.JsonParser.parseString(server.takeRequest().body.readUtf8()).asJsonObject
                assertEquals(word, body["answer"].asString)
                assertEquals("HANZI", body["stage"].asString)
                assertFalse(body.has("correct"))
            }
        }
    }
}
