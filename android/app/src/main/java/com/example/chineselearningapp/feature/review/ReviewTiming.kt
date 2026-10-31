package com.example.chineselearningapp.feature.review

import android.util.Log
import com.example.chineselearningapp.BuildConfig

/** Debug-only durations: no identities, prompts, answers or credentials. */
internal object ReviewTiming {
    fun failure(event: String, error: Exception) {
        val category = when (error) {
            is retrofit2.HttpException -> "http_${error.code()}"
            is java.io.InterruptedIOException -> "timeout"
            is java.io.IOException -> "transport"
            else -> "response"
        }
        if (BuildConfig.DEBUG) runCatching { Log.d("ReviewTiming", "$event failure=$category") }
    }
    fun record(event: String, startedAt: Long) {
        if (BuildConfig.DEBUG) runCatching {
            Log.d("ReviewTiming", "$event ms=${(System.nanoTime() - startedAt) / 1_000_000.0}")
        }
    }
}
