package com.example.chineselearningapp.feature.roadmap

import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import androidx.compose.runtime.*
import androidx.compose.ui.platform.LocalContext
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import java.util.Locale

internal data class WordSpeech(
    val ready: Boolean,
    val unavailable: Boolean,
    val isSpeaking: Boolean = false,
    val speak: () -> Unit,
    val speakWithRate: (Float) -> Unit = {},
    val stop: () -> Unit = {},
)

@Composable
internal fun rememberWordSpeech(hanzi: String, volume: Float = 1.0f): WordSpeech {
    val context = LocalContext.current.applicationContext
    val owner = LocalLifecycleOwner.current
    val currentHanzi by rememberUpdatedState(hanzi)
    val currentVolume by rememberUpdatedState(volume)
    var engine by remember { mutableStateOf<TextToSpeech?>(null) }
    var ready by remember { mutableStateOf(false) }
    var unavailable by remember { mutableStateOf(false) }
    var isSpeaking by remember { mutableStateOf(false) }
    DisposableEffect(context, owner) {
        var disposed = false
        val handler = Handler(Looper.getMainLooper())
        ready = false
        unavailable = false
        isSpeaking = false
        val speech = TextToSpeech(context) { status ->
            handler.post {
                if (!disposed) {
                    val language = if (status == TextToSpeech.SUCCESS) engine?.setLanguage(Locale.SIMPLIFIED_CHINESE) else null
                    ready = language != null && language >= TextToSpeech.LANG_AVAILABLE
                    unavailable = !ready
                }
            }
        }
        engine = speech
        speech.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
            override fun onStart(utteranceId: String?) {
                handler.post { if (!disposed) isSpeaking = true }
            }
            override fun onDone(utteranceId: String?) {
                handler.post { if (!disposed) isSpeaking = false }
            }
            @Deprecated("Required by the platform listener")
            override fun onError(utteranceId: String?) {
                handler.post {
                    if (!disposed) {
                        isSpeaking = false
                        unavailable = true
                    }
                }
            }
        })
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_STOP) {
                speech.stop()
                isSpeaking = false
            }
        }
        owner.lifecycle.addObserver(observer)
        onDispose {
            disposed = true
            owner.lifecycle.removeObserver(observer)
            handler.removeCallbacksAndMessages(null)
            speech.stop()
            speech.shutdown()
            engine = null
        }
    }
    val speakWithRate: (Float) -> Unit = { rate ->
        if (ready && owner.lifecycle.currentState.isAtLeast(Lifecycle.State.STARTED)) {
            val params = Bundle().apply {
                putFloat(TextToSpeech.Engine.KEY_PARAM_VOLUME, currentVolume.coerceIn(0f, 1f))
            }
            engine?.setSpeechRate(rate)
            val utteranceId = "word-speech-${System.currentTimeMillis()}"
            val res = engine?.speak(currentHanzi, TextToSpeech.QUEUE_FLUSH, params, utteranceId)
            if (res == TextToSpeech.SUCCESS) {
                isSpeaking = true
                unavailable = false
            } else {
                unavailable = true
                isSpeaking = false
            }
        }
    }
    return WordSpeech(
        ready = ready,
        unavailable = unavailable,
        isSpeaking = isSpeaking,
        speak = { speakWithRate(1.0f) },
        speakWithRate = speakWithRate,
        stop = {
            engine?.stop()
            isSpeaking = false
        }
    )
}
