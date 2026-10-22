package com.example.chineselearningapp.feature.learning

import androidx.compose.material3.*
import androidx.compose.foundation.layout.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.runtime.Composable
import androidx.compose.ui.res.stringResource
import com.example.chineselearningapp.R
import com.example.chineselearningapp.core.designsystem.*

@Composable
fun LearningScreen(openLessons: () -> Unit, openConnectivity: () -> Unit, openDictionary: () -> Unit = {}) {
    PageColumn {
        Card(onClick = openDictionary, colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer),
            shape = MaterialTheme.shapes.large) {
            Column(Modifier.fillMaxWidth().padding(24.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(stringResource(R.string.dictionary_title), style = MaterialTheme.typography.headlineSmall)
                Text(stringResource(R.string.dictionary_intro), style = MaterialTheme.typography.bodyMedium)
            }
        }
        FeatureEmptyState(R.string.learning_title, R.string.learning_soon, R.drawable.ic_book)
        PrimaryAction(R.string.learning_catalog, false, openLessons)
        TextButton(onClick = openConnectivity) { Text(stringResource(R.string.connection_title)) }
    }
}
