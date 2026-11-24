package com.example.chineselearningapp

import com.example.chineselearningapp.domain.model.*
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

class ExerciseSelectorTest {

    private lateinit var selector: ExerciseSelector
    private val loggedWarnings = mutableListOf<String>()

    private val targetWord = Word(
        hanzi = "好",
        pinyin = "hǎo",
        reading = "hảo",
        meaning = "tốt",
        partOfSpeech = "adj",
        notes = null,
        audioId = "audio_hao"
    )

    private val oldLearnedWord1 = Word(
        hanzi = "你",
        pinyin = "nǐ",
        reading = "nhĩ",
        meaning = "bạn",
        partOfSpeech = "pron",
        notes = null,
        audioId = "audio_ni"
    )

    private val oldLearnedWord2 = Word(
        hanzi = "我",
        pinyin = "wǒ",
        reading = "ngã",
        meaning = "tôi",
        partOfSpeech = "pron",
        notes = null,
        audioId = "audio_wo"
    )

    private val savedWord = Word(
        hanzi = "茶",
        pinyin = "chá",
        reading = "trà",
        meaning = "trà",
        partOfSpeech = "n",
        notes = null,
        audioId = "audio_cha"
    )

    @Before
    fun setUp() {
        loggedWarnings.clear()
        selector = DefaultExerciseSelector(
            logger = { loggedWarnings.add(it) }
        )
    }

    /**
     * Test 1: Bài đầu tiên của roadmap, người dùng chưa lưu từ nào:
     * Trả đúng 1 câu, 4 options (đủ nhờ fallback mục 3.4/3.5).
     */
    @Test
    fun testFirstLessonNoHistoryReturnsOneQuestionWithFourOptions() {
        val lesson = Lesson(
            id = "lesson-0",
            targetWord = targetWord,
            attemptIndex = 0
        )
        val context = LearnerContext(
            learnedRoadmapWords = emptyList(),
            savedWords = emptyList()
        )

        val questions = selector.selectListening(lesson, context)

        assertEquals("First lesson without old words should return exactly 1 question", 1, questions.size)
        val q1 = questions.first()
        assertEquals(0, q1.questionIndex)
        assertEquals(1, q1.questionCount)
        assertEquals("Answer must be current learning word", "好", q1.answerWord.hanzi)
        assertEquals("Question must have exactly 4 options", 4, q1.options.size)
        assertTrue("Answer must be one of the options", q1.options.any { it.hanzi == "好" })
        assertEquals("Options must be unique", 4, q1.options.map { it.hanzi }.distinct().size)
    }

    /**
     * Test 2: Có từ cũ trong roadmap:
     * Trả 2 câu, câu 2 có từ đang học trong options.
     */
    @Test
    fun testOldWordsInRoadmapReturnsTwoQuestionsWithTargetWordInQ2Options() {
        val lesson = Lesson(
            id = "lesson-2",
            targetWord = targetWord, // "好"
            attemptIndex = 0
        )
        val context = LearnerContext(
            learnedRoadmapWords = listOf(
                LearnedWord(word = oldLearnedWord1, masteryLevel = 2, isDueForReview = false),
                LearnedWord(word = oldLearnedWord2, masteryLevel = 1, isDueForReview = true)
            ),
            savedWords = emptyList()
        )

        val questions = selector.selectListening(lesson, context)

        assertEquals("Should return 2 questions when roadmap has old words", 2, questions.size)
        val q1 = questions[0]
        val q2 = questions[1]

        assertEquals("好", q1.answerWord.hanzi)
        assertEquals(4, q1.options.size)

        // Q2 answer should be from roadmap, prioritized isDueForReview ("我")
        assertEquals("我", q2.answerWord.hanzi)
        assertEquals(4, q2.options.size)
        assertEquals("Options in Q2 must be unique", 4, q2.options.map { it.hanzi }.distinct().size)

        // Rule: câu 2 có từ đang học ("好") trong options
        assertTrue(
            "Question 2 options must contain the current learning word ('好')",
            q2.options.any { it.hanzi == "好" }
        )
    }

    /**
     * Test 3: Roadmap trống nhưng có từ đã lưu:
     * Câu 2 dùng từ đã lưu.
     */
    @Test
    fun testEmptyRoadmapWithSavedWordsUsesSavedWordForQuestion2() {
        val lesson = Lesson(
            id = "lesson-0",
            targetWord = targetWord, // "好"
            attemptIndex = 0
        )
        val context = LearnerContext(
            learnedRoadmapWords = emptyList(),
            savedWords = listOf(savedWord) // "茶"
        )

        val questions = selector.selectListening(lesson, context)

        assertEquals("Should return 2 questions when saved words exist", 2, questions.size)
        val q2 = questions[1]
        assertEquals("Question 2 answer must be from saved words", "茶", q2.answerWord.hanzi)
        assertEquals(4, q2.options.size)
        assertTrue("Question 2 options must include target word '好'", q2.options.any { it.hanzi == "好" })
    }

    /**
     * Test 4: Cấu hình thủ công đủ cả 2 câu và cả nhiễu:
     * Kết quả đúng như cấu hình.
     */
    @Test
    fun testFullManualConfigurationAppliesAccurately() {
        val config = LessonExercisesConfig(
            listening = ListeningExerciseConfig(
                items = listOf(
                    ExerciseItemConfig(answer = "好", distractors = listOf("女", "子", "妈")),
                    ExerciseItemConfig(answer = "你", distractors = listOf("好", "我", "他"))
                )
            )
        )
        val lesson = Lesson(
            id = "lesson-manual",
            targetWord = targetWord,
            exercises = config,
            attemptIndex = 0
        )
        val context = LearnerContext(
            learnedRoadmapWords = listOf(LearnedWord(oldLearnedWord1), LearnedWord(oldLearnedWord2)),
            savedWords = emptyList()
        )

        val questions = selector.selectListening(lesson, context)

        assertEquals(2, questions.size)
        val q1 = questions[0]
        val q2 = questions[1]

        assertEquals("好", q1.answerWord.hanzi)
        val q1OptionHanzi = q1.options.map { it.hanzi }.toSet()
        assertEquals(setOf("好", "女", "子", "妈"), q1OptionHanzi)

        assertEquals("你", q2.answerWord.hanzi)
        val q2OptionHanzi = q2.options.map { it.hanzi }.toSet()
        assertEquals(setOf("你", "好", "我", "他"), q2OptionHanzi)
    }

    /**
     * Test 5: Cấu hình chỉ có `answer`, thiếu nhiễu:
     * Nhiễu được điền bằng fallback, vẫn đủ 4 options.
     */
    @Test
    fun testManualAnswerWithMissingDistractorsFallsBackToFourOptions() {
        val config = LessonExercisesConfig(
            listening = ListeningExerciseConfig(
                items = listOf(
                    ExerciseItemConfig(answer = "好", distractors = listOf("女")), // only 1 distractor
                    ExerciseItemConfig(answer = "你", distractors = emptyList())    // 0 distractors
                )
            )
        )
        val lesson = Lesson(
            id = "lesson-partial",
            targetWord = targetWord,
            exercises = config,
            attemptIndex = 0
        )
        val context = LearnerContext(
            learnedRoadmapWords = listOf(LearnedWord(oldLearnedWord1), LearnedWord(oldLearnedWord2)),
            savedWords = emptyList()
        )

        val questions = selector.selectListening(lesson, context)

        assertEquals(2, questions.size)
        val q1 = questions[0]
        val q2 = questions[1]

        assertEquals("好", q1.answerWord.hanzi)
        assertEquals(4, q1.options.size)
        assertTrue("Q1 must include manually specified distractor '女'", q1.options.any { it.hanzi == "女" })
        assertEquals("All options in Q1 must be distinct", 4, q1.options.map { it.hanzi }.distinct().size)

        assertEquals("你", q2.answerWord.hanzi)
        assertEquals(4, q2.options.size)
        assertEquals("All options in Q2 must be distinct", 4, q2.options.map { it.hanzi }.distinct().size)
        assertTrue("Q2 with empty distractors must include target word '好'", q2.options.any { it.hanzi == "好" })
    }

    /**
     * Test 6: Nhiễu thủ công trùng pinyin với đáp án:
     * Bị loại và thay thế, kèm log cảnh báo.
     */
    @Test
    fun testManualDistractorWithSamePinyinDiscardedAndReplaced() {
        // "他" (tā) and "她" (tā) have identical pinyin with tone!
        // If answer is "他" and manual distractor is "她", "她" must be discarded!
        val taWord = Word(hanzi = "他", pinyin = "tā", reading = "tha", meaning = "anh ấy", partOfSpeech = "pron", notes = null, audioId = "audio_ta")
        val config = LessonExercisesConfig(
            listening = ListeningExerciseConfig(
                items = listOf(
                    ExerciseItemConfig(answer = "他", distractors = listOf("她", "你", "好"))
                )
            )
        )
        val lesson = Lesson(
            id = "lesson-pinyin-clash",
            targetWord = taWord,
            exercises = config,
            attemptIndex = 0
        )
        val context = LearnerContext()

        val questions = selector.selectListening(lesson, context)
        val q1 = questions.first()

        assertEquals(4, q1.options.size)
        assertFalse("Manual distractor '她' with identical pinyin to '他' must be discarded", q1.options.any { it.hanzi == "她" })
        assertTrue("Must log warning for identical pinyin", loggedWarnings.any { it.contains("identical pinyin") })
    }

    /**
     * Test 7: `skipSecond = true`:
     * Chỉ có 1 câu dù đủ từ cũ.
     */
    @Test
    fun testSkipSecondFlagProducesOnlyOneQuestion() {
        val config = LessonExercisesConfig(
            listening = ListeningExerciseConfig(
                skipSecond = true
            )
        )
        val lesson = Lesson(
            id = "lesson-skip-second",
            targetWord = targetWord,
            exercises = config,
            attemptIndex = 0
        )
        val context = LearnerContext(
            learnedRoadmapWords = listOf(LearnedWord(oldLearnedWord1), LearnedWord(oldLearnedWord2)),
            savedWords = listOf(savedWord)
        )

        val questions = selector.selectListening(lesson, context)

        assertEquals("When skipSecond is true, must return exactly 1 question", 1, questions.size)
        assertEquals("好", questions.first().answerWord.hanzi)
        assertEquals(4, questions.first().options.size)
    }

    /**
     * Test 8: Cùng seed → cùng thứ tự; khác seed → thứ tự có thể khác.
     */
    @Test
    fun testDeterministicSeedProducesConsistentShuffling() {
        val lesson1 = Lesson(id = "lesson-seed", targetWord = targetWord, attemptIndex = 0)
        val lessonSameSeed = Lesson(id = "lesson-seed", targetWord = targetWord, attemptIndex = 0)
        val lessonDifferentSeed = Lesson(id = "lesson-seed", targetWord = targetWord, attemptIndex = 5)

        val context = LearnerContext(
            learnedRoadmapWords = listOf(LearnedWord(oldLearnedWord1)),
            savedWords = emptyList()
        )

        val questionsRun1 = selector.selectListening(lesson1, context)
        val questionsRun2 = selector.selectListening(lessonSameSeed, context)
        val questionsRunDiff = selector.selectListening(lessonDifferentSeed, context)

        // Same seed must produce identical order
        assertEquals(
            questionsRun1[0].options.map { it.hanzi },
            questionsRun2[0].options.map { it.hanzi }
        )
        assertEquals(
            questionsRun1[1].options.map { it.hanzi },
            questionsRun2[1].options.map { it.hanzi }
        )

        // Different seeds across several attempts should vary order
        var differentOrderObserved = false
        for (attempt in 1..10) {
            val qDiff = selector.selectListening(
                lesson1.copy(attemptIndex = attempt),
                context
            )
            if (qDiff[0].options.map { it.hanzi } != questionsRun1[0].options.map { it.hanzi }) {
                differentOrderObserved = true
                break
            }
        }
        assertTrue("Different seeds should produce different permutations", differentOrderObserved)
    }

    /**
     * Test 9: Non-existent character in config or missing audio:
     * Logs warning and falls back without crashing.
     */
    @Test
    fun testInvalidCharOrNoAudioLogsWarningAndFallsBack() {
        val config = LessonExercisesConfig(
            listening = ListeningExerciseConfig(
                items = listOf(
                    ExerciseItemConfig(answer = "NON_EXISTENT", distractors = listOf("NOT_REAL", "女", "子"))
                )
            )
        )
        val lesson = Lesson(
            id = "lesson-invalid-chars",
            targetWord = targetWord,
            exercises = config,
            attemptIndex = 0
        )
        val context = LearnerContext()

        val questions = selector.selectListening(lesson, context)
        assertEquals(1, questions.size)
        val q1 = questions.first()

        assertEquals("Fallback answer should be used when manual answer does not exist", "好", q1.answerWord.hanzi)
        assertEquals(4, q1.options.size)
        assertTrue(loggedWarnings.any { it.contains("not found in database") })
    }

    /**
     * Test 10: "auto" answer in manual config:
     * Automatically picks answer while respecting manual distractors.
     */
    @Test
    fun testAutoAnswerUsesAutomaticSelectionWithManualDistractors() {
        val config = LessonExercisesConfig(
            listening = ListeningExerciseConfig(
                items = listOf(
                    ExerciseItemConfig(answer = "auto", distractors = listOf("女", "子"))
                )
            )
        )
        val lesson = Lesson(
            id = "lesson-auto-answer",
            targetWord = targetWord,
            exercises = config,
            attemptIndex = 0
        )
        val context = LearnerContext()

        val questions = selector.selectListening(lesson, context)
        val q1 = questions.first()

        assertEquals("好", q1.answerWord.hanzi)
        assertEquals(4, q1.options.size)
        assertTrue(q1.options.any { it.hanzi == "女" })
        assertTrue(q1.options.any { it.hanzi == "子" })
    }
}

