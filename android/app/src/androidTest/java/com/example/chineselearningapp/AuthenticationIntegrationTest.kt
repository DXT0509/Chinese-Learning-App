package com.example.chineselearningapp

import androidx.activity.ComponentActivity
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.compose.runtime.getValue
import androidx.test.platform.app.InstrumentationRegistry
import com.example.chineselearningapp.core.navigation.SessionActions
import com.example.chineselearningapp.core.navigation.SessionNavigation
import com.example.chineselearningapp.core.network.SessionApi
import com.example.chineselearningapp.core.network.SessionTokenStore
import com.example.chineselearningapp.core.network.TokensDto
import com.example.chineselearningapp.feature.auth.SessionStatus
import com.example.chineselearningapp.feature.auth.SessionViewModel
import com.example.chineselearningapp.feature.auth.data.RemoteSessionRepository
import com.example.chineselearningapp.ui.theme.ChineseLearningAppTheme
import java.util.UUID
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

/** Opt-in only: requires a dedicated test API/database on USB-reversed port 8001.
 * Uses memory tokens and never reads, replaces or clears the user's real session vault.
 */
class AuthenticationIntegrationTest {
    @get:Rule val compose = createAndroidComposeRule<ComponentActivity>()

    @Test fun sixCharacterRegistrationLoginAndLogoutAgainstFastApi() {
        val url = InstrumentationRegistry.getArguments().getString("test_api_base_url")
        assumeTrue("Start an isolated test API and pass test_api_base_url", url == "http://127.0.0.1:8001/")
        val api = Retrofit.Builder().baseUrl(requireNotNull(url))
            .addConverterFactory(GsonConverterFactory.create()).build().create(SessionApi::class.java)
        val store = object : SessionTokenStore {
            private var tokens: TokensDto? = null
            override fun read() = tokens
            override fun write(tokens: TokensDto) { this.tokens = tokens }
            override fun clear() { tokens = null }
        }
        val repository = RemoteSessionRepository(api, store)
        val model = ViewModelProvider(compose.activity, object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: Class<T>): T = SessionViewModel(repository) as T
        })[SessionViewModel::class.java]
        compose.setContent {
            val state by model.state.collectAsStateWithLifecycle()
            ChineseLearningAppTheme {
                SessionNavigation(state, SessionActions(model::authenticate, model::logout, model::reload,
                    model::clearFormErrors, model::start, model::resume, model::checkpoint))
            }
        }
        compose.waitUntil(15000) { model.state.value.status == SessionStatus.SignedOut }
        val email = "usb-${UUID.randomUUID().toString().take(8)}@example.com"
        compose.onNodeWithText("Tạo tài khoản").performScrollTo().performClick()
        compose.onNodeWithTag("email_input").performScrollTo().performTextInput(email)
        compose.onNodeWithTag("password_input").performScrollTo().performTextInput("123456")
        compose.onNodeWithTag("confirmation_input").performScrollTo().performTextInput("123456")
        compose.onNodeWithTag("auth_submit").performScrollTo().performClick()
        compose.waitUntil(20000) { model.state.value.status == SessionStatus.SignedIn && !model.state.value.loading }
        compose.onNodeWithText(email).assertIsDisplayed()
        compose.onNodeWithTag("tab_Profile").performClick()
        compose.onNodeWithTag("profile_logout").performScrollTo().performClick()
        compose.onNodeWithTag("confirm_logout").performClick()
        compose.waitUntil(15000) { model.state.value.status == SessionStatus.SignedOut }
        compose.onNodeWithTag("email_input").performTextInput(email)
        compose.onNodeWithTag("password_input").performScrollTo().performTextInput("123456")
        compose.onNodeWithTag("auth_submit").performScrollTo().performClick()
        compose.waitUntil(20000) { model.state.value.status == SessionStatus.SignedIn && !model.state.value.loading }
        compose.onNodeWithText(email).assertIsDisplayed()
        compose.onNodeWithTag("tab_Profile").performClick()
        compose.onNodeWithTag("profile_logout").performScrollTo().performClick()
        compose.onNodeWithTag("confirm_logout").performClick()
        compose.waitUntil(15000) { model.state.value.status == SessionStatus.SignedOut }
        compose.onNodeWithTag("email_input").assertExists()
    }
}
