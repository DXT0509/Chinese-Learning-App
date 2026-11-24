package com.example.chineselearningapp.feature.roadmap

import android.graphics.ImageDecoder
import android.graphics.Movie
import android.graphics.drawable.Animatable
import android.graphics.drawable.Drawable
import android.media.MediaDataSource
import android.media.MediaPlayer
import android.os.Build
import android.view.View
import android.widget.ImageView
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.compose.LifecycleEventEffect
import com.example.chineselearningapp.R
import com.example.chineselearningapp.domain.model.*
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.nio.ByteBuffer

@Composable
internal fun RoadmapAudio(enrichment: LessonEnrichment, load: suspend (String) -> RoadmapMedia) {
    var bytes by remember(enrichment.assetId) { mutableStateOf<ByteArray?>(null) }
    var player by remember { mutableStateOf<MediaPlayer?>(null) }
    var busy by remember { mutableStateOf(false) }
    var failed by remember { mutableStateOf(false) }
    var loadJob by remember { mutableStateOf<kotlinx.coroutines.Job?>(null) }
    val scope = rememberCoroutineScope()
    fun release() { player?.release(); player = null; busy = false }
    DisposableEffect(enrichment.assetId) { onDispose { loadJob?.cancel(); release() } }
    LifecycleEventEffect(Lifecycle.Event.ON_STOP) { loadJob?.cancel(); release() }
    if (!enrichment.available || enrichment.assetId == null) {
        Text(stringResource(R.string.roadmap_no_audio), style = MaterialTheme.typography.labelMedium)
        return
    }
    OutlinedButton(onClick = {
        if (busy) { loadJob?.cancel(); release() } else {
            busy = true; failed = false
            loadJob = scope.launch {
                try {
                    val audio = bytes ?: load(enrichment.assetId).also { require(it.mediaType.startsWith("audio/")) }.bytes.also { bytes = it }
                    val media = MediaPlayer()
                    player = media
                    media.setDataSource(ByteArraySource(audio))
                    media.setOnPreparedListener { it.start() }
                    media.setOnCompletionListener { release() }
                    media.setOnErrorListener { _, _, _ -> release(); failed = true; true }
                    media.prepareAsync()
                } catch (cancelled: CancellationException) { release(); throw cancelled }
                catch (_: Exception) { release(); failed = true }
            }
        }
    }) { Text(stringResource(if (busy) R.string.roadmap_stop_audio else R.string.roadmap_listen)) }
    if (failed) Text(stringResource(R.string.roadmap_media_error), color = MaterialTheme.colorScheme.error)
}

private class ByteArraySource(private val bytes: ByteArray) : MediaDataSource() {
    override fun getSize() = bytes.size.toLong()
    override fun readAt(position: Long, buffer: ByteArray, offset: Int, size: Int): Int {
        if (position >= bytes.size) return -1
        val count = minOf(size, bytes.size - position.toInt())
        bytes.copyInto(buffer, offset, position.toInt(), position.toInt() + count)
        return count
    }
    override fun close() = Unit
}

@Composable
internal fun ReviewedEnrichment(enrichment: LessonEnrichment, load: suspend (String) -> RoadmapMedia) {
    if (!enrichment.available) return
    enrichment.text?.let { Text(it) }
    if (enrichment.assetId != null) ReviewedAsset(enrichment, load)
}

private data class DecodedAsset(val drawable: Drawable? = null, val movie: Movie? = null, val text: String? = null)

@Suppress("DEPRECATION")
@Composable
internal fun ReviewedAsset(enrichment: LessonEnrichment, load: suspend (String) -> RoadmapMedia,
    animationControls: Boolean = false, onRendered: (Boolean) -> Unit = {},
    imageModifier: Modifier = Modifier.fillMaxWidth().height(240.dp),
    showPlaybackControls: Boolean = true, replayRequest: Int = 0) {
    val context = LocalContext.current
    var decoded by remember(enrichment.assetId) { mutableStateOf<DecodedAsset?>(null) }
    var failed by remember(enrichment.assetId) { mutableStateOf(false) }
    var retry by remember { mutableIntStateOf(0) }
    var playing by remember { mutableStateOf(true) }
    var epoch by remember { mutableIntStateOf(0) }
    val currentRendered by rememberUpdatedState(onRendered)
    LaunchedEffect(replayRequest) {
        if (replayRequest > 0) {
            (decoded?.drawable as? Animatable)?.stop()
            epoch++; playing = true
        }
    }
    LaunchedEffect(enrichment.assetId, retry) {
        currentRendered(false)
        val id = enrichment.assetId ?: run { failed = true; return@LaunchedEffect }
        try {
            val media = load(id)
            decoded = withContext(Dispatchers.Default) {
                when {
                    media.mediaType.substringBefore(';') == "image/gif" -> {
                        val movie = Movie.decodeByteArray(media.bytes, 0, media.bytes.size)
                        require(movie != null); DecodedAsset(movie = movie)
                    }
                    media.mediaType.startsWith("image/") && Build.VERSION.SDK_INT >= 28 -> DecodedAsset(
                        drawable = ImageDecoder.decodeDrawable(ImageDecoder.createSource(ByteBuffer.wrap(media.bytes))))
                    media.mediaType.substringBefore(';') in setOf("image/png", "image/jpeg") -> DecodedAsset(
                        drawable = android.graphics.drawable.BitmapDrawable(context.resources,
                            checkNotNull(android.graphics.BitmapFactory.decodeByteArray(media.bytes, 0, media.bytes.size))))
                    !animationControls && media.mediaType.startsWith("text/plain") -> DecodedAsset(text = media.bytes.toString(Charsets.UTF_8))
                    else -> error("Unsupported published asset")
                }
            }
            failed = false; currentRendered(true)
        } catch (cancelled: CancellationException) { throw cancelled }
        catch (_: Exception) { failed = true; currentRendered(false) }
    }
    LifecycleEventEffect(Lifecycle.Event.ON_STOP) { playing = false; (decoded?.drawable as? Animatable)?.stop() }
    DisposableEffect(decoded) { onDispose { (decoded?.drawable as? Animatable)?.stop() } }
    when {
        failed -> Row(verticalAlignment = androidx.compose.ui.Alignment.CenterVertically) {
            Text(stringResource(R.string.roadmap_media_error), Modifier.weight(1f))
            TextButton(onClick = { failed = false; retry++ }) { Text(stringResource(R.string.retry)) }
        }
        decoded == null -> LinearProgressIndicator(Modifier.fillMaxWidth())
        else -> {
            val asset = checkNotNull(decoded)
            asset.text?.let { Text(it) }
            asset.drawable?.let { drawable ->
                key(epoch) {
                    AndroidView(factory = { ImageView(it).apply { scaleType = ImageView.ScaleType.FIT_CENTER; setImageDrawable(drawable) } },
                        modifier = imageModifier, update = {
                            if (playing) (drawable as? Animatable)?.start() else (drawable as? Animatable)?.stop()
                        })
                }
            }
            asset.movie?.let { movie -> key(epoch) {
                AndroidView(factory = { MovieView(it, movie) }, modifier = imageModifier, update = { it.playing = playing; it.invalidate() })
            } }
            if (animationControls && showPlaybackControls) Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                TextButton(onClick = { playing = !playing }) { Text(stringResource(if (playing) R.string.roadmap_pause else R.string.roadmap_play)) }
                TextButton(onClick = { epoch++; playing = true; (asset.drawable as? Animatable)?.stop() }) { Text(stringResource(R.string.roadmap_replay)) }
            }
        }
    }
}

@Suppress("DEPRECATION")
private class MovieView(context: android.content.Context, private val movie: Movie) : View(context) {
    var playing = true
    private var elapsed = 0L
    private var last = 0L
    override fun onDraw(canvas: android.graphics.Canvas) {
        super.onDraw(canvas)
        val now = android.os.SystemClock.uptimeMillis()
        if (playing && last != 0L) elapsed += (now - last).coerceAtMost(100)
        last = now
        movie.setTime((elapsed % movie.duration().coerceAtLeast(1)).toInt())
        val scale = minOf(width.toFloat() / movie.width().coerceAtLeast(1), height.toFloat() / movie.height().coerceAtLeast(1))
        canvas.save(); canvas.translate((width - movie.width() * scale) / 2, 0f); canvas.scale(scale, scale)
        movie.draw(canvas, 0f, 0f); canvas.restore()
        if (playing) postInvalidateDelayed(32)
    }
}
