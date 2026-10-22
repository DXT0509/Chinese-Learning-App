package com.example.chineselearningapp.feature.lesson

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.selection.toggleable
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.unit.dp
import com.example.chineselearningapp.R
import com.example.chineselearningapp.core.designsystem.*
import com.example.chineselearningapp.feature.auth.SessionState

@Composable
fun PreviewLessonsScreen(state: SessionState, start: (String) -> Unit, resume: (String) -> Unit,
    checkpoint: (String) -> Unit, reload: () -> Unit) {
    var consent by rememberSaveable { mutableStateOf(false) }
    PageColumn {
        Text(stringResource(R.string.lessons_heading), style = MaterialTheme.typography.headlineMedium)
        Text(stringResource(R.string.preview_notice), color = MaterialTheme.colorScheme.onSurfaceVariant)
        state.error?.let { ErrorBanner(it) }
        if (state.loading) LinearProgressIndicator(Modifier.fillMaxWidth())
        Row(Modifier.fillMaxWidth().toggleable(consent, role = Role.Checkbox, onValueChange = { consent = it })
            .padding(vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
            Checkbox(consent, onCheckedChange = null)
            Text(stringResource(R.string.preview_consent), Modifier.padding(start = 12.dp))
        }
        if (state.contentLoaded && state.catalog.isEmpty()) Text(stringResource(R.string.home_catalog_empty))
        state.catalog.sortedByDescending { it.version }.forEach { lesson ->
            Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {
                Column(Modifier.fillMaxWidth().padding(20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text(lesson.title, style = MaterialTheme.typography.titleMedium)
                    Text(stringResource(R.string.lesson_version_label, lesson.version), color = MaterialTheme.colorScheme.onSurfaceVariant)
                    PrimaryAction(R.string.preview_start, state.loading, { start(lesson.versionId) }, enabled = consent)
                }
            }
        }
        if (state.runs.isNotEmpty()) {
            Text(stringResource(R.string.home_continue), style = MaterialTheme.typography.titleLarge)
            state.runs.forEach { run ->
                OutlinedButton(onClick = { resume(run.id) }, enabled = consent && !state.loading,
                    modifier = Modifier.fillMaxWidth().heightIn(min = 56.dp)) {
                    Text(state.catalog.firstOrNull { it.versionId == run.versionId }?.title ?: stringResource(R.string.home_run_label))
                }
            }
        }
        TextButton(onClick = reload, enabled = !state.loading) { Text(stringResource(R.string.session_retry)) }
    }
}
