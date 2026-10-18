package com.example.chineselearningapp

import com.example.chineselearningapp.domain.model.BackendHealth
import com.example.chineselearningapp.domain.repository.HealthRepository
import com.example.chineselearningapp.feature.roadmap.ConnectivityState
import com.example.chineselearningapp.feature.roadmap.ConnectivityViewModel
import java.io.IOException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.resetMain
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.test.setMain
import org.junit.Assert.assertEquals
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class ConnectivityViewModelTest {
    @Test
    fun unavailableBackendCanBeRetried() = runTest {
        Dispatchers.setMain(StandardTestDispatcher(testScheduler))
        try {
            var fail = true
            val repository = object : HealthRepository {
                override suspend fun checkHealth(): BackendHealth {
                    if (fail) throw IOException("offline")
                    return BackendHealth("test", "0.1.0")
                }
            }
            val viewModel = ConnectivityViewModel(repository)
            assertEquals(ConnectivityState.Loading, viewModel.state.value)
            advanceUntilIdle()
            assertEquals(ConnectivityState.Unavailable, viewModel.state.value)
            fail = false
            viewModel.retry()
            advanceUntilIdle()
            assertEquals(ConnectivityState.Reachable(BackendHealth("test", "0.1.0")), viewModel.state.value)
        } finally {
            Dispatchers.resetMain()
        }
    }
}
