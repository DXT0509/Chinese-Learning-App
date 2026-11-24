package com.example.chineselearningapp.feature.roadmap

import com.example.chineselearningapp.R

internal fun activityTitle(kind: String): Int = when (kind) {
    "INTRODUCTION" -> R.string.roadmap_introduction
    "COMPONENTS" -> R.string.roadmap_components
    "STROKE_ORDER" -> R.string.roadmap_stroke_order
    "HANDWRITING" -> R.string.roadmap_handwriting
    "QUIZ" -> R.string.roadmap_quiz
    "PRONUNCIATION" -> R.string.roadmap_pronunciation
    else -> R.string.roadmap_unavailable
}


enum class RoadmapMicrophoneState { Idle, Denied, Unavailable, Recording, Ready }
fun canSubmitSpeaking(state: RoadmapMicrophoneState, durationMs: Int) =
    state == RoadmapMicrophoneState.Ready && durationMs >= 1000
