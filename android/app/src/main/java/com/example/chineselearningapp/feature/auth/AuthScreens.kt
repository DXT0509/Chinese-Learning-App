package com.example.chineselearningapp.feature.auth

import androidx.annotation.StringRes
import androidx.compose.animation.animateContentSize
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusDirection
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.unit.dp
import com.example.chineselearningapp.R
import com.example.chineselearningapp.core.designsystem.*

@Composable
fun LoginScreen(state: SessionState, submit: (String, String) -> Unit, register: () -> Unit, edited: () -> Unit) {
    AuthForm(false, state, { email, password, _ -> submit(email, password) }, register, edited)
}

@Composable
fun RegistrationScreen(state: SessionState, submit: (String, String, String) -> Unit, login: () -> Unit, edited: () -> Unit) {
    AuthForm(true, state, submit, login, edited)
}

@Composable
private fun AuthForm(
    register: Boolean,
    state: SessionState,
    submit: (String, String, String) -> Unit,
    switchScreen: () -> Unit,
    edited: () -> Unit
) {
    var email by rememberSaveable { mutableStateOf("") }
    // Passwords and visibility are intentionally never saved during process recreation.
    var password by remember { mutableStateOf("") }
    var confirmation by remember { mutableStateOf("") }
    val focus = LocalFocusManager.current
    val keyboard = LocalSoftwareKeyboardController.current
    val send = {
        focus.clearFocus()
        keyboard?.hide()
        submit(email, password, confirmation)
    }
    LaunchedEffect(state.loading) {
        if (state.loading) { password = ""; confirmation = "" }
    }
    PageColumn {
        Spacer(Modifier.height(8.dp))
        AppBrand()
        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Text(stringResource(R.string.auth_eyebrow), style = MaterialTheme.typography.labelLarge,
                color = MaterialTheme.colorScheme.primary)
            Text(stringResource(if (register) R.string.register_heading else R.string.login_heading),
                style = MaterialTheme.typography.headlineLarge)
            Text(stringResource(if (register) R.string.register_intro else R.string.login_intro),
                color = MaterialTheme.colorScheme.onSurfaceVariant, style = MaterialTheme.typography.bodyLarge)
        }
        Card(shape = MaterialTheme.shapes.large, colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
            border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
            modifier = Modifier.fillMaxWidth().animateContentSize()) {
            Column(Modifier.padding(24.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {
                Text(stringResource(if (register) R.string.auth_register else R.string.login), style = MaterialTheme.typography.titleLarge)
                state.error?.let { ErrorBanner(it) }
                OutlinedTextField(
                    value = email, onValueChange = { email = it; edited() },
                    modifier = Modifier.fillMaxWidth().testTag("email_input"),
                    label = { Text(stringResource(R.string.auth_email)) },
                    placeholder = { Text(stringResource(R.string.auth_email_example)) },
                    singleLine = true, enabled = !state.loading, shape = MaterialTheme.shapes.small,
                    isError = state.fieldErrors.email != null,
                    supportingText = state.fieldErrors.email?.let { error -> { Text(stringResource(error)) } },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email, imeAction = ImeAction.Next),
                    keyboardActions = KeyboardActions(onNext = { focus.moveFocus(FocusDirection.Down) })
                )
                PasswordField(password, { password = it; edited() }, R.string.auth_password_label,
                    state.fieldErrors.password, !state.loading, "password_input",
                    if (register) ImeAction.Next else ImeAction.Done,
                    KeyboardActions(onNext = { focus.moveFocus(FocusDirection.Down) }, onDone = { send() }))
                if (register) {
                    PasswordField(confirmation, { confirmation = it; edited() }, R.string.auth_confirm_password,
                        state.fieldErrors.confirmation, !state.loading, "confirmation_input", ImeAction.Done,
                        KeyboardActions(onDone = { send() }))
                }
                Text(stringResource(R.string.auth_password_hint), style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant)
                PrimaryAction(if (register) R.string.auth_register else R.string.login, state.loading, send,
                    modifier = Modifier.testTag("auth_submit"))
                TextButton(onClick = switchScreen, enabled = !state.loading, modifier = Modifier.fillMaxWidth().heightIn(min = 48.dp)) {
                    Text(stringResource(if (register) R.string.auth_to_login else R.string.auth_to_register))
                }
            }
        }
        Text(stringResource(R.string.auth_unverified), style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant)
        Spacer(Modifier.height(8.dp))
    }
}

@Composable
private fun PasswordField(
    value: String, changed: (String) -> Unit, @StringRes label: Int, @StringRes error: Int?,
    enabled: Boolean, tag: String, action: ImeAction, keyboardActions: KeyboardActions
) {
    var visible by remember { mutableStateOf(false) }
    OutlinedTextField(
        value, changed, modifier = Modifier.fillMaxWidth().testTag(tag),
        label = { Text(stringResource(label)) }, singleLine = true, enabled = enabled,
        shape = MaterialTheme.shapes.small, isError = error != null,
        supportingText = error?.let { message -> { Text(stringResource(message)) } },
        visualTransformation = if (visible) VisualTransformation.None else PasswordVisualTransformation(),
        trailingIcon = {
            IconButton(onClick = { visible = !visible }, enabled = enabled) {
                Icon(painterResource(if (visible) R.drawable.ic_visibility_off else R.drawable.ic_visibility),
                    stringResource(if (visible) R.string.auth_hide_password else R.string.auth_show_password))
            }
        },
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password, imeAction = action),
        keyboardActions = keyboardActions
    )
}
