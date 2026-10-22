package com.example.chineselearningapp.feature.lesson

import android.graphics.ImageDecoder
import android.graphics.drawable.AnimatedImageDrawable
import android.media.MediaPlayer
import android.os.Build
import android.widget.ImageView
import androidx.activity.compose.BackHandler
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import com.example.chineselearningapp.R
import com.example.chineselearningapp.core.designsystem.*
import com.example.chineselearningapp.domain.model.*
import java.nio.ByteBuffer

@Composable
fun LessonPlayerScreen(state: LessonPlayerState, move: (Boolean) -> Unit, exit: () -> Unit,
    retry: () -> Unit, persist: () -> Unit, ink: (List<List<InkPoint>>) -> Unit, loadMedia: (String) -> Unit) {
    BackHandler { exit() }
    val owner = LocalLifecycleOwner.current
    val save by rememberUpdatedState(persist)
    DisposableEffect(owner) {
        val observer = LifecycleEventObserver { _, event -> if (event == Lifecycle.Event.ON_STOP) save() }
        owner.lifecycle.addObserver(observer)
        onDispose { owner.lifecycle.removeObserver(observer) }
    }
    PageColumn {
        TextButton(onClick = exit, enabled = !state.loading && !state.saving) { Text(stringResource(R.string.lesson_exit)) }
        Text(state.bundle?.title?.takeIf { it.isNotBlank() } ?: stringResource(R.string.lesson_title), style = MaterialTheme.typography.headlineMedium)
        Text(stringResource(R.string.lesson_preview_hint), style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant)
        if (state.loading || state.saving) LinearProgressIndicator(Modifier.fillMaxWidth())
        state.error?.let {
            ErrorBanner(it)
            TextButton(onClick = retry, enabled = !state.loading && !state.saving) { Text(stringResource(R.string.session_retry)) }
        }
        val bundle = state.bundle
        if (bundle != null) {
            if (bundle.scenes.isEmpty()) Text(stringResource(R.string.lesson_empty))
            else {
                Text(stringResource(R.string.lesson_progress, state.index + 1, bundle.scenes.size))
                LinearProgressIndicator(progress = { (state.index + 1f) / bundle.scenes.size }, modifier = Modifier.fillMaxWidth())
                Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface), shape = MaterialTheme.shapes.large) {
                    Column(Modifier.fillMaxWidth().padding(24.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {
                        key(state.scene?.key, state.page) { SceneBody(state, ink, loadMedia) }
                    }
                }
                if (state.pageCount > 1) Text(stringResource(R.string.lesson_page, state.page + 1, state.pageCount))
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    OutlinedButton(onClick = { move(false) }, modifier = Modifier.weight(1f).heightIn(min = 52.dp),
                        enabled = !state.saving && (state.index > 0 || state.page > 0)) { Text(stringResource(R.string.lesson_previous)) }
                    val last = state.index == bundle.scenes.lastIndex && state.page == state.pageCount - 1
                    Button(onClick = { if (last) exit() else move(true) }, modifier = Modifier.weight(1f).heightIn(min = 52.dp),
                        enabled = !state.saving) { Text(stringResource(if (last) R.string.lesson_save_exit else R.string.lesson_next)) }
                }
            }
        }
    }
}

@Composable
private fun SceneBody(state: LessonPlayerState, ink: (List<List<InkPoint>>) -> Unit, loadMedia: (String) -> Unit) {
    when (val content = state.scene?.content) {
        is SceneContent.Introduction -> {
            Text(stringResource(R.string.lesson_introduction), style = MaterialTheme.typography.titleLarge)
            Text(content.word.hanzi ?: stringResource(R.string.lesson_missing), fontSize = 80.sp)
            Field(R.string.lesson_pinyin, content.word.pinyin)
            Field(R.string.lesson_reading, content.word.reading)
            if (content.showMeaning) Field(R.string.lesson_meaning, content.word.meaning)
            content.word.audioId?.let { AssetMedia(it, true, state, loadMedia) }
        }
        is SceneContent.Information -> {
            Text(stringResource(R.string.lesson_information), style = MaterialTheme.typography.titleLarge)
            Text(content.word.hanzi ?: stringResource(R.string.lesson_missing), style = MaterialTheme.typography.displayMedium)
            if ("PINYIN" in content.fields) Field(R.string.lesson_pinyin, content.word.pinyin)
            if ("SINO_VIETNAMESE" in content.fields) Field(R.string.lesson_reading, content.word.reading)
            if ("MEANING" in content.fields) Field(R.string.lesson_meaning, content.word.meaning)
            if ("POS" in content.fields) Field(R.string.lesson_pos, content.word.partOfSpeech)
            if ("NOTES" in content.fields) Field(R.string.lesson_notes, content.word.notes)
        }
        is SceneContent.Analysis -> {
            Text(stringResource(R.string.lesson_analysis), style = MaterialTheme.typography.titleLarge)
            val page = content.characters.getOrNull(state.page)
            Text(page?.hanzi ?: stringResource(R.string.lesson_missing), fontSize = 72.sp)
            page?.strokeCount?.let { Text(stringResource(R.string.lesson_stroke_count, it)) }
            if (page?.components.isNullOrEmpty()) Text(stringResource(R.string.lesson_analysis_missing))
            else page?.components?.forEach { Text(it) }
        }
        is SceneContent.Stroke -> {
            Text(stringResource(R.string.lesson_stroke), style = MaterialTheme.typography.titleLarge)
            val page = content.characters.getOrNull(state.page)
            Text(page?.hanzi ?: stringResource(R.string.lesson_missing), fontSize = 72.sp)
            if (page?.strokeAssetId == null) Text(stringResource(R.string.lesson_stroke_missing))
            else AssetMedia(page.strokeAssetId, false, state, loadMedia)
        }
        is SceneContent.Handwriting -> {
            Text(stringResource(R.string.lesson_handwriting), style = MaterialTheme.typography.titleLarge)
            Text(content.hanzi ?: stringResource(R.string.lesson_missing), fontSize = 56.sp)
            Text(stringResource(R.string.lesson_handwriting_hint))
            HandwritingCanvas(state.ink[state.scene?.key].orEmpty(), ink)
            TextButton(onClick = { ink(emptyList()) }) { Text(stringResource(R.string.lesson_clear)) }
        }
        else -> Text(stringResource(R.string.lesson_unsupported))
    }
}

@Composable
private fun Field(label: Int, value: String?) {
    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
        Text(stringResource(label), style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.primary)
        Text(value ?: stringResource(R.string.lesson_missing), style = MaterialTheme.typography.bodyLarge)
    }
}

@Composable
private fun HandwritingCanvas(strokes: List<List<InkPoint>>, changed: (List<List<InkPoint>>) -> Unit) {
    val latest by rememberUpdatedState(strokes)
    val change by rememberUpdatedState(changed)
    val color = MaterialTheme.colorScheme.onSurface
    val guide = MaterialTheme.colorScheme.outlineVariant
    Canvas(Modifier.fillMaxWidth().aspectRatio(1f).background(MaterialTheme.colorScheme.surfaceVariant, MaterialTheme.shapes.medium)
        .pointerInput(Unit) {
            var working = latest
            detectDragGestures(onDragStart = { point ->
                working = latest + listOf(listOf(InkPoint((point.x / size.width).coerceIn(0f, 1f), (point.y / size.height).coerceIn(0f, 1f))))
                change(working)
            }, onDrag = { event, _ ->
                event.consume()
                if (working.isNotEmpty()) {
                    working = working.dropLast(1) + listOf(working.last() + InkPoint(
                        (event.position.x / size.width).coerceIn(0f, 1f), (event.position.y / size.height).coerceIn(0f, 1f)))
                    change(working)
                }
            })
        }) {
        drawLine(guide, Offset(size.width / 2, 0f), Offset(size.width / 2, size.height))
        drawLine(guide, Offset(0f, size.height / 2), Offset(size.width, size.height / 2))
        strokes.forEach { stroke ->
            if (stroke.size == 1) drawCircle(color, 2.5.dp.toPx(), Offset(stroke[0].x * size.width, stroke[0].y * size.height))
            stroke.zipWithNext().forEach { (a, b) -> drawLine(color, Offset(a.x * size.width, a.y * size.height),
                Offset(b.x * size.width, b.y * size.height), strokeWidth = 5.dp.toPx(), cap = StrokeCap.Round) }
        }
    }
}

@Composable
private fun AssetMedia(id: String, audio: Boolean, state: LessonPlayerState, load: (String) -> Unit) {
    LaunchedEffect(id) { load(id) }
    val bytes = state.media[id]
    if (id in state.mediaErrors) Text(stringResource(R.string.lesson_media_error))
    else if (bytes == null) CircularProgressIndicator(Modifier.size(24.dp))
    else if (audio) AudioButton(bytes)
    else {
        var failed by remember(id) { mutableStateOf(false) }
        if (failed) Text(stringResource(R.string.lesson_media_error))
        else AndroidView(modifier = Modifier.fillMaxWidth().height(240.dp), factory = { context ->
            ImageView(context).apply {
                scaleType = ImageView.ScaleType.FIT_CENTER
                runCatching {
                    if (Build.VERSION.SDK_INT >= 28) {
                        val drawable = ImageDecoder.decodeDrawable(ImageDecoder.createSource(ByteBuffer.wrap(bytes)))
                        setImageDrawable(drawable)
                        if (drawable is AnimatedImageDrawable) drawable.start()
                    } else {
                        val bitmap = android.graphics.BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
                        requireNotNull(bitmap)
                        setImageBitmap(bitmap)
                    }
                }.onFailure { failed = true }
            }
        }, onRelease = { view -> if (Build.VERSION.SDK_INT >= 28) (view.drawable as? AnimatedImageDrawable)?.stop() })
    }
}

@Composable
private fun AudioButton(bytes: ByteArray) {
    val context = LocalContext.current
    var player by remember { mutableStateOf<MediaPlayer?>(null) }
    var failed by remember { mutableStateOf(false) }
    DisposableEffect(bytes) { onDispose { player?.release(); player = null } }
    if (failed) Text(stringResource(R.string.lesson_media_error))
    Button(onClick = {
        player?.release()
        val file = java.io.File.createTempFile("lesson-audio", ".media", context.cacheDir)
        try {
            file.writeBytes(bytes)
            val media = MediaPlayer()
            player = media
            media.setDataSource(file.path)
            media.setOnPreparedListener { file.delete(); it.start() }
            media.setOnCompletionListener { it.release(); player = null }
            media.setOnErrorListener { mediaPlayer, _, _ -> file.delete(); mediaPlayer.release(); player = null; failed = true; true }
            media.prepareAsync()
        } catch (_: Exception) { file.delete(); player?.release(); player = null; failed = true }
    }) { Text(stringResource(R.string.lesson_play_audio)) }
}
