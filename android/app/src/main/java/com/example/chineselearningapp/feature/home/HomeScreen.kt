package com.example.chineselearningapp.feature.home

import androidx.annotation.DrawableRes
import androidx.annotation.StringRes
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.example.chineselearningapp.R
import com.example.chineselearningapp.core.designsystem.*
import com.example.chineselearningapp.feature.auth.SessionState

@Composable
fun HomeScreen(
    state: SessionState, openLessons: () -> Unit, openRoadmap: () -> Unit,
    openVocabulary: () -> Unit, openReview: () -> Unit, openProfile: () -> Unit,
    reload: () -> Unit
) {
    PageColumn {
        AppBrand(compact = true)
        val name = state.account?.displayName?.takeIf { it.isNotBlank() }
            ?: state.account?.email?.substringBefore('@') ?: stringResource(R.string.home_friend)
        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(stringResource(R.string.home_greeting, name), style = MaterialTheme.typography.headlineMedium)
            Text(stringResource(R.string.home_intro), color = MaterialTheme.colorScheme.onSurfaceVariant)
            state.account?.email?.let { email ->
                Text(email, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
        }
        state.error?.let {
            ErrorBanner(it)
            TextButton(onClick = reload, enabled = !state.loading) { Text(stringResource(R.string.session_retry)) }
        }
        LearningInvitation(state, openLessons)
        ContinueSection(state, openLessons)
        RoadmapEntry(openRoadmap)
        Text(stringResource(R.string.home_section_explore), style = MaterialTheme.typography.titleLarge)
        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            FutureFeatureEntry(R.drawable.ic_book, R.string.vocabulary, R.string.home_vocabulary_hint, openVocabulary)
            FutureFeatureEntry(R.drawable.ic_path, R.string.review, R.string.home_review_hint, openReview)
            FutureFeatureEntry(R.drawable.ic_person, R.string.profile, R.string.home_profile_hint, openProfile, comingSoon = false)
        }
        TextButton(onClick = reload, enabled = !state.loading, modifier = Modifier.fillMaxWidth()) {
            Text(stringResource(R.string.session_retry))
        }
        Spacer(Modifier.height(8.dp))
    }
}

@Composable
private fun LearningInvitation(state: SessionState, openLessons: () -> Unit) {
    Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer),
        shape = MaterialTheme.shapes.large) {
        Column(Modifier.fillMaxWidth().padding(24.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically) {
                Text(stringResource(R.string.home_preview_badge), style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onPrimaryContainer, modifier = Modifier.weight(1f))
                Icon(painterResource(R.drawable.ic_book), null, Modifier.size(36.dp), tint = MaterialTheme.colorScheme.primary)
            }
            Text(stringResource(R.string.home_hero_title), style = MaterialTheme.typography.headlineMedium,
                color = MaterialTheme.colorScheme.onPrimaryContainer)
            Text(stringResource(R.string.home_hero_body), color = MaterialTheme.colorScheme.onPrimaryContainer)
            PrimaryAction(R.string.home_start, state.loading, openLessons, enabled = state.catalog.isNotEmpty())
            if (!state.contentLoaded && state.loading) Text(stringResource(R.string.home_content_loading))
            else if (!state.contentLoaded && state.error != null) Text(stringResource(R.string.home_content_unavailable),
                color = MaterialTheme.colorScheme.onPrimaryContainer)
            else if (state.contentLoaded && state.catalog.isEmpty()) Text(stringResource(R.string.home_catalog_empty),
                color = MaterialTheme.colorScheme.onPrimaryContainer, style = MaterialTheme.typography.bodyMedium)
            Text(stringResource(R.string.preview_notice), style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onPrimaryContainer)
        }
    }
}

@Composable
private fun ContinueSection(state: SessionState, openLessons: () -> Unit) {
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text(stringResource(R.string.home_continue), style = MaterialTheme.typography.titleLarge)
        Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {
            Column(Modifier.fillMaxWidth().padding(20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                val run = state.runs.firstOrNull()
                if (run != null) {
                    val title = state.catalog.firstOrNull { it.versionId == run.versionId }?.title
                        ?: stringResource(R.string.home_run_label)
                    Text(title, style = MaterialTheme.typography.titleMedium)
                    Text(stringResource(R.string.preview_resume_pinned), color = MaterialTheme.colorScheme.onSurfaceVariant)
                    OutlinedButton(onClick = openLessons, modifier = Modifier.fillMaxWidth().heightIn(min = 48.dp),
                        enabled = !state.loading) { Text(stringResource(R.string.home_continue_action)) }
                } else {
                    Text(stringResource(when {
                        state.contentLoaded -> R.string.home_continue_empty
                        state.error != null -> R.string.home_content_unavailable
                        else -> R.string.home_content_loading
                    }),
                        color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
            }
        }
    }
}

@Composable
private fun RoadmapEntry(open: () -> Unit) {
    OutlinedCard(onClick = open, shape = MaterialTheme.shapes.large) {
        Column(Modifier.fillMaxWidth().padding(24.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {
            Icon(painterResource(R.drawable.ic_path), null, Modifier.size(40.dp), tint = MaterialTheme.colorScheme.primary)
            Text(stringResource(R.string.home_roadmap_title), style = MaterialTheme.typography.titleLarge)
            Text(stringResource(R.string.home_roadmap_body), color = MaterialTheme.colorScheme.onSurfaceVariant)
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                Text(stringResource(R.string.home_roadmap_action), color = MaterialTheme.colorScheme.primary,
                    style = MaterialTheme.typography.labelLarge)
                Icon(painterResource(R.drawable.ic_arrow), null, tint = MaterialTheme.colorScheme.primary)
            }
        }
    }
}

@Composable
private fun FutureFeatureEntry(@DrawableRes icon: Int, @StringRes title: Int, @StringRes description: Int, open: () -> Unit, comingSoon: Boolean = true) {
    Card(onClick = open, colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {
        Row(Modifier.fillMaxWidth().padding(20.dp), verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(16.dp)) {
            Icon(painterResource(icon), null, tint = MaterialTheme.colorScheme.primary)
            Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(stringResource(title), style = MaterialTheme.typography.titleMedium)
                Text(stringResource(description), style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant)
                if (comingSoon) Text(stringResource(R.string.coming_soon), style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.primary)
            }
            Icon(painterResource(R.drawable.ic_arrow), null, tint = MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
}
