package com.example.chineselearningapp.feature.roadmap

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.os.SystemClock
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.compose.LifecycleEventEffect
import com.example.chineselearningapp.R
import com.example.chineselearningapp.core.designsystem.*

/** Owned by a screen lifecycle. It releases the system service on background/disposal. */
internal class LessonSpeechInput(private val context: Context) {
    private var engine: SpeechRecognizer? = null
    private var captureStarted = 0L
    private var captureEnded = 0L
    private var heardSpeech = false
    private var generation = 0
    fun cancel() { generation++; engine?.cancel(); engine?.destroy(); engine = null }

    fun start(recording: (Boolean) -> Unit, result: (List<String>, Int) -> Unit, failed: () -> Unit) {
        cancel()
        if (!SpeechRecognizer.isRecognitionAvailable(context)) { failed(); return }
        val token = generation
        captureStarted = 0; captureEnded = 0; heardSpeech = false
        var finished = false
        fun duration(): Int = if (!heardSpeech || captureStarted == 0L) 0 else
            ((captureEnded.takeIf { it > 0 } ?: SystemClock.elapsedRealtime()) - captureStarted).coerceIn(0, 300000).toInt()
        try {
            val recognizer = SpeechRecognizer.createSpeechRecognizer(context)
            engine = recognizer
            recognizer.setRecognitionListener(object : RecognitionListener {
                override fun onReadyForSpeech(params: Bundle?) { if (token == generation) { captureStarted = SystemClock.elapsedRealtime(); recording(true) } }
                override fun onBeginningOfSpeech() { if (token == generation) heardSpeech = true }
                override fun onEndOfSpeech() { if (token == generation) { captureEnded = SystemClock.elapsedRealtime(); recording(false) } }
                override fun onResults(results: Bundle?) {
                    if (token != generation || finished) return
                    finished = true
                    recording(false)
                    val candidates = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION).orEmpty()
                    if (candidates.isEmpty() || duration() < 1000) failed() else result(candidates, duration())
                }
                override fun onError(error: Int) {
                    if (token != generation || finished) return
                    finished = true
                    recording(false)
                    if (error == SpeechRecognizer.ERROR_NO_MATCH && duration() >= 1000) result(emptyList(), duration()) else failed()
                }
                override fun onRmsChanged(rmsdB: Float) = Unit
                override fun onBufferReceived(buffer: ByteArray?) = Unit
                override fun onPartialResults(partialResults: Bundle?) = Unit
                override fun onEvent(eventType: Int, params: Bundle?) = Unit
            })
            recognizer.startListening(Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                putExtra(RecognizerIntent.EXTRA_LANGUAGE, "zh-CN")
                putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 3)
            })
        } catch (_: Exception) { cancel(); recording(false); failed() }
    }
    fun stop() { engine?.stopListening() }
}

@Composable
internal fun SpeechPractice(
    target: String,
    state: LessonState,
    enabled: Boolean,
    result: (List<String>, Int) -> Unit,
    onSkip: (() -> Unit)? = null
) {
    val context = LocalContext.current
    val input = remember(context) { LessonSpeechInput(context) }
    val currentResult by rememberUpdatedState(result)
    var recording by remember { mutableStateOf(false) }
    var processing by remember { mutableStateOf(false) }
    var denied by remember { mutableStateOf(false) }
    var failed by remember { mutableStateOf(false) }
    val snackbar = remember { SnackbarHostState() }
    val tryAgainText = stringResource(R.string.lesson_flow_speech_try_again)

    fun start() {
        if (!enabled || processing || recording || state.feedback == true) return
        processing = true; failed = false; denied = false
        input.start({ recording = it }, { candidates, duration ->
            processing = false; recording = false; currentResult(candidates, duration)
        }, { failed = true; processing = false; recording = false })
    }
    val permission = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
        if (granted) start() else denied = true
    }
    LifecycleEventEffect(Lifecycle.Event.ON_STOP) { input.cancel(); recording = false; processing = false }
    DisposableEffect(input) { onDispose { input.cancel() } }
    LaunchedEffect(processing) {
        if (processing) {
            kotlinx.coroutines.delay(30000)
            input.cancel(); recording = false; processing = false; failed = true
        }
    }
    LaunchedEffect(state.speechAttempts, state.feedback) {
        if (state.feedback == false && state.speechAttempts > 0) {
            snackbar.showSnackbar(tryAgainText)
        }
    }
    Text(target, fontSize = 36.sp, color = TextPrimary)
    LessonListen(target)
    val microphoneLabel = stringResource(if (recording) R.string.roadmap_stop_recording else R.string.lesson_flow_mic)
    Box(Modifier.size(144.dp), contentAlignment = Alignment.Center) {
        if (recording) {
            val transition = rememberInfiniteTransition(label = "microphone")
            val pulse by transition.animateFloat(.85f, 1.15f,
                infiniteRepeatable(tween(650), RepeatMode.Reverse), label = "pulse")
            Box(Modifier.size(128.dp).scale(pulse).background(Primary.copy(alpha = .15f), CircleShape))
        }
        FilledIconButton(onClick = {
            if (recording) input.stop()
            else if (ContextCompat.checkSelfPermission(context, Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) start()
            else permission.launch(Manifest.permission.RECORD_AUDIO)
        }, enabled = enabled && (recording || !processing) && state.feedback != true,
            shape = CircleShape, modifier = Modifier.size(88.dp).semantics { contentDescription = microphoneLabel }) {
            Text(if (recording) "■" else "🎤", fontSize = 32.sp)
        }
    }
    Text(stringResource(if (recording) R.string.roadmap_stop_recording else if (processing)
        R.string.lesson_flow_speech_processing else R.string.lesson_flow_mic))
    val attemptDisplay = if (state.feedback == true) maxOf(1, state.speechAttempts) else state.speechAttempts + 1
    Text(stringResource(R.string.lesson_flow_speech_attempts, attemptDisplay), color = TextMuted)
    if (state.speechAttempts >= 3 && state.feedback != true) {
        Text(stringResource(R.string.lesson_flow_speech_skip_hint), style = FontLabel, color = TextMuted)
        if (onSkip != null) {
            SecondaryButton(
                text = stringResource(R.string.lesson_flow_speech_skip),
                onClick = onSkip,
                enabled = enabled && !processing && !recording
            )
        }
    }
    if (denied) Text(stringResource(R.string.roadmap_mic_denied), color = MaterialTheme.colorScheme.error)
    if (failed) Text(stringResource(R.string.lesson_flow_speech_unavailable), color = MaterialTheme.colorScheme.error)
    if (state.speechText.isNotBlank()) Text(state.speechText)
    LessonFeedback(state.feedback)
    Text(stringResource(R.string.lesson_flow_speech_notice), style = FontLabel, color = TextMuted)
    SnackbarHost(snackbar)
}

@Composable
internal fun SpeechPractice(
    target: String,
    state: LessonState,
    enabled: Boolean,
    result: (String, Int) -> Unit
) = SpeechPractice(
    target = target,
    state = state,
    enabled = enabled,
    result = { candidates, duration -> result(candidates.firstOrNull().orEmpty(), duration) },
    onSkip = null
)
