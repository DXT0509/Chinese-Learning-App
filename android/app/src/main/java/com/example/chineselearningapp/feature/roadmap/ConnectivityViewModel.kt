package com.example.chineselearningapp.feature.roadmap

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.chineselearningapp.domain.model.BackendHealth
import com.example.chineselearningapp.domain.repository.HealthRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

sealed interface ConnectivityState {
    data object Loading : ConnectivityState
    data class Reachable(val health: BackendHealth) : ConnectivityState
    data object Unavailable : ConnectivityState
}

@HiltViewModel
class ConnectivityViewModel @Inject constructor(private val repository: HealthRepository) : ViewModel() {
    private val mutableState = MutableStateFlow<ConnectivityState>(ConnectivityState.Loading)
    val state = mutableState.asStateFlow()
    private var request: Job? = null

    init { retry() }

    fun retry() {
        if (request?.isActive == true) return
        request = viewModelScope.launch {
            mutableState.value = ConnectivityState.Loading
            mutableState.value = try {
                ConnectivityState.Reachable(repository.checkHealth())
            } catch (cancelled: CancellationException) {
                throw cancelled
            } catch (_: Exception) {
                ConnectivityState.Unavailable
            }
        }
    }
}
