package com.example.chineselearningapp.feature.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.chineselearningapp.R
import com.example.chineselearningapp.domain.model.AuthValidation
import com.example.chineselearningapp.domain.repository.Account
import com.example.chineselearningapp.domain.repository.CatalogLesson
import com.example.chineselearningapp.domain.repository.PreviewRun
import com.example.chineselearningapp.domain.repository.PreviewScene
import com.example.chineselearningapp.domain.repository.SessionRepository
import com.example.chineselearningapp.feature.auth.data.SessionExpired
import dagger.hilt.android.lifecycle.HiltViewModel
import java.util.UUID
import javax.inject.Inject
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import retrofit2.HttpException

enum class SessionStatus { Restoring, RestoreFailed, SignedOut, SignedIn }

data class AuthFieldErrors(
    val email: Int? = null,
    val password: Int? = null,
    val confirmation: Int? = null
) {
    val hasErrors: Boolean get() = email != null || password != null || confirmation != null
}

data class SessionState(
    val status: SessionStatus = SessionStatus.Restoring,
    val loading: Boolean = false,
    val account: Account? = null,
    // Only network/backend/session errors appear in the banner. Form errors stay inline.
    val error: Int? = null,
    val fieldErrors: AuthFieldErrors = AuthFieldErrors(),
    val contentLoaded: Boolean = false,
    val catalog: List<CatalogLesson> = emptyList(),
    val runs: List<PreviewRun> = emptyList(),
    val run: PreviewRun? = null,
    val scenes: List<PreviewScene> = emptyList()
)

@HiltViewModel
class SessionViewModel @Inject constructor(private val repository: SessionRepository) : ViewModel() {
    private val mutableState = MutableStateFlow(SessionState())
    val state = mutableState.asStateFlow()
    private val startRequests = mutableMapOf<String, String>()

    init { reload() }

    private fun operation(block: suspend () -> Unit) {
        if (mutableState.value.loading) return
        mutableState.value = mutableState.value.copy(loading = true, error = null)
        viewModelScope.launch {
            try {
                block()
            } catch (cancelled: CancellationException) {
                throw cancelled
            } catch (_: SessionExpired) {
                signedOut(R.string.session_expired)
            } catch (error: Exception) {
                val current = mutableState.value
                mutableState.value = current.copy(
                    status = if (current.status == SessionStatus.Restoring) SessionStatus.RestoreFailed else current.status,
                    error = when {
                        error is HttpException && error.code() == 401 -> R.string.auth_invalid
                        error is HttpException && error.code() == 409 -> R.string.auth_duplicate
                        error is HttpException && error.code() == 422 -> R.string.auth_server_validation
                        error is HttpException && error.code() == 429 -> R.string.auth_throttled
                        error is HttpException && error.code() == 403 -> R.string.preview_disabled
                        error is HttpException -> R.string.session_server_error
                        else -> R.string.session_network_error
                    }
                )
            } finally {
                mutableState.value = mutableState.value.copy(loading = false)
            }
        }
    }

    private fun signedOut(error: Int? = null) {
        startRequests.clear()
        mutableState.value = SessionState(status = SessionStatus.SignedOut, error = error)
    }

    private suspend fun restoreAccount() {
        val account = repository.account()
        if (account == null) {
            signedOut()
            return
        }
        mutableState.value = mutableState.value.copy(status = SessionStatus.SignedIn, account = account)
        val catalog = repository.catalog()
        val runs = repository.runs()
        mutableState.value = mutableState.value.copy(catalog = catalog, runs = runs, contentLoaded = true)
    }

    fun reload() = operation {
        if (mutableState.value.account == null) {
            mutableState.value = mutableState.value.copy(status = SessionStatus.Restoring)
        }
        restoreAccount()
    }

    fun clearFormErrors() {
        mutableState.value = mutableState.value.copy(fieldErrors = AuthFieldErrors(), error = null)
    }

    fun authenticate(email: String, password: String, register: Boolean, confirmation: String = password) {
        if (mutableState.value.loading || mutableState.value.status != SessionStatus.SignedOut) return
        val errors = AuthFieldErrors(
            email = if (AuthValidation.validEmail(email)) null else R.string.auth_email_error,
            password = if (AuthValidation.validPassword(password)) null else R.string.auth_password_error,
            confirmation = if (register && password != confirmation) R.string.auth_confirmation_error else null
        )
        mutableState.value = mutableState.value.copy(fieldErrors = errors, error = null)
        if (errors.hasErrors) return
        operation {
            repository.authenticate(email, password, register)
            // The API returns a session for both register and login. Restore its real account.
            mutableState.value = mutableState.value.copy(status = SessionStatus.Restoring)
            restoreAccount()
        }
    }

    fun logout() = operation {
        repository.logout()
        signedOut()
    }

    fun start(versionId: String) = operation {
        val request = startRequests.getOrPut(versionId) { UUID.randomUUID().toString() }
        open(repository.start(versionId, request))
    }

    fun resume(runId: String) = operation { open(repository.resume(runId)) }

    private suspend fun open(run: PreviewRun) {
        val scenes = repository.scenes(run.versionId)
        mutableState.value = mutableState.value.copy(run = run, scenes = scenes)
        mutableState.value = mutableState.value.copy(runs = repository.runs())
    }

    fun checkpoint(sceneKey: String) = operation {
        val run = mutableState.value.run ?: return@operation
        val page = ((run.checkpoints[sceneKey] ?: 0) + 1).coerceAtMost(10000)
        mutableState.value = mutableState.value.copy(run = repository.checkpoint(run.id, sceneKey, page))
    }
}
