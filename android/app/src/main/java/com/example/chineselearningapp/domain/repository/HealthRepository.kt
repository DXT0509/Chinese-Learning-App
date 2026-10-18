package com.example.chineselearningapp.domain.repository

import com.example.chineselearningapp.domain.model.BackendHealth

interface HealthRepository {
    suspend fun checkHealth(): BackendHealth
}
