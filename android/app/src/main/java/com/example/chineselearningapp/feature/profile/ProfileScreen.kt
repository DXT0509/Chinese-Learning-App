package com.example.chineselearningapp.feature.profile

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.example.chineselearningapp.R
import com.example.chineselearningapp.core.designsystem.*
import com.example.chineselearningapp.feature.auth.SessionState

@Composable
fun ProfileScreen(state: SessionState, logout: () -> Unit) {
    var confirming by rememberSaveable { mutableStateOf(false) }
    PageColumn {
        Text(stringResource(R.string.profile), style = MaterialTheme.typography.headlineMedium)
        OutlinedCard(colors = CardDefaults.outlinedCardColors(containerColor = MaterialTheme.colorScheme.surface)) {
            Column(Modifier.fillMaxWidth().padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(16.dp)) {
                Surface(shape = CircleShape, color = MaterialTheme.colorScheme.primaryContainer) {
                    Box(Modifier.size(88.dp), contentAlignment = Alignment.Center) {
                        Icon(painterResource(R.drawable.ic_person), null, Modifier.size(44.dp), tint = MaterialTheme.colorScheme.primary)
                    }
                }
                state.account?.displayName?.takeIf { it.isNotBlank() }?.let {
                    Text(it, style = MaterialTheme.typography.titleLarge)
                }
                state.account?.email?.let { Text(it, style = MaterialTheme.typography.bodyLarge) }
            }
        }
        Text(stringResource(R.string.profile_account), style = MaterialTheme.typography.titleLarge)
        Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {
            Column(Modifier.fillMaxWidth().padding(20.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(stringResource(R.string.profile_email), style = MaterialTheme.typography.labelLarge)
                state.account?.email?.let { Text(it) }
                Text(stringResource(R.string.auth_unverified), color = MaterialTheme.colorScheme.onSurfaceVariant,
                    style = MaterialTheme.typography.bodySmall)
            }
        }
        Text(stringResource(R.string.profile_settings), style = MaterialTheme.typography.titleLarge)
        Text(stringResource(R.string.profile_settings_soon), color = MaterialTheme.colorScheme.onSurfaceVariant)
        HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant)
        state.error?.let { ErrorBanner(it) }
        OutlinedButton(onClick = { confirming = true }, enabled = !state.loading,
            modifier = Modifier.fillMaxWidth().heightIn(min = 56.dp).testTag("profile_logout"),
            colors = ButtonDefaults.outlinedButtonColors(contentColor = MaterialTheme.colorScheme.error)) {
            if (state.loading) {
                CircularProgressIndicator(Modifier.size(20.dp), strokeWidth = 2.dp)
                Spacer(Modifier.width(12.dp))
                Text(stringResource(R.string.action_processing))
            } else Text(stringResource(R.string.auth_logout))
        }
    }
    if (confirming) {
        AlertDialog(onDismissRequest = { confirming = false },
            title = { Text(stringResource(R.string.logout_confirm_title)) },
            text = { Text(stringResource(R.string.logout_confirm_body)) },
            confirmButton = {
                TextButton(onClick = { confirming = false; logout() }, enabled = !state.loading,
                    modifier = Modifier.testTag("confirm_logout"),
                    colors = ButtonDefaults.textButtonColors(contentColor = MaterialTheme.colorScheme.error)) {
                    Text(stringResource(R.string.auth_logout))
                }
            },
            dismissButton = {
                TextButton(onClick = { confirming = false }, modifier = Modifier.testTag("cancel_logout")) {
                    Text(stringResource(R.string.logout_cancel))
                }
            })
    }
}
