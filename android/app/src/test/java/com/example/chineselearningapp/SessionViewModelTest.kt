package com.example.chineselearningapp

import com.example.chineselearningapp.domain.repository.*
import com.example.chineselearningapp.feature.auth.SessionViewModel
import com.example.chineselearningapp.feature.auth.SessionStatus
import kotlinx.coroutines.CompletableDeferred
import okhttp3.ResponseBody.Companion.toResponseBody
import retrofit2.HttpException
import retrofit2.Response
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.*
import org.junit.Assert.*
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class SessionViewModelTest {
    private class FakeRepository : SessionRepository {
        var user: Account? = null
        var failStart = true
        var accountFailure: Exception? = null
        var authFailure: Exception? = null
        var contentFailure: Exception? = null
        var restoreGate: CompletableDeferred<Unit>? = null
        var authCalls = 0
        val requests = mutableListOf<String>()
        override suspend fun authenticate(email: String, password: String, register: Boolean) {
            authCalls++
            authFailure?.let { throw it }
            user = Account("user", email)
        }
        override suspend fun account(): Account? {
            restoreGate?.await()
            accountFailure?.let { throw it }
            return user
        }
        override suspend fun logout() { user = null }
        override suspend fun catalog(): List<CatalogLesson> {
            contentFailure?.let { throw it }
            return listOf(CatalogLesson("version-1", "Preview"))
        }
        override suspend fun runs() = emptyList<PreviewRun>()
        override suspend fun start(versionId: String, requestId: String): PreviewRun {
            requests += requestId
            if (failStart) throw java.io.IOException()
            return PreviewRun("run-1", versionId, emptyMap())
        }
        override suspend fun resume(runId: String) = PreviewRun(runId, "version-1", emptyMap())
        override suspend fun scenes(versionId: String) = listOf(PreviewScene("scene", 0))
        override suspend fun checkpoint(runId: String, sceneKey: String, page: Int) = PreviewRun(runId, "version-1", mapOf(sceneKey to page))
    }
    @Test fun validationLoginRetryCheckpointAndLogout() = runTest {
        Dispatchers.setMain(StandardTestDispatcher(testScheduler))
        try {
            val repository = FakeRepository()
            val model = SessionViewModel(repository)
            advanceUntilIdle()
            model.authenticate("user@example.com", "short", true)
            assertEquals(R.string.auth_password_error, model.state.value.fieldErrors.password)
            assertNull(model.state.value.error)
            assertNull(repository.user)
            model.authenticate("user@example.com", "123456", true)
            assertTrue(model.state.value.loading)
            advanceUntilIdle()
            assertEquals("user", model.state.value.account?.id)
            model.start("version-1")
            advanceUntilIdle()
            assertEquals(R.string.session_network_error, model.state.value.error)
            repository.failStart = false
            model.start("version-1")
            advanceUntilIdle()
            assertEquals(repository.requests[0], repository.requests[1])
            assertEquals("version-1", model.state.value.run?.versionId)
            model.checkpoint("scene")
            advanceUntilIdle()
            assertEquals(1, model.state.value.run?.checkpoints?.get("scene"))
            model.logout()
            advanceUntilIdle()
            assertNull(model.state.value.account)
            assertEquals(SessionStatus.SignedOut, model.state.value.status)
            assertNull(model.state.value.run)
            assertTrue(model.state.value.runs.isEmpty())
        } finally { Dispatchers.resetMain() }
    }

    @Test fun passwordBoundariesAreEnforcedBeforeNetwork() = runTest {
        Dispatchers.setMain(StandardTestDispatcher(testScheduler))
        try {
            listOf(5 to false, 6 to true, 128 to true, 129 to false).forEach { (length, accepted) ->
                val repository = FakeRepository()
                val model = SessionViewModel(repository)
                advanceUntilIdle()
                model.authenticate("user@example.com", "a".repeat(length), true, "a".repeat(length))
                advanceUntilIdle()
                assertEquals(if (accepted) 1 else 0, repository.authCalls)
                assertEquals(if (accepted) SessionStatus.SignedIn else SessionStatus.SignedOut, model.state.value.status)
            }
        } finally { Dispatchers.resetMain() }
    }

    @Test fun confirmationMismatchStaysInline() = runTest {
        Dispatchers.setMain(StandardTestDispatcher(testScheduler))
        try {
            val repository = FakeRepository()
            val model = SessionViewModel(repository)
            advanceUntilIdle()
            model.authenticate("user@example.com", "123456", true, "654321")
            assertEquals(R.string.auth_confirmation_error, model.state.value.fieldErrors.confirmation)
            assertEquals(0, repository.authCalls)
            assertNull(model.state.value.error)
        } finally { Dispatchers.resetMain() }
    }

    @Test fun existingSessionStaysOnRestorationUntilAccountIsAvailable() = runTest {
        Dispatchers.setMain(StandardTestDispatcher(testScheduler))
        try {
            val gate = CompletableDeferred<Unit>()
            val repository = FakeRepository().apply { user = Account("saved-user", "saved@example.com"); restoreGate = gate }
            val model = SessionViewModel(repository)
            runCurrent()
            assertEquals(SessionStatus.Restoring, model.state.value.status)
            assertNull(model.state.value.account)
            gate.complete(Unit)
            advanceUntilIdle()
            assertEquals(SessionStatus.SignedIn, model.state.value.status)
            assertEquals("saved-user", model.state.value.account?.id)
        } finally { Dispatchers.resetMain() }
    }

    @Test fun restorationNetworkFailureCanBeRetriedWithoutShowingLogin() = runTest {
        Dispatchers.setMain(StandardTestDispatcher(testScheduler))
        try {
            val repository = FakeRepository().apply { accountFailure = java.io.IOException() }
            val model = SessionViewModel(repository)
            advanceUntilIdle()
            assertEquals(SessionStatus.RestoreFailed, model.state.value.status)
            repository.accountFailure = null
            repository.user = Account("saved", "saved@example.com")
            model.reload()
            advanceUntilIdle()
            assertEquals(SessionStatus.SignedIn, model.state.value.status)
        } finally { Dispatchers.resetMain() }
    }

    @Test fun backendValidationAndInvalidCredentialsAreNotClientFieldErrors() = runTest {
        Dispatchers.setMain(StandardTestDispatcher(testScheduler))
        try {
            listOf(422 to R.string.auth_server_validation, 401 to R.string.auth_invalid).forEach { (code, message) ->
                val repository = FakeRepository().apply { authFailure = HttpException(Response.error<Any>(code, "{}".toResponseBody())) }
                val model = SessionViewModel(repository)
                advanceUntilIdle()
                model.authenticate("user@example.com", "123456", false)
                advanceUntilIdle()
                assertEquals(message, model.state.value.error)
                assertFalse(model.state.value.fieldErrors.hasErrors)
                assertEquals(SessionStatus.SignedOut, model.state.value.status)
            }
        } finally { Dispatchers.resetMain() }
    }

    @Test fun catalogFailureDoesNotUndoSuccessfulAuthentication() = runTest {
        Dispatchers.setMain(StandardTestDispatcher(testScheduler))
        try {
            val repository = FakeRepository().apply { contentFailure = java.io.IOException() }
            val model = SessionViewModel(repository)
            advanceUntilIdle()
            model.authenticate("user@example.com", "123456", false)
            advanceUntilIdle()
            assertEquals(SessionStatus.SignedIn, model.state.value.status)
            assertNotNull(model.state.value.account)
            assertFalse(model.state.value.contentLoaded)
            assertEquals(R.string.session_network_error, model.state.value.error)
        } finally { Dispatchers.resetMain() }
    }
}
