package com.example.chineselearningapp.feature.dictionary

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.text.selection.SelectionContainer
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.TextFieldValue
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.example.chineselearningapp.R
import com.example.chineselearningapp.core.designsystem.*
import com.example.chineselearningapp.domain.model.*
import com.example.chineselearningapp.feature.dictionary.handwriting.*

@Composable
fun DictionarySearchScreen(
    state: DictionarySearchState,
    edit: (String, Boolean) -> Unit,
    retry: () -> Unit,
    loadMore: () -> Unit,
    open: (String) -> Unit,
    back: () -> Unit,
    handwriting: HandwritingViewModel? = null
) {
    var field by rememberSaveable(stateSaver = TextFieldValue.Saver) { mutableStateOf(TextFieldValue(state.query)) }
    val keyboard = LocalSoftwareKeyboardController.current
    val focus = LocalFocusManager.current
    val inkState = handwriting?.state?.collectAsStateWithLifecycle()?.value ?: HandwritingState()

    // Ensure handwriting recognizer is open for the drawing canvas
    LaunchedEffect(handwriting) {
        if (handwriting != null && inkState.phase == HandwritingPhase.Closed) {
            handwriting.open()
        }
    }

    val context = LocalContext.current
    DisposableEffect(handwriting, context) {
        onDispose {
            var owner = context
            while (owner is android.content.ContextWrapper && owner !is android.app.Activity) owner = owner.baseContext
            if ((owner as? android.app.Activity)?.isChangingConfigurations != true) handwriting?.close()
        }
    }

    val canDraw = handwriting != null && inkState.phase !in setOf(
        HandwritingPhase.Preparing,
        HandwritingPhase.Downloading,
        HandwritingPhase.ModelError
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Surface0)
            .statusBarsPadding()
            .imePadding()
    ) {
        // 1. Back button "← Quay lại" (Primary) + title "Tra từ điển"
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = SpaceLG, vertical = SpaceMD),
            verticalAlignment = Alignment.CenterVertically
        ) {
            TextButton(
                onClick = back,
                contentPadding = PaddingValues(0.dp)
            ) {
                Text(
                    text = "← Quay lại",
                    color = Primary,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Medium
                )
            }
            Spacer(Modifier.width(SpaceMD))
            Text(
                text = "Tra từ điển",
                style = FontTitle,
                color = TextPrimary
            )
        }

        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = SpaceLG),
            contentPadding = PaddingValues(bottom = Space2XL),
            verticalArrangement = Arrangement.spacedBy(SpaceXL)
        ) {
            // 2. SearchBar (Surface1 bg, border-radius 12dp, padding 10dp 14dp)
            item(key = "search_bar") {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(RadiusMedium))
                        .background(Surface1)
                        .border(1.dp, Border, RoundedCornerShape(RadiusMedium))
                        .padding(horizontal = 14.dp, vertical = 10.dp)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(SpaceSM)
                    ) {
                        Icon(
                            painter = painterResource(R.drawable.ic_handwriting),
                            contentDescription = "Search",
                            tint = TextMuted,
                            modifier = Modifier.size(20.dp)
                        )
                        Box(modifier = Modifier.weight(1f)) {
                            if (field.text.isEmpty()) {
                                Text(
                                    text = "Nhập hoặc vẽ chữ Hán...",
                                    style = FontBody.copy(color = TextMuted)
                                )
                            }
                            BasicTextField(
                                value = field,
                                onValueChange = { next ->
                                    field = next
                                    edit(next.text, next.composition != null)
                                },
                                textStyle = FontBody.copy(color = TextPrimary, fontSize = 16.sp),
                                cursorBrush = SolidColor(Primary),
                                singleLine = true,
                                keyboardOptions = KeyboardOptions(imeAction = ImeAction.Search),
                                keyboardActions = KeyboardActions(onSearch = {
                                    keyboard?.hide()
                                    focus.clearFocus()
                                    edit(field.text, false)
                                }),
                                modifier = Modifier.fillMaxWidth()
                            )
                        }
                        if (field.text.isNotEmpty()) {
                            Text(
                                text = "✕",
                                color = TextMuted,
                                fontSize = 14.sp,
                                modifier = Modifier
                                    .clickable {
                                        field = TextFieldValue("")
                                        edit("", false)
                                    }
                                    .padding(SpaceXS)
                            )
                        }
                    }
                }
            }

            // 3. SectionLabel "VẼ CHỮ" & 4. CanvasArea
            if (handwriting != null) {
                item(key = "canvas_section") {
                    Column(verticalArrangement = Arrangement.spacedBy(SpaceMD)) {
                        SectionLabel("VẼ CHỮ")
                        CanvasArea(
                            strokes = inkState.strokes,
                            enabled = canDraw,
                            onBeginStroke = handwriting::beginStroke,
                            onCompleteStroke = { stroke ->
                                handwriting.endStroke(stroke)
                                if (stroke != null) {
                                    handwriting.recognize()
                                }
                            },
                            onUndo = handwriting::undo,
                            onClear = handwriting::clear,
                            undoEnabled = inkState.strokes.isNotEmpty() && !inkState.drawing,
                            clearEnabled = inkState.strokes.isNotEmpty() && !inkState.drawing
                        )
                    }
                }

                // 5. SectionLabel "GỢI Ý KẾT QUẢ" & 6. ChipRow
                if (inkState.candidates.isNotEmpty()) {
                    item(key = "chips_section") {
                        Column(verticalArrangement = Arrangement.spacedBy(SpaceMD)) {
                            SectionLabel("GỢI Ý KẾT QUẢ")
                            ChipRow(
                                candidates = inkState.candidates,
                                selected = if (field.text in inkState.candidates) field.text else null,
                                onSelect = { candidate ->
                                    field = insertHandwriting(field, candidate)
                                    edit(field.text, false)
                                }
                            )
                        }
                    }
                }
            }

            // 7. PrimaryButton "Tra từ điển →"
            item(key = "search_button") {
                PrimaryButton(
                    text = "Tra từ điển →",
                    onClick = {
                        keyboard?.hide()
                        focus.clearFocus()
                        if (handwriting != null && inkState.canRecognize) {
                            handwriting.recognize()
                        }
                        edit(field.text, false)
                    },
                    enabled = field.text.isNotBlank() || (handwriting != null && inkState.strokes.isNotEmpty())
                )
            }

            // Search results or status
            if (state.phase != DictionaryPhase.Results && state.phase != DictionaryPhase.Empty) {
                item(key = "status") {
                    DictionaryStatus(state.phase, retry)
                }
            }

            if (state.phase == DictionaryPhase.Results) {
                items(state.items, key = { it.entryId }) { suggestion ->
                    Surface(
                        onClick = {
                            keyboard?.hide()
                            focus.clearFocus()
                            open(suggestion.entryId)
                        },
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(RadiusLarge),
                        color = Surface1,
                        border = BorderStroke(1.dp, Border)
                    ) {
                        Column(
                            modifier = Modifier.padding(SpaceLG),
                            verticalArrangement = Arrangement.spacedBy(SpaceXS)
                        ) {
                            Text(
                                text = suggestion.simplified,
                                fontSize = 20.sp,
                                fontWeight = FontWeight.Medium,
                                color = TextPrimary
                            )
                            Text(
                                text = suggestion.pinyin,
                                fontSize = 14.sp,
                                fontWeight = FontWeight.Medium,
                                color = Primary
                            )
                            suggestion.shortVietnameseMeaning?.takeIf { it.isNotBlank() }?.let {
                                Text(
                                    text = it,
                                    style = FontBody.copy(color = TextSecondary, fontSize = 14.sp)
                                )
                            }
                        }
                    }
                }

                if (state.nextOffset != null) {
                    item(key = "more") {
                        if (state.pageError) {
                            Text(
                                text = stringResource(R.string.dictionary_error),
                                style = FontCaption.copy(color = Color(0xFFA32D2D))
                            )
                        }
                        SecondaryButton(
                            text = stringResource(if (state.pageError) R.string.dictionary_retry else R.string.dictionary_more),
                            onClick = loadMore,
                            enabled = !state.loadingMore
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun DictionaryDetailScreen(
    state: DictionaryDetailState,
    retry: () -> Unit,
    back: () -> Unit,
    savedAction: @Composable () -> Unit = {}
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Surface0)
            .statusBarsPadding()
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = SpaceLG, vertical = SpaceMD),
            verticalAlignment = Alignment.CenterVertically
        ) {
            TextButton(
                onClick = back,
                contentPadding = PaddingValues(0.dp)
            ) {
                Text(
                    text = "← Quay lại",
                    color = Primary,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Medium
                )
            }
            Spacer(Modifier.width(SpaceMD))
            Text(
                text = stringResource(R.string.dictionary_title),
                style = FontTitle,
                color = TextPrimary
            )
        }

        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = SpaceLG),
            contentPadding = PaddingValues(bottom = Space2XL),
            verticalArrangement = Arrangement.spacedBy(SpaceXL)
        ) {
            val entry = state.entry
            if (entry == null) {
                item { DictionaryStatus(state.phase, retry) }
            } else {
                item {
                    DictionaryPanel {
                        SelectionContainer {
                            Column(verticalArrangement = Arrangement.spacedBy(SpaceMD)) {
                                Text(
                                    text = entry.suggestion.simplified,
                                    fontSize = 36.sp,
                                    fontWeight = FontWeight.Medium,
                                    color = TextPrimary
                                )
                                Text(
                                    text = entry.citationPinyin,
                                    fontSize = 18.sp,
                                    fontWeight = FontWeight.Medium,
                                    color = Primary
                                )
                                entry.sinoVietnamese?.takeIf { it.isNotBlank() }?.let {
                                    Text(
                                        text = stringResource(R.string.dictionary_sino, it),
                                        style = FontBody.copy(color = TextSecondary)
                                    )
                                }
                            }
                        }
                    }
                }

                item { savedAction() }

                if (!entry.active) {
                    item {
                        Text(
                            text = stringResource(R.string.wordbook_inactive),
                            style = FontCaption.copy(color = TextMuted)
                        )
                    }
                }

                entry.meaningGroups.forEach { group ->
                    item(key = "meanings-" + group.key) {
                        DictionaryPanel {
                            SectionLabel(meaningLabel(group.key))
                            SelectionContainer {
                                Column(verticalArrangement = Arrangement.spacedBy(SpaceSM)) {
                                    group.value.forEach { sense ->
                                        Text(
                                            text = "${sense.number}. ${sense.gloss}",
                                            style = FontBody.copy(color = TextPrimary)
                                        )
                                    }
                                }
                            }
                        }
                    }
                }

                item {
                    Text(
                        text = stringResource(
                            if (entry.reviewStatus == "LOCAL_CODEX_REVIEWED") R.string.curated_local_codex_source
                            else R.string.curated_content_source
                        ),
                        style = FontCaption.copy(color = TextMuted)
                    )
                }
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
private fun DictionaryPanel(content: @Composable ColumnScope.() -> Unit) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(RadiusLarge),
        color = Surface1,
        border = BorderStroke(1.dp, Border)
    ) {
        Column(
            modifier = Modifier.padding(SpaceLG),
            verticalArrangement = Arrangement.spacedBy(SpaceMD),
            content = content
        )
    }
}

@Composable
private fun DictionaryStatus(phase: DictionaryPhase, retry: () -> Unit) {
    DictionaryPanel {
        if (phase == DictionaryPhase.Loading) {
            AppProgressBar(progress = 0.5f)
        }
        Text(
            text = stringResource(when (phase) {
                DictionaryPhase.Empty -> R.string.dictionary_initial
                DictionaryPhase.Typing -> R.string.dictionary_typing
                DictionaryPhase.Loading -> R.string.dictionary_loading
                DictionaryPhase.NoResults -> R.string.dictionary_empty
                DictionaryPhase.Invalid -> R.string.dictionary_invalid
                DictionaryPhase.Expired -> R.string.dictionary_expired
                DictionaryPhase.NotFound -> R.string.dictionary_not_found
                else -> R.string.dictionary_error
            }),
            style = FontBody.copy(color = TextSecondary)
        )
        if (phase == DictionaryPhase.Error) {
            SecondaryButton(onClick = retry, text = stringResource(R.string.dictionary_retry))
        }
    }
}
