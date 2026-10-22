package com.example.chineselearningapp.core.navigation

import androidx.annotation.StringRes
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.core.tween
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.navigation.compose.*
import com.example.chineselearningapp.R
import com.example.chineselearningapp.core.designsystem.*
import com.example.chineselearningapp.feature.auth.*
import com.example.chineselearningapp.feature.lesson.*
import com.example.chineselearningapp.feature.roadmap.*
import com.example.chineselearningapp.feature.dictionary.handwriting.HandwritingRecognizer

enum class Destination(@param:StringRes val title: Int) {
    Home(R.string.home_title), Learning(R.string.nav_learning), Lessons(R.string.lessons), Roadmap(R.string.roadmap),
    Vocabulary(R.string.vocabulary), Review(R.string.review), Profile(R.string.profile)
}

data class SessionActions(
    val authenticate: (String, String, Boolean, String) -> Unit = { _, _, _, _ -> },
    val logout: () -> Unit = {}, val reload: () -> Unit = {}, val edited: () -> Unit = {},
    val start: (String) -> Unit = {}, val resume: (String) -> Unit = {},
    val checkpoint: (String) -> Unit = {}
)

@Composable
fun AppNavigation(viewModel: ConnectivityViewModel, sessionViewModel: SessionViewModel, lessonViewModel: LessonPlayerViewModel, dictionaryRepository: com.example.chineselearningapp.domain.repository.DictionaryRepository,
    handwritingFactory: (() -> HandwritingRecognizer)? = null) {
    val connectivity by viewModel.state.collectAsStateWithLifecycle()
    val session by sessionViewModel.state.collectAsStateWithLifecycle()
    LaunchedEffect(session.account?.id) { lessonViewModel.bindIdentity(session.account?.id) }
    SessionNavigation(session, SessionActions(
        sessionViewModel::authenticate, sessionViewModel::logout, sessionViewModel::reload,
        sessionViewModel::clearFormErrors, sessionViewModel::start, sessionViewModel::resume,
        sessionViewModel::checkpoint
    ), connectivity, viewModel::retry, lessonViewModel, dictionaryRepository, handwritingFactory)
}

@Composable
fun SessionNavigation(state: SessionState, actions: SessionActions,
    connectivity: ConnectivityState = ConnectivityState.Loading, retryConnection: () -> Unit = {}, lessonViewModel: LessonPlayerViewModel? = null, dictionaryRepository: com.example.chineselearningapp.domain.repository.DictionaryRepository? = null,
    handwritingFactory: (() -> HandwritingRecognizer)? = null) {
    FreshBackground {
        // The entire graph is removed on identity changes. No protected back-stack or
        // saved destination survives logout/account switching; no login graph survives login.
        when (state.status) {
            SessionStatus.Restoring, SessionStatus.RestoreFailed ->
                Scaffold(containerColor = MaterialTheme.colorScheme.surface.copy(alpha = 0f)) { padding ->
                    Box(Modifier.padding(padding)) { RestorationScreen(state, actions.reload) }
                }
            SessionStatus.SignedOut -> key("signed-out") { AuthenticationGraph(state, actions) }
            SessionStatus.SignedIn -> key("signed-in", state.account?.id) {
                ProtectedGraph(state, actions, connectivity, retryConnection, lessonViewModel, dictionaryRepository, handwritingFactory)
            }
        }
    }
}

@Composable
private fun AuthenticationGraph(state: SessionState, actions: SessionActions) {
    val controller = rememberNavController()
    Scaffold(containerColor = MaterialTheme.colorScheme.surface.copy(alpha = 0f)) { padding ->
        NavHost(controller, startDestination = "login", modifier = Modifier.padding(padding),
            enterTransition = { fadeIn(tween(180)) }, exitTransition = { fadeOut(tween(120)) }) {
            composable("login") {
                LoginScreen(state, { email, password -> actions.authenticate(email, password, false, "") }, {
                    actions.edited()
                    controller.navigate("register") { launchSingleTop = true }
                }, actions.edited)
            }
            composable("register") {
                RegistrationScreen(state, { email, password, confirmation ->
                    actions.authenticate(email, password, true, confirmation)
                }, { actions.edited(); controller.popBackStack() }, actions.edited)
            }
        }
    }
}

@Composable
private fun RestorationScreen(state: SessionState, retry: () -> Unit) {
    Column(Modifier.fillMaxSize().padding(32.dp), verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally) {
        AppBrand()
        Spacer(Modifier.height(32.dp))
        if (state.status == SessionStatus.RestoreFailed) {
            Text(stringResource(R.string.session_restore_failed), style = MaterialTheme.typography.titleLarge)
            Spacer(Modifier.height(16.dp))
            state.error?.let { ErrorBanner(it) }
            Spacer(Modifier.height(16.dp))
            Text(stringResource(R.string.session_restore_hint), color = MaterialTheme.colorScheme.onSurfaceVariant)
            Spacer(Modifier.height(24.dp))
            PrimaryAction(R.string.session_retry, state.loading, retry)
        } else {
            CircularProgressIndicator()
            Spacer(Modifier.height(24.dp))
            Text(stringResource(R.string.session_restoring), color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
}
