package com.example.chineselearningapp.feature.dictionary.handwriting

import com.google.android.gms.tasks.Task
import com.google.mlkit.common.model.DownloadConditions
import com.google.mlkit.common.model.RemoteModelManager
import com.google.mlkit.vision.digitalink.recognition.*
import javax.inject.Inject
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.withContext
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

/** One instance per dictionary back-stack entry, retained across rotation and closed by its VM. */
class MlKitHandwritingRecognizer @Inject constructor() : HandwritingRecognizer {
    private val model by lazy {
        val identifier = checkNotNull(DigitalInkRecognitionModelIdentifier.fromLanguageTag("zh-Hani-CN"))
        DigitalInkRecognitionModel.builder(identifier).build()
    }
    private val manager by lazy { RemoteModelManager.getInstance() }
    private var download: Task<Void>? = null
    private var client: DigitalInkRecognizer? = null
    private var closed = false
    private var activeTasks = 0

    override suspend fun prepareModel(onDownload: () -> Unit) {
        if (!manager.isModelDownloaded(model).awaitResult()) {
            onDownload()
            val task = synchronized(this) {
                download?.takeUnless { it.isComplete } ?: manager.download(model,
                    DownloadConditions.Builder().build()).also { download = it }
            }
            task.awaitResult()
        }
        synchronized(this) {
            check(!closed)
            if (client == null) client = DigitalInkRecognition.getClient(DigitalInkRecognizerOptions.builder(model).build())
        }
    }

    override suspend fun recognize(strokes: List<HandwritingStroke>): List<String> = withContext(Dispatchers.Default) {
        require(strokes.isNotEmpty() && strokes.all { it.isValid })
        val ink = Ink.builder().apply {
            strokes.forEach { stroke ->
                addStroke(Ink.Stroke.builder().apply {
                    stroke.points.forEach { addPoint(Ink.Point.create(it.x, it.y, it.timeMillis)) }
                }.build())
            }
        }.build()
        val task = synchronized(this@MlKitHandwritingRecognizer) {
            check(!closed)
            checkNotNull(client).recognize(ink).also { activeTasks++ }
        }
        // ML Kit Tasks cannot be cancelled. Release only after native inference actually finishes.
        task.addOnCompleteListener {
            synchronized(this@MlKitHandwritingRecognizer) {
                activeTasks--
                if (closed && activeTasks == 0) { client?.close(); client = null }
            }
        }
        task.awaitResult().candidates.map { it.text }
    }

    override fun close() = synchronized(this) {
        closed = true
        if (activeTasks == 0) { client?.close(); client = null }
    }
}

private suspend fun <T> Task<T>.awaitResult(): T = suspendCancellableCoroutine { continuation ->
    addOnSuccessListener { if (continuation.isActive) continuation.resume(it) }
    addOnFailureListener { if (continuation.isActive) continuation.resumeWithException(it) }
    addOnCanceledListener { continuation.cancel() }
}
