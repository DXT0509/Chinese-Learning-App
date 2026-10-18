package com.example.chineselearningapp.core.network

import com.example.chineselearningapp.domain.model.BackendHealth
import com.example.chineselearningapp.domain.repository.HealthRepository
import java.io.IOException
import javax.inject.Inject

class RemoteHealthRepository @Inject constructor(private val api: HealthApi) : HealthRepository {
    override suspend fun checkHealth(): BackendHealth {
        val response = api.health()
        if (response.status != "ok" || response.service.isNullOrBlank() || response.version.isNullOrBlank()) {
            throw IOException("Invalid health response")
        }
        return BackendHealth(response.service, response.version)
    }
}
