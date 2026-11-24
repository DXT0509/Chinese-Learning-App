package com.example.chineselearningapp.feature.roadmap

import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.rememberScrollState
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.example.chineselearningapp.R
import com.example.chineselearningapp.core.designsystem.TextSecondary
import com.example.chineselearningapp.core.designsystem.TigerCanvas
import com.example.chineselearningapp.domain.model.*
import kotlinx.coroutines.flow.distinctUntilChanged

@Composable
fun VocabularyRoadmapScreen(state: RoadmapState, model: RoadmapViewModel, back: () -> Unit = {}) {
    if (state.lesson != null) {
        if (state.lesson.type == "REVIEW") {
            val session = remember(state.lesson.nodeVersionId) { state.lesson.toReviewSession() }
            ReviewSessionFlow(
                session = session,
                recognizer = model.handwritingRecognizer,
                onBack = { model.leave() },
                onFinish = {
                    if (state.ready && state.completion == null) {
                        model.complete()
                    }
                    model.continuePath()
                }
            )
        } else {
            RoadmapLessonFlow(state, model)
        }
        return
    }
    val list = rememberLazyListState(model.scrollIndex, model.scrollOffset)
    var locked by remember { mutableStateOf(false) }
    val snackbar = remember { SnackbarHostState() }
    val lockedText = stringResource(R.string.roadmap_locked_hint)

    LaunchedEffect(locked) {
        if (locked) {
            snackbar.showSnackbar(lockedText)
            locked = false
        }
    }
    LaunchedEffect(state.scrollTarget, state.nodes) {
        val target = state.scrollTarget ?: return@LaunchedEffect
        val index = state.nodes.indexOfFirst { it.position == target }
        if (index >= 0) {
            list.scrollToItem(index + 1)
            model.scrolled(target)
        }
    }
    LaunchedEffect(list) {
        snapshotFlow { list.firstVisibleItemIndex to list.firstVisibleItemScrollOffset }
            .distinctUntilChanged()
            .collect { (index, offset) ->
                model.saveScroll(index, offset)
            }
    }
    LaunchedEffect(list, state.next, state.busy) {
        snapshotFlow { list.layoutInfo.visibleItemsInfo.lastOrNull()?.index ?: 0 }
            .distinctUntilChanged()
            .collect { index ->
                if (!state.busy && state.next != null && index >= state.nodes.size - 4) {
                    model.more()
                }
            }
    }

    Box(Modifier.fillMaxSize()) {
        // Floating sparkles and background gradient
        FloatingSparklesBackground(Modifier.fillMaxSize())

        Column(Modifier.fillMaxSize()) {
            // App Bar Row
            Row(
                Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 4.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                TextButton(onClick = back) {
                    Text(stringResource(R.string.screen_back))
                }
                Text(
                    text = state.selected?.title ?: stringResource(R.string.roadmap),
                    modifier = Modifier.weight(1f),
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Medium
                )
                TextButton(
                    onClick = { model.jump() },
                    enabled = state.current != null && !state.busy
                ) {
                    Text(stringResource(R.string.roadmap_current))
                }
            }

            // Catalog switcher chips
            if (state.catalog.size > 1 || state.catalogNext != null) {
                Row(
                    Modifier
                        .horizontalScroll(rememberScrollState())
                        .padding(horizontal = 16.dp, vertical = 2.dp)
                ) {
                    state.catalog.forEach { roadmap ->
                        FilterChip(
                            selected = roadmap == state.selected,
                            onClick = { model.select(roadmap) },
                            enabled = !state.busy,
                            label = { Text(roadmap.title) }
                        )
                        Spacer(Modifier.width(8.dp))
                    }
                    if (state.catalogNext != null) {
                        TextButton(onClick = model::moreCatalog, enabled = !state.busy) {
                            Text(stringResource(R.string.roadmap_more))
                        }
                    }
                }
            }

            // Section buttons
            if (state.sections.size > 1) {
                Row(
                    Modifier
                        .horizontalScroll(rememberScrollState())
                        .padding(horizontal = 16.dp, vertical = 2.dp)
                ) {
                    state.sections.toList().sortedBy { it.second }.forEach { (section, position) ->
                        TextButton(onClick = { model.jump(position) }, enabled = !state.busy) {
                            Text(section)
                        }
                    }
                }
            }

            RoadmapError(state.error, model::retry)
            if (state.loading || state.opening) LinearProgressIndicator(Modifier.fillMaxWidth())

            if (!state.loading && state.catalog.isEmpty() && state.error == null) {
                RoadmapEmpty()
            } else {
                val mascotPosition = remember(state.current, state.nodes) {
                    if (state.nodes.any { it.position == state.current }) {
                        state.current
                    } else {
                        state.nodes.firstOrNull()?.position
                    }
                }
                LazyColumn(
                    state = list,
                    modifier = Modifier.weight(1f),
                    contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp)
                ) {
                    item(key = "earlier") {
                        if ((state.nodes.firstOrNull()?.position ?: 0) > 0) {
                            Box(Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
                                TextButton(
                                    onClick = {
                                        model.jump((state.nodes.first().position - 45).coerceAtLeast(0))
                                    },
                                    enabled = !state.busy
                                ) {
                                    Text(stringResource(R.string.roadmap_earlier))
                                }
                            }
                        }
                    }
                    itemsIndexed(state.nodes, key = { _, node -> node.versionId }) { index, node ->
                        val prev = state.nodes.getOrNull(index - 1)
                        val next = state.nodes.getOrNull(index + 1)
                        RoadmapPathNode(
                            node = node,
                            index = index,
                            previousNode = prev,
                            nextNode = next,
                            current = node.position == state.current,
                            currentPosition = state.current,
                            enabled = !state.busy,
                            showMascot = node.position == mascotPosition
                        ) {
                            if (node.canOpen) model.open(node) else locked = true
                        }
                    }
                    item(key = "more") {
                        if (state.next != null) {
                            Box(Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
                                TextButton(onClick = model::more, enabled = !state.busy) {
                                    Text(stringResource(R.string.roadmap_more))
                                }
                            }
                        }
                        if (state.busy) LinearProgressIndicator(Modifier.fillMaxWidth())
                    }
                }
            }
        }
        SnackbarHost(snackbar, Modifier.align(Alignment.BottomCenter))
    }
}

@Composable
fun RoadmapEmpty() {
    Column(
        Modifier
            .fillMaxWidth()
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        TigerCanvas(Modifier.size(72.dp, 88.dp))
        Text(
            text = stringResource(R.string.roadmap_empty),
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Medium
        )
        Text(
            text = stringResource(R.string.roadmap_empty_detail),
            style = MaterialTheme.typography.bodyMedium,
            color = TextSecondary
        )
    }
}

@Composable
internal fun RoadmapError(error: Int?, retry: () -> Unit) {
    if (error != null) Row(
        Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = stringResource(error),
            modifier = Modifier.weight(1f),
            color = MaterialTheme.colorScheme.error
        )
        TextButton(onClick = retry) {
            Text(stringResource(R.string.retry))
        }
    }
}
