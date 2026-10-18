package com.example.chineselearningapp

import androidx.activity.ComponentActivity
import androidx.activity.OnBackPressedCallback
import android.graphics.Bitmap
import androidx.compose.runtime.mutableStateOf
import androidx.compose.ui.graphics.asAndroidBitmap
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.test.platform.app.InstrumentationRegistry
import java.io.File
import com.example.chineselearningapp.core.navigation.SessionActions
import com.example.chineselearningapp.core.navigation.SessionNavigation
import com.example.chineselearningapp.domain.repository.Account
import com.example.chineselearningapp.feature.auth.AuthFieldErrors
import com.example.chineselearningapp.feature.auth.SessionState
import com.example.chineselearningapp.feature.auth.SessionStatus
import com.example.chineselearningapp.ui.theme.ChineseLearningAppTheme
import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test

/** UI fixtures only. Real authentication is independently exercised against PostgreSQL. */
class SessionNavigationTest {
    @get:Rule val compose = createAndroidComposeRule<ComponentActivity>()

    private fun screenshot(name: String) {
        val directory = File(InstrumentationRegistry.getInstrumentation().targetContext.cacheDir, "auth-ui-review")
        directory.mkdirs()
        File(directory, name).outputStream().use { stream ->
            compose.onRoot().captureToImage().asAndroidBitmap().compress(Bitmap.CompressFormat.PNG, 100, stream)
        }
    }

    @Test fun restorationNeverShowsLoginAndClearsAuthHistoryOnSuccess() {
        val state = mutableStateOf(SessionState(status = SessionStatus.Restoring))
        var rootBackCount = 0
        compose.activityRule.scenario.onActivity { activity ->
            activity.onBackPressedDispatcher.addCallback(activity, object : OnBackPressedCallback(true) {
                override fun handleOnBackPressed() { rootBackCount++ }
            })
        }
        compose.setContent { ChineseLearningAppTheme { SessionNavigation(state.value, SessionActions()) } }
        compose.onNodeWithText("Đang mở hành trình của bạn…").assertIsDisplayed()
        compose.onNodeWithTag("email_input").assertDoesNotExist()
        compose.runOnIdle { state.value = SessionState(status = SessionStatus.SignedIn,
            account = Account("fixture-user", "fixture@example.com", "An"), contentLoaded = true) }
        compose.onNodeWithText("Chào An!").assertIsDisplayed()
        compose.activityRule.scenario.onActivity { it.onBackPressedDispatcher.onBackPressed() }
        compose.runOnIdle { assertEquals(1, rootBackCount) }
        compose.onNodeWithTag("email_input").assertDoesNotExist()
    }

    @Test fun registrationLoginAndLogoutReplaceEntireNavigationGraphs() {
        val state = mutableStateOf(SessionState(status = SessionStatus.SignedOut))
        var rootBackCount = 0
        compose.activityRule.scenario.onActivity { activity ->
            activity.onBackPressedDispatcher.addCallback(activity, object : OnBackPressedCallback(true) {
                override fun handleOnBackPressed() { rootBackCount++ }
            })
        }
        val actions = SessionActions(
            authenticate = { _, _, _, _ -> state.value = SessionState(status = SessionStatus.SignedIn,
                account = Account("fixture-user", "fixture@example.com", "An"), contentLoaded = true) },
            logout = { state.value = SessionState(status = SessionStatus.SignedOut) }
        )
        compose.setContent { ChineseLearningAppTheme(darkTheme = false) { SessionNavigation(state.value, actions) } }
        compose.onNodeWithTag("email_input").assertIsDisplayed()
        screenshot("login-light.png")
        compose.onNodeWithText("Tạo tài khoản").performScrollTo().performClick()
        compose.onNodeWithTag("confirmation_input").assertExists()
        screenshot("registration-light.png")
        compose.onNodeWithTag("confirmation_input").performScrollTo().assertIsDisplayed()
        compose.onNodeWithTag("email_input").performTextInput("fixture@example.com")
        compose.onNodeWithTag("password_input").performScrollTo().performTextInput("123456")
        compose.onNodeWithTag("confirmation_input").performScrollTo().performTextInput("123456")
        compose.onNodeWithTag("auth_submit").performScrollTo().performClick()
        compose.onNodeWithText("Chào An!").assertIsDisplayed()
        screenshot("home-light.png")
        compose.onNodeWithTag("confirmation_input").assertDoesNotExist()
        compose.activityRule.scenario.onActivity { it.onBackPressedDispatcher.onBackPressed() }
        compose.runOnIdle { assertEquals(1, rootBackCount) }
        compose.onNodeWithText("Đăng xuất").performClick()
        compose.onNodeWithTag("email_input").assertIsDisplayed()
        compose.activityRule.scenario.onActivity { it.onBackPressedDispatcher.onBackPressed() }
        compose.runOnIdle { assertEquals(2, rootBackCount) }
        compose.onNodeWithText("Chào An!").assertDoesNotExist()
    }

    @Test fun fieldErrorsAndBackendErrorsRemainDistinctInDarkMode() {
        val state = SessionState(status = SessionStatus.SignedOut, error = R.string.auth_server_validation,
            fieldErrors = AuthFieldErrors(password = R.string.auth_password_error))
        compose.setContent { ChineseLearningAppTheme(darkTheme = true) { SessionNavigation(state, SessionActions()) } }
        compose.onNodeWithText("Máy chủ chưa chấp nhận thông tin này. Kiểm tra email và mật khẩu rồi thử lại.")
            .performScrollTo().assertIsDisplayed()
        compose.onNodeWithText("Mật khẩu cần có từ 6 đến 128 ký tự.").performScrollTo().assertIsDisplayed()
        compose.onNodeWithContentDescription("Hiện mật khẩu").performScrollTo().performClick()
        compose.onNodeWithContentDescription("Ẩn mật khẩu").assertExists()
    }
}
