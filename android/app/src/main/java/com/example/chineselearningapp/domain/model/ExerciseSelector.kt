package com.example.chineselearningapp.domain.model

/**
 * Exercise manual configuration block optionally provided in lesson data.
 *
 * Example in lesson JSON:
 * {
 *   "exercises": {
 *     "listening": {
 *       "items": [
 *         { "answer": "好", "distractors": ["女", "子", "妈"] },
 *         { "answer": "你", "distractors": ["好", "我"] }
 *       ],
 *       "skipSecond": true
 *     }
 *   }
 * }
 */
data class ExerciseItemConfig(
    val answer: String? = null,
    val distractors: List<String> = emptyList()
)

data class ListeningExerciseConfig(
    val items: List<ExerciseItemConfig> = emptyList(),
    val skipSecond: Boolean = false
)

data class LessonExercisesConfig(
    val listening: ListeningExerciseConfig? = null,
    val skipSecond: Boolean = false
) {
    val effectiveSkipSecond: Boolean
        get() = skipSecond || (listening?.skipSecond == true)
}

/**
 * Represents a learning lesson provided to the ExerciseSelector.
 */
data class Lesson(
    val id: String,
    val targetWord: Word,
    val words: List<Word> = listOf(targetWord),
    val exercises: LessonExercisesConfig? = null,
    val attemptIndex: Int = 0
) {
    constructor(
        id: String,
        words: List<Word>,
        exercises: LessonExercisesConfig? = null,
        attemptIndex: Int = 0
    ) : this(
        id = id,
        targetWord = words.firstOrNull() ?: Word(
            hanzi = "",
            pinyin = null,
            reading = null,
            meaning = null,
            partOfSpeech = null,
            notes = null
        ),
        words = words,
        exercises = exercises,
        attemptIndex = attemptIndex
    )
}

/**
 * A word learned previously in the roadmap with review and mastery metadata.
 */
data class LearnedWord(
    val word: Word,
    val masteryLevel: Int = 0,
    val isDueForReview: Boolean = false,
    val nextReviewDue: Long? = null,
    val learnedAt: Long? = null
)

/**
 * Context of the learner when entering a lesson.
 */
data class LearnerContext(
    val learnedRoadmapWords: List<LearnedWord> = emptyList(),
    val savedWords: List<Word> = emptyList(),
    val databaseWords: List<Word> = emptyList(),
    val confusableMap: Map<String, List<String>> = emptyMap()
) {
    companion object {
        fun fromWords(
            learnedWords: List<Word>,
            savedWords: List<Word> = emptyList(),
            databaseWords: List<Word> = emptyList(),
            confusableMap: Map<String, List<String>> = emptyMap()
        ): LearnerContext = LearnerContext(
            learnedRoadmapWords = learnedWords.map { LearnedWord(it) },
            savedWords = savedWords,
            databaseWords = databaseWords,
            confusableMap = confusableMap
        )
    }
}

/**
 * ExerciseSelector interface: selects exercises (such as listening) for a lesson.
 * Designed to be easily extensible for future exercise types (fill-in-the-blank, matching...).
 */
interface ExerciseSelector {
    fun selectListening(
        lesson: Lesson,
        context: LearnerContext
    ): List<ListeningQuestion>
}

