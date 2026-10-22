package com.example.chineselearningapp.feature.dictionary

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.text.selection.SelectionContainer
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.platform.LocalUriHandler
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.input.TextFieldValue
import androidx.compose.ui.unit.dp
import com.example.chineselearningapp.R
import com.example.chineselearningapp.domain.model.*
import com.example.chineselearningapp.feature.dictionary.handwriting.*
import androidx.activity.compose.BackHandler
import androidx.lifecycle.compose.collectAsStateWithLifecycle

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DictionarySearchScreen(state: DictionarySearchState, edit: (String, Boolean) -> Unit,
    retry: () -> Unit, loadMore: () -> Unit, open: (String) -> Unit, back: () -> Unit,
    handwriting: HandwritingViewModel? = null) {
    // TextFieldValue retains selection and IME composition; the ViewModel owns the query.
    var field by rememberSaveable(stateSaver = TextFieldValue.Saver) { mutableStateOf(TextFieldValue(state.query)) }
    val keyboard = LocalSoftwareKeyboardController.current
    val focus = LocalFocusManager.current
    val inkState = handwriting?.state?.collectAsStateWithLifecycle()?.value ?: HandwritingState()
    val panelOpen = inkState.phase != HandwritingPhase.Closed
    BackHandler(panelOpen) { handwriting?.close() }
    val context = LocalContext.current
    // Preserve completed strokes and panel state on rotation, close on actual navigation.
    DisposableEffect(handwriting, context) { onDispose {
        var owner = context
        while (owner is android.content.ContextWrapper && owner !is android.app.Activity) owner = owner.baseContext
        if ((owner as? android.app.Activity)?.isChangingConfigurations != true) handwriting?.close()
    } }
    Column(Modifier.fillMaxSize().imePadding()) {
        DictionaryTopBar { if (panelOpen) handwriting?.close() else back() }
        OutlinedTextField(value = field, onValueChange = {
            field = it
            edit(it.text, it.composition != null)
        }, modifier = Modifier.fillMaxWidth().padding(horizontal = 24.dp),
            label = { Text(stringResource(R.string.dictionary_query)) }, singleLine = true,
            shape = MaterialTheme.shapes.large,
            leadingIcon = { if (handwriting != null) IconButton(onClick = {
                if (panelOpen) handwriting.close() else {
                    keyboard?.hide(); focus.clearFocus(); handwriting.open()
                }
            }) { Icon(painterResource(R.drawable.ic_handwriting), stringResource(R.string.ink_title)) } },
            isError = state.phase == DictionaryPhase.Invalid,
            trailingIcon = { if (field.text.isNotEmpty()) TextButton(onClick = {
                field = TextFieldValue(""); edit("", false)
            }) { Text(stringResource(R.string.dictionary_clear)) } })
        LazyColumn(Modifier.fillMaxSize(), contentPadding = PaddingValues(24.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)) {
            if (panelOpen && handwriting != null) item(key = "handwriting") {
                HandwritingPanel(inkState, handwriting) { candidate ->
                    field = insertHandwriting(field, candidate)
                    edit(field.text, false)
                }
            }
            if (state.phase != DictionaryPhase.Results) item {
                DictionaryStatus(state.phase, retry)
            }
            if (state.phase == DictionaryPhase.Results) {
                items(state.items, key = { it.entryId }) { suggestion ->
                    Card(onClick = { keyboard?.hide(); open(suggestion.entryId) },
                        modifier = Modifier.fillMaxWidth(), shape = MaterialTheme.shapes.large,
                        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
                        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)) {
                        Column(Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                            Text(suggestion.simplified, style = MaterialTheme.typography.headlineMedium)
                            Traditional(suggestion.simplified, suggestion.traditional)
                            Text(suggestion.pinyin, style = MaterialTheme.typography.titleMedium,
                                color = MaterialTheme.colorScheme.primary)
                            suggestion.shortVietnameseMeaning?.takeIf { it.isNotBlank() }?.let { Text(it) }
                        }
                    }
                }
                if (state.nextOffset != null) item {
                    if (state.pageError) Text(stringResource(R.string.dictionary_error))
                    if (state.loadingMore) CircularProgressIndicator()
                    else OutlinedButton(onClick = loadMore, modifier = Modifier.fillMaxWidth()) {
                        Text(stringResource(if (state.pageError) R.string.dictionary_retry else R.string.dictionary_more))
                    }
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun DictionaryTopBar(back: () -> Unit) {
    TopAppBar(title = { Text(stringResource(R.string.dictionary_title)) }, navigationIcon = {
        TextButton(onClick = back) { Text(stringResource(R.string.screen_back)) }
    }, colors = TopAppBarDefaults.topAppBarColors(containerColor = MaterialTheme.colorScheme.surface.copy(alpha = 0f)))
}

@Composable
fun DictionaryDetailScreen(state: DictionaryDetailState, retry: () -> Unit, back: () -> Unit) {
    Column(Modifier.fillMaxSize()) {
        DictionaryTopBar(back)
        LazyColumn(Modifier.fillMaxSize(), contentPadding = PaddingValues(24.dp),
            verticalArrangement = Arrangement.spacedBy(20.dp)) {
            val entry = state.entry
            if (entry == null) item { DictionaryStatus(state.phase, retry) }
            else {
                item {
                    DictionaryPanel {
                        SelectionContainer {
                            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                                Text(entry.suggestion.simplified, style = MaterialTheme.typography.displayMedium)
                                Traditional(entry.suggestion.simplified, entry.suggestion.traditional)
                                Text(entry.citationPinyin, style = MaterialTheme.typography.headlineSmall,
                                    color = MaterialTheme.colorScheme.primary)
                                entry.sinoVietnamese?.takeIf { it.isNotBlank() }?.let {
                                    Text(stringResource(R.string.dictionary_sino, it))
                                }
                            }
                        }
                    }
                }
                entry.meaningGroups.forEach { group ->
                    item(key = "meanings-" + group.key) {
                        DictionaryPanel {
                            Text(meaningLabel(group.key), style = MaterialTheme.typography.titleLarge)
                            SelectionContainer {
                                Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                                    group.value.forEach { sense -> Text("${sense.number}. ${sense.gloss}") }
                                }
                            }
                        }
                    }
                }
                val characters = entry.characters.filter { it.scope == "character" }
                if (characters.isNotEmpty()) {
                    item {
                        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            Text(stringResource(R.string.dictionary_characters), style = MaterialTheme.typography.titleLarge)
                            Text(stringResource(R.string.dictionary_character_note), style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                    }
                    items(characters) { character -> CharacterCard(character) }
                }
                item { Sources((listOf(entry.provenance) + characters.map { it.provenance }).distinct()) }
            }
        }
    }
}

@Composable
internal fun meaningLabel(language: String): String = when (language) {
    "vi" -> stringResource(R.string.dictionary_meaning_vi)
    "en" -> stringResource(R.string.dictionary_meaning_en)
    else -> stringResource(R.string.dictionary_meaning_other, language)
}

@Composable
private fun Traditional(simplified: String, traditional: String?) {
    if (!traditional.isNullOrBlank() && traditional != simplified)
        Text(stringResource(R.string.dictionary_traditional, traditional), color = MaterialTheme.colorScheme.onSurfaceVariant)
}

@Composable
internal fun CharacterCard(character: CharacterEnrichment) {
    DictionaryPanel {
        Text(character.form, style = MaterialTheme.typography.headlineLarge)
        Text(character.pinyin, color = MaterialTheme.colorScheme.primary, style = MaterialTheme.typography.titleMedium)
        character.sinoVietnamese?.takeIf { it.isNotBlank() }?.let { Text(stringResource(R.string.dictionary_sino, it)) }
        character.vietnameseGloss?.takeIf { it.isNotBlank() }?.let { Text(it) }
        if (character.matchesEntryPronunciation != true) Text(stringResource(
            if (character.matchesEntryPronunciation == false) R.string.dictionary_reading_mismatch else R.string.dictionary_reading_unknown),
            style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

@Composable
private fun DictionaryPanel(content: @Composable ColumnScope.() -> Unit) {
    Surface(Modifier.fillMaxWidth(), shape = MaterialTheme.shapes.large,
        color = MaterialTheme.colorScheme.surface, border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
        shadowElevation = 1.dp) {
        Column(Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(12.dp), content = content)
    }
}

@Composable
private fun Sources(sources: List<DictionarySource>) {
    var expanded by rememberSaveable { mutableStateOf(false) }
    val uriHandler = LocalUriHandler.current
    var linkError by remember { mutableStateOf(false) }
    fun open(url: String) {
        val uri = runCatching { java.net.URI(url) }.getOrNull()
        if (uri?.scheme !in listOf("https", "http") || uri?.host.isNullOrEmpty()) { linkError = true; return }
        linkError = runCatching { uriHandler.openUri(url) }.isFailure
    }
    DictionaryPanel {
        TextButton(onClick = { expanded = !expanded }) { Text(stringResource(R.string.dictionary_sources)) }
        if (expanded) sources.forEach { source ->
            Text(source.source, style = MaterialTheme.typography.titleMedium)
            Text(source.attribution, style = MaterialTheme.typography.bodySmall)
            if (source.changes.isNotBlank()) Text(source.changes, style = MaterialTheme.typography.bodySmall)
            TextButton(onClick = { open(source.sourceUrl) }) { Text(stringResource(R.string.dictionary_source_link)) }
            TextButton(onClick = { open(source.licenseUrl) }) { Text(stringResource(R.string.dictionary_license_link, source.license)) }
        }
        if (linkError) Text(stringResource(R.string.dictionary_link_error))
    }
}

@Composable
private fun DictionaryStatus(phase: DictionaryPhase, retry: () -> Unit) {
    DictionaryPanel {
        if (phase == DictionaryPhase.Loading) CircularProgressIndicator()
        Text(stringResource(when (phase) {
            DictionaryPhase.Empty -> R.string.dictionary_initial
            DictionaryPhase.Typing -> R.string.dictionary_typing
            DictionaryPhase.Loading -> R.string.dictionary_loading
            DictionaryPhase.NoResults -> R.string.dictionary_empty
            DictionaryPhase.Invalid -> R.string.dictionary_invalid
            DictionaryPhase.Expired -> R.string.dictionary_expired
            DictionaryPhase.NotFound -> R.string.dictionary_not_found
            else -> R.string.dictionary_error
        }))
        if (phase == DictionaryPhase.Error) Button(onClick = retry) { Text(stringResource(R.string.dictionary_retry)) }
    }
}
