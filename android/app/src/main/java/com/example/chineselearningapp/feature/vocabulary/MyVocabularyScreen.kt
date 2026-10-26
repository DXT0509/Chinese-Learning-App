package com.example.chineselearningapp.feature.vocabulary

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.example.chineselearningapp.R
import com.example.chineselearningapp.domain.repository.SavedWord

@Composable
fun SavedVocabularyAction(state: SavedEntryState, save: () -> Unit, retry: () -> Unit) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Button(onClick = save, enabled = state.statusKnown && !state.loading && state.savedId == null,
            modifier = Modifier.fillMaxWidth()) {
            Text(stringResource(if (state.savedId != null) R.string.wordbook_saved else R.string.wordbook_save))
        }
        if (state.loading) LinearProgressIndicator(Modifier.fillMaxWidth())
        if (state.confirmed) Text(stringResource(R.string.wordbook_save_success))
        if (state.error) {
            Text(stringResource(R.string.wordbook_error))
            TextButton(onClick = retry) { Text(stringResource(R.string.dictionary_retry)) }
        }
    }
}

@Composable
fun MyVocabularyScreen(state: WordbookState, edit: (String) -> Unit, refresh: () -> Unit,
    more: () -> Unit, open: (String) -> Unit, explore: () -> Unit, askRemove: (SavedWord) -> Unit,
    cancelRemove: () -> Unit, confirmRemove: () -> Unit) {
    Column(Modifier.fillMaxSize().imePadding().padding(horizontal = 24.dp)) {
        Text(stringResource(R.string.wordbook_title), style = MaterialTheme.typography.headlineMedium)
        Text(stringResource(R.string.wordbook_count, state.total))
        OutlinedTextField(state.query, edit, Modifier.fillMaxWidth(), singleLine = true,
            label = { Text(stringResource(R.string.wordbook_search)) }, isError = state.invalid)
        if (state.invalid) Text(stringResource(R.string.dictionary_invalid))
        if (state.loading) LinearProgressIndicator(Modifier.fillMaxWidth())
        if (state.error || state.removeError) {
            Text(stringResource(R.string.wordbook_error))
            TextButton(onClick = refresh) { Text(stringResource(R.string.dictionary_retry)) }
        }
        if (state.removed) Text(stringResource(R.string.wordbook_remove_success))
        LazyColumn(Modifier.weight(1f), contentPadding = PaddingValues(vertical = 16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)) {
            if (!state.loading && !state.error && !state.invalid && state.items.isEmpty()) item {
                Text(stringResource(if (state.query.isBlank()) R.string.wordbook_empty else R.string.dictionary_empty))
                Button(onClick = explore) { Text(stringResource(R.string.wordbook_explore)) }
            }
            items(state.items, key = { it.id }) { word ->
                Card(onClick = { open(word.entryId) }, modifier = Modifier.fillMaxWidth(),
                    shape = MaterialTheme.shapes.large,
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {
                    Column(Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Text(word.simplified, style = MaterialTheme.typography.headlineMedium)
                        Text(word.pinyin, color = MaterialTheme.colorScheme.primary)
                        if (!word.vietnamese.isNullOrBlank()) Text(word.vietnamese, maxLines = 3, overflow = TextOverflow.Ellipsis)
                        else if (!word.english.isNullOrBlank()) Text(stringResource(R.string.wordbook_english, word.english),
                            maxLines = 3, overflow = TextOverflow.Ellipsis)
                        if (!word.active) Text(stringResource(R.string.wordbook_inactive))
                        TextButton(onClick = { askRemove(word) }, enabled = state.removing == null) {
                            Text(stringResource(R.string.wordbook_remove))
                        }
                    }
                }
            }
            if (state.nextCursor != null) item {
                OutlinedButton(onClick = more, enabled = !state.loading) { Text(stringResource(R.string.dictionary_more)) }
            }
        }
    }
    state.pendingRemoval?.let { word ->
        AlertDialog(onDismissRequest = cancelRemove,
            title = { Text(stringResource(R.string.wordbook_remove)) },
            text = { Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(stringResource(R.string.wordbook_confirm_remove, word.simplified))
                if (state.removing != null) LinearProgressIndicator(Modifier.fillMaxWidth())
                if (state.removeError) Text(stringResource(R.string.wordbook_error))
            } },
            confirmButton = { TextButton(onClick = confirmRemove, enabled = state.removing == null) {
                Text(stringResource(R.string.wordbook_remove)) } },
            dismissButton = { TextButton(onClick = cancelRemove, enabled = state.removing == null) {
                Text(stringResource(R.string.wordbook_cancel)) } })
    }
}
