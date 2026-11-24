package com.example.chineselearningapp.feature.roadmap

import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import com.example.chineselearningapp.domain.model.ListeningQuestion
import com.example.chineselearningapp.domain.model.RoadmapActivity
import com.example.chineselearningapp.domain.model.Word

/**
 * Legacy compatibility wrapper for MultipleChoiceScreen.
 * Delegates to ListeningChoiceScreen. The old radio buttons, "Trả lời" button,
 * and "Câu hỏi" chips have been removed.
 */
@Composable
internal fun MultipleChoiceScreen(
    activity: RoadmapActivity?,
    feedback: Boolean?,
    enabled: Boolean,
    submit: (Int) -> Unit,
    next: () -> Unit,
    back: () -> Unit,
    status: @Composable () -> Unit
) {
    var qIndex by rememberSaveable(activity?.id) { mutableIntStateOf(0) }
    val questionCount = 2
    val question = remember(activity?.id, qIndex) {
        val options = activity?.options.orEmpty().take(4).map {
            Word(hanzi = it, pinyin = null, reading = null, meaning = null, partOfSpeech = null, notes = null)
        }
        val safeOptions = if (options.size == 4) {
            options
        } else {
            val list = options.toMutableList()
            while (list.size < 4) {
                list.add(Word(hanzi = "字${list.size + 1}", pinyin = null, reading = null, meaning = null, partOfSpeech = null, notes = null))
            }
            list
        }
        val answer = safeOptions.firstOrNull() ?: Word(hanzi = "字", pinyin = null, reading = null, meaning = null, partOfSpeech = null, notes = null)
        ListeningQuestion(
            answerWord = answer,
            options = safeOptions,
            questionIndex = qIndex,
            questionCount = questionCount
        )
    }

    ListeningChoiceScreen(
        question = question,
        onAnswerChecked = { isCorrect ->
            submit(if (isCorrect) 0 else 1)
        },
        onContinue = {
            if (qIndex < questionCount - 1) {
                qIndex++
            } else {
                next()
            }
        },
        onBack = {
            if (qIndex > 0) {
                qIndex--
            } else {
                back()
            }
        },
        status = status
    )
}
