package com.example.chineselearningapp

import com.example.chineselearningapp.core.network.HealthApi
import com.example.chineselearningapp.core.network.RemoteHealthRepository
import java.io.IOException
import kotlinx.coroutines.test.runTest
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.junit.Assert.assertEquals
import org.junit.Test
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

class HealthRepositoryTest {
    @Test
    fun usesVersionedEndpointAndRejectsInvalidHealth() = runTest {
        val server = MockWebServer()
        server.start()
        try {
            val api = Retrofit.Builder().baseUrl(server.url("/"))
                .addConverterFactory(GsonConverterFactory.create()).build().create(HealthApi::class.java)
            val repository = RemoteHealthRepository(api)
            server.enqueue(MockResponse().setBody("""{"status":"ok","service":"test","version":"0.1.0"}"""))
            assertEquals("test", repository.checkHealth().service)
            assertEquals("/api/v1/health", server.takeRequest().path)
            server.enqueue(MockResponse().setBody("{}"))
            var rejected = false
            try { repository.checkHealth() } catch (_: IOException) { rejected = true }
            assertEquals(true, rejected)
        } finally {
            server.shutdown()
        }
    }
}
