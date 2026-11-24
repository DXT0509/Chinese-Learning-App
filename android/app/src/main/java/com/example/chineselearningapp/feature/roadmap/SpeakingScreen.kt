package com.example.chineselearningapp.feature.roadmap

import androidx.compose.runtime.Composable
import com.example.chineselearningapp.domain.model.RoadmapExample

/**
 * SpeakingScreen (đọc câu) is the SENTENCE mode of PronunciationScreen.
 * Character card automatically wraps text and sizes font down for longer sentences,
 * omitting the TianZiGe grid.
 * IMPORTANT: No sample audio playback anywhere on this screen.
 */
@Composable
internal fun SpeakingScreen(
    sentence: RoadmapExample?,
    fallbackTarget: String,
    state: LessonState = LessonState(),
    enabled: Boolean = true,
    result: (List<String>, Int) -> Unit = { _, _ -> },
    next: () -> Unit = {},
    back: () -> Unit = {},
    onSkip: () -> Unit = {},
    progress: Float = 8f / 9f,
    onKnownWord: () -> Unit = {},
    onLeaveLesson: () -> Unit = {},
    onPauseLesson: () -> Unit = {},
    onResumeLesson: () -> Unit = {},
    status: @Composable () -> Unit = {}
) {
    val target = sentence?.simplified ?: fallbackTarget
    val meaning = sentence?.vietnamese.orEmpty()
    val pinyin = sentence?.pinyin.orEmpty()

    PronunciationScreen(
        target = target,
        meaning = meaning,
        pinyin = pinyin,
        mode = PronunciationMode.SENTENCE,
        state = state,
        enabled = enabled,
        result = result,
        next = next,
        back = back,
        onSkip = onSkip,
        progress = progress,
        onKnownWord = onKnownWord,
        onLeaveLesson = onLeaveLesson,
        onPauseLesson = onPauseLesson,
        onResumeLesson = onResumeLesson,
        status = status
    )
}

@Composable
internal fun SpeakingScreen(
    sentence: RoadmapExample?,
    fallbackTarget: String,
    state: LessonState,
    enabled: Boolean,
    result: (String, Int) -> Unit,
    next: () -> Unit,
    back: () -> Unit,
    status: @Composable () -> Unit = {}
) = SpeakingScreen(
    sentence = sentence,
    fallbackTarget = fallbackTarget,
    state = state,
    enabled = enabled,
    result = { candidates, duration -> result(candidates.firstOrNull().orEmpty(), duration) },
    next = next,
    back = back,
    onSkip = {},
    status = status
)
