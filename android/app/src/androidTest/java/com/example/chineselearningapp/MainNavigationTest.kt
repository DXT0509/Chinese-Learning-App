package com.example.chineselearningapp

import androidx.activity.ComponentActivity
import androidx.compose.runtime.mutableStateOf
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.StateRestorationTester
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import com.example.chineselearningapp.core.navigation.SessionActions
import com.example.chineselearningapp.core.navigation.SessionNavigation
import com.example.chineselearningapp.domain.repository.Account
import com.example.chineselearningapp.feature.auth.SessionState
import com.example.chineselearningapp.feature.auth.SessionStatus
import com.example.chineselearningapp.ui.theme.ChineseLearningAppTheme
import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test

class MainNavigationTest {
    @get:Rule val compose = createAndroidComposeRule<ComponentActivity>()

    private val signedIn = SessionState(status = SessionStatus.SignedIn,
        account = Account("account", "learner@example.com", "An"), contentLoaded = true)

    private fun back() {
        compose.activityRule.scenario.onActivity { it.onBackPressedDispatcher.onBackPressed() }
        compose.waitForIdle()
    }

    @Test fun tabsRestoreSelectionAndBackReturnsHomeWithoutDuplicateEntries() {
        val restoration = StateRestorationTester(compose)
        restoration.setContent { ChineseLearningAppTheme { SessionNavigation(signedIn, SessionActions()) } }
        compose.onNodeWithTag("tab_Home").assertIsSelected()
        compose.onNodeWithTag("profile_logout").assertDoesNotExist()
        compose.onNodeWithText("Đăng xuất").assertDoesNotExist()
        listOf("Learning", "Review", "Profile", "Home", "Review").forEach { tab ->
            compose.onNodeWithTag("tab_$tab").performClick().assertIsSelected()
        }
        restoration.emulateSavedInstanceStateRestore()
        compose.onNodeWithTag("tab_Review").assertIsSelected()
        compose.onNodeWithTag("tab_Review").performClick()
        back()
        compose.onNodeWithTag("tab_Home").assertIsSelected()
        compose.onNodeWithTag("tab_Learning").performClick()
        compose.onNodeWithText("Khám phá bài học xem trước").performScrollTo().performClick()
        compose.onNodeWithTag("main_navigation").assertDoesNotExist()
        back()
        compose.onNodeWithTag("tab_Learning").assertIsSelected()
    }

    @Test fun confirmationCanCancelAndRestoreAndLogoutDiscardsProtectedHistory() {
        val state = mutableStateOf(signedIn)
        var logouts = 0
        var rootBacks = 0
        compose.activityRule.scenario.onActivity { activity ->
            activity.onBackPressedDispatcher.addCallback(activity,
                object : androidx.activity.OnBackPressedCallback(true) {
                    override fun handleOnBackPressed() { rootBacks++ }
                })
        }
        val restoration = StateRestorationTester(compose)
        restoration.setContent {
            ChineseLearningAppTheme {
                SessionNavigation(state.value, SessionActions(logout = {
                    logouts++
                    state.value = SessionState(status = SessionStatus.SignedOut)
                }))
            }
        }
        compose.onNodeWithTag("tab_Profile").performClick()
        compose.onNodeWithTag("profile_logout").performScrollTo().performClick()
        compose.onNodeWithTag("cancel_logout").performClick()
        compose.runOnIdle { assertEquals(0, logouts) }
        compose.onNodeWithTag("confirm_logout").assertDoesNotExist()
        compose.onNodeWithTag("profile_logout").performClick()
        restoration.emulateSavedInstanceStateRestore()
        compose.onNodeWithTag("confirm_logout").performClick()
        compose.runOnIdle { assertEquals(1, logouts) }
        compose.onNodeWithTag("main_navigation").assertDoesNotExist()
        compose.onNodeWithTag("email_input").assertIsDisplayed()
        back()
        compose.runOnIdle { assertEquals(1, rootBacks) }
        compose.onNodeWithTag("profile_logout").assertDoesNotExist()
        compose.onNodeWithTag("email_input").assertIsDisplayed()
        compose.onNodeWithText("Tạo tài khoản").performScrollTo().performClick()
        compose.onNodeWithTag("confirmation_input").assertExists()
        compose.onNodeWithTag("main_navigation").assertDoesNotExist()
    }

    @Test fun homeScrollPositionSurvivesTabSwitchAndSavedStateRestoration() {
        val restoration = StateRestorationTester(compose)
        restoration.setContent { ChineseLearningAppTheme { SessionNavigation(signedIn, SessionActions()) } }
        compose.onNodeWithText("Góc học tập cá nhân").performScrollTo().assertIsDisplayed()
        compose.onNodeWithTag("tab_Review").performClick()
        compose.onNodeWithTag("tab_Home").performClick()
        compose.onNodeWithText("Góc học tập cá nhân").assertIsDisplayed()
        restoration.emulateSavedInstanceStateRestore()
        compose.onNodeWithTag("tab_Home").assertIsSelected()
        compose.onNodeWithText("Góc học tập cá nhân").assertIsDisplayed()
    }

    @Test fun profileShowsRealAccountAndDisablesLogoutWhileBusyInDarkMode() {
        compose.setContent {
            ChineseLearningAppTheme(darkTheme = true) {
                SessionNavigation(signedIn.copy(loading = true, error = R.string.session_network_error), SessionActions())
            }
        }
        compose.onNodeWithTag("tab_Profile").performClick()
        compose.onNodeWithText("An").assertExists()
        compose.onAllNodesWithText("learner@example.com").assertCountEquals(2)
        compose.onNodeWithTag("profile_logout").performScrollTo().assertIsNotEnabled()
    }
}
