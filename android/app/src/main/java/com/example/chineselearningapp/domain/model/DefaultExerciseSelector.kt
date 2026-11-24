package com.example.chineselearningapp.domain.model

import java.text.Normalizer
import java.util.Locale
import kotlin.random.Random

/**
 * Default implementation of [ExerciseSelector].
 *
 * Implements the fallback mechanism: manual configuration -> prioritized fallback.
 * - Max 2 listening questions per lesson:
 *     - Question 1: target word of current lesson.
 *     - Question 2: an older word; target word of current lesson is in distractors.
 * - Always exactly 4 options per question.
 * - Manual configuration overrides automatic selection.
 * - Disambiguation constraints (unique Hanzi, non-empty, pinyin != answer).
 * - Deterministic shuffling based on (lessonId + attemptIndex).
 */
class DefaultExerciseSelector(
    private val defaultConfusableMap: Map<String, List<String>> = BUILT_IN_CONFUSABLES,
    private val defaultDatabaseWords: List<Word> = BUILT_IN_CATALOG_WORDS,
    private val logger: (String) -> Unit = { message ->
        System.err.println("[ExerciseSelector] $message")
    }
) : ExerciseSelector {

    override fun selectListening(
        lesson: Lesson,
        context: LearnerContext
    ): List<ListeningQuestion> {
        val confusableMap = if (context.confusableMap.isNotEmpty()) context.confusableMap else defaultConfusableMap
        val catalogWords = (context.databaseWords + defaultDatabaseWords).distinctBy { it.hanzi }
        val allAvailableWords = (catalogWords + context.savedWords + context.learnedRoadmapWords.map { it.word } + lesson.words)
            .filter { it.hasDisplayableHanzi() }
            .distinctBy { it.hanzi }

        val wordDb = allAvailableWords.associateBy { it.hanzi.orEmpty() }

        // --- Question 1 Selection ---
        val q1Config = lesson.exercises?.listening?.items?.getOrNull(0)
        val q1Answer = resolveAnswerWord(
            configuredAnswer = q1Config?.answer,
            fallbackWord = lesson.targetWord,
            wordDb = wordDb,
            questionNumber = 1
        )

        val q1Distractors = selectDistractorsForQuestion1(
            answer = q1Answer,
            manualDistractorChars = q1Config?.distractors.orEmpty(),
            context = context,
            confusableMap = confusableMap,
            catalogWords = catalogWords,
            wordDb = wordDb,
            seed = computeSeed(lesson.id, lesson.attemptIndex, 0)
        )

        val q1Seed = computeSeed(lesson.id, lesson.attemptIndex, 0)
        val q1Options = (q1Distractors + q1Answer).shuffled(Random(q1Seed))

        // --- Question 2 Selection ---
        val shouldSkipSecond = lesson.exercises?.effectiveSkipSecond == true
        val q2Config = lesson.exercises?.listening?.items?.getOrNull(1)

        val q2Answer = if (shouldSkipSecond) {
            null
        } else {
            resolveQuestion2Answer(
                configuredAnswer = q2Config?.answer,
                q1Answer = q1Answer,
                targetWord = lesson.targetWord,
                context = context,
                wordDb = wordDb,
                seed = computeSeed(lesson.id, lesson.attemptIndex, 1)
            )
        }

        val questionList = mutableListOf<ListeningQuestion>()

        if (q2Answer == null) {
            // Only 1 question
            questionList.add(
                ListeningQuestion(
                    answerWord = q1Answer,
                    options = q1Options,
                    questionIndex = 0,
                    questionCount = 1
                )
            )
            return questionList
        }

        // Question 2 distractors
        val q2Distractors = selectDistractorsForQuestion2(
            answer = q2Answer,
            targetWord = lesson.targetWord,
            manualConfig = q2Config,
            context = context,
            confusableMap = confusableMap,
            catalogWords = catalogWords,
            wordDb = wordDb,
            seed = computeSeed(lesson.id, lesson.attemptIndex, 1)
        )

        val q2Seed = computeSeed(lesson.id, lesson.attemptIndex, 1)
        val q2Options = (q2Distractors + q2Answer).shuffled(Random(q2Seed))

        questionList.add(
            ListeningQuestion(
                answerWord = q1Answer,
                options = q1Options,
                questionIndex = 0,
                questionCount = 2
            )
        )
        questionList.add(
            ListeningQuestion(
                answerWord = q2Answer,
                options = q2Options,
                questionIndex = 1,
                questionCount = 2
            )
        )

        return questionList
    }

    // ---------------------------------------------------------------------------------------------
    // Answer Resolvers
    // ---------------------------------------------------------------------------------------------

    private fun resolveAnswerWord(
        configuredAnswer: String?,
        fallbackWord: Word,
        wordDb: Map<String, Word>,
        questionNumber: Int
    ): Word {
        if (!configuredAnswer.isNullOrBlank() && configuredAnswer != "auto") {
            val word = wordDb[configuredAnswer]
            if (word == null) {
                logger("Question $questionNumber manual answer '$configuredAnswer' not found in database; using fallback.")
            } else if (!word.hasAudio()) {
                logger("Question $questionNumber manual answer '$configuredAnswer' has no audio; using fallback.")
            } else {
                return word
            }
        }
        // Fallback
        val resolvedFallback = wordDb[fallbackWord.hanzi] ?: fallbackWord
        if (!resolvedFallback.hasAudio()) {
            logger("Warning: Fallback answer '${resolvedFallback.hanzi}' has no audio asset/id.")
        }
        return resolvedFallback
    }

    private fun resolveQuestion2Answer(
        configuredAnswer: String?,
        q1Answer: Word,
        targetWord: Word,
        context: LearnerContext,
        wordDb: Map<String, Word>,
        seed: Long
    ): Word? {
        // 1. Manual configuration override
        if (!configuredAnswer.isNullOrBlank() && configuredAnswer != "auto") {
            if (configuredAnswer == q1Answer.hanzi) {
                logger("Question 2 manual answer cannot be the same as Question 1 ('$configuredAnswer'); falling back.")
            } else if (configuredAnswer == targetWord.hanzi) {
                logger("Question 2 manual answer cannot be the same as current learning word ('$configuredAnswer'); falling back.")
            } else {
                val word = wordDb[configuredAnswer]
                if (word == null) {
                    logger("Question 2 manual answer '$configuredAnswer' not found in database; falling back.")
                } else if (!word.hasAudio()) {
                    logger("Question 2 manual answer '$configuredAnswer' has no audio; falling back.")
                } else {
                    return word
                }
            }
        }

        val random = Random(seed)

        // 2. Priority 1: Learned words in roadmap (prioritize due for review, lowest mastery, tie-break random)
        val roadmapCandidates = context.learnedRoadmapWords
            .filter { learned ->
                val w = learned.word
                w.hasDisplayableHanzi() &&
                        w.hasAudio() &&
                        w.hanzi != targetWord.hanzi &&
                        w.hanzi != q1Answer.hanzi
            }

        if (roadmapCandidates.isNotEmpty()) {
            // Sort by:
            // 1. isDueForReview descending (true first)
            // 2. masteryLevel ascending (lower mastery first)
            val sorted = roadmapCandidates.shuffled(random).sortedWith(
                compareByDescending<LearnedWord> { it.isDueForReview }
                    .thenBy { it.masteryLevel }
            )
            val chosen = sorted.first()
            return wordDb[chosen.word.hanzi] ?: chosen.word
        }

        // 3. Priority 2: User's saved words (excluding target word and q1 answer)
        val savedCandidates = context.savedWords
            .filter { w ->
                w.hasDisplayableHanzi() &&
                        w.hasAudio() &&
                        w.hanzi != targetWord.hanzi &&
                        w.hanzi != q1Answer.hanzi
            }

        if (savedCandidates.isNotEmpty()) {
            val chosen = savedCandidates.shuffled(random).first()
            return wordDb[chosen.hanzi] ?: chosen
        }

        // 4. Priority 3: No old words available -> DROP question 2
        return null
    }

    // ---------------------------------------------------------------------------------------------
    // Distractor Selectors
    // ---------------------------------------------------------------------------------------------

    private fun selectDistractorsForQuestion1(
        answer: Word,
        manualDistractorChars: List<String>,
        context: LearnerContext,
        confusableMap: Map<String, List<String>>,
        catalogWords: List<Word>,
        wordDb: Map<String, Word>,
        seed: Long
    ): List<Word> {
        val selected = mutableListOf<Word>()
        val random = Random(seed)

        // 1. Manual distractors
        for (char in manualDistractorChars.take(3)) {
            val word = wordDb[char]
            if (word == null) {
                logger("Question 1 manual distractor '$char' not found in database; skipping.")
                continue
            }
            if (!word.hasAudio()) {
                logger("Question 1 manual distractor '$char' has no audio; skipping.")
                continue
            }
            if (word.hanzi == answer.hanzi) {
                logger("Question 1 manual distractor '$char' matches answer; skipping.")
                continue
            }
            if (isPinyinIdentical(word.pinyin, answer.pinyin)) {
                logger("Question 1 manual distractor '$char' has identical pinyin (${word.pinyin}) to answer; skipping.")
                continue
            }
            if (selected.any { it.hanzi == word.hanzi }) {
                continue
            }
            selected.add(word)
        }

        fillRemainingDistractors(
            neededCount = 3 - selected.size,
            selected = selected,
            answer = answer,
            context = context,
            confusableMap = confusableMap,
            catalogWords = catalogWords,
            wordDb = wordDb,
            random = random
        )

        return selected
    }

    private fun selectDistractorsForQuestion2(
        answer: Word,
        targetWord: Word,
        manualConfig: ExerciseItemConfig?,
        context: LearnerContext,
        confusableMap: Map<String, List<String>>,
        catalogWords: List<Word>,
        wordDb: Map<String, Word>,
        seed: Long
    ): List<Word> {
        val selected = mutableListOf<Word>()
        val random = Random(seed)
        val hasManualDistractors = !manualConfig?.distractors.isNullOrEmpty()

        if (hasManualDistractors) {
            for (char in manualConfig!!.distractors.take(3)) {
                val word = wordDb[char]
                if (word == null) {
                    logger("Question 2 manual distractor '$char' not found in database; skipping.")
                    continue
                }
                if (!word.hasAudio()) {
                    logger("Question 2 manual distractor '$char' has no audio; skipping.")
                    continue
                }
                if (word.hanzi == answer.hanzi) {
                    logger("Question 2 manual distractor '$char' matches answer; skipping.")
                    continue
                }
                if (isPinyinIdentical(word.pinyin, answer.pinyin)) {
                    logger("Question 2 manual distractor '$char' has identical pinyin (${word.pinyin}) to answer; skipping.")
                    continue
                }
                if (selected.any { it.hanzi == word.hanzi }) {
                    continue
                }
                selected.add(word)
            }
        } else {
            // Rule: "nếu tôi không chỉ định, BẮT BUỘC đưa từ đang học vào làm 1 trong 3 nhiễu"
            val resolvedTarget = wordDb[targetWord.hanzi] ?: targetWord
            if (resolvedTarget.hasDisplayableHanzi() &&
                resolvedTarget.hanzi != answer.hanzi &&
                !isPinyinIdentical(resolvedTarget.pinyin, answer.pinyin)
            ) {
                selected.add(resolvedTarget)
            }
        }

        fillRemainingDistractors(
            neededCount = 3 - selected.size,
            selected = selected,
            answer = answer,
            context = context,
            confusableMap = confusableMap,
            catalogWords = catalogWords,
            wordDb = wordDb,
            random = random
        )

        return selected
    }

    private fun fillRemainingDistractors(
        neededCount: Int,
        selected: MutableList<Word>,
        answer: Word,
        context: LearnerContext,
        confusableMap: Map<String, List<String>>,
        catalogWords: List<Word>,
        wordDb: Map<String, Word>,
        random: Random
    ) {
        if (selected.size >= 3) return

        val answerHanzi = answer.hanzi.orEmpty()
        val confusableChars = confusableMap[answerHanzi].orEmpty()

        fun isEligible(w: Word?): Boolean {
            if (w == null) return false
            if (!w.hasDisplayableHanzi()) return false
            if (!w.hasAudio()) return false
            if (w.hanzi == answer.hanzi) return false
            if (selected.any { it.hanzi == w.hanzi }) return false
            if (isPinyinIdentical(w.pinyin, answer.pinyin)) return false
            return true
        }

        // Priority 2: Learned words in roadmap (prioritize Hanzi or Pinyin similarity, then random)
        val learnedWords = context.learnedRoadmapWords.map { it.word }
            .mapNotNull { wordDb[it.hanzi] ?: it }
            .filter { isEligible(it) }

        if (learnedWords.isNotEmpty()) {
            val sorted = learnedWords.shuffled(random).sortedByDescending {
                similarityScore(it, answer, confusableChars)
            }
            for (w in sorted) {
                if (selected.size >= 3) return
                if (isEligible(w)) selected.add(w)
            }
        }

        // Priority 3: User's saved words
        val savedWords = context.savedWords
            .mapNotNull { wordDb[it.hanzi] ?: it }
            .filter { isEligible(it) }

        if (savedWords.isNotEmpty()) {
            val sorted = savedWords.shuffled(random).sortedByDescending {
                similarityScore(it, answer, confusableChars)
            }
            for (w in sorted) {
                if (selected.size >= 3) return
                if (isEligible(w)) selected.add(w)
            }
        }

        // Priority 4: Confusable characters list (confusable_chars.json)
        for (char in confusableChars) {
            if (selected.size >= 3) return
            val w = wordDb[char]
            if (isEligible(w)) {
                selected.add(w!!)
            }
        }

        // Priority 5: Most common unlearned words in database (sorted by frequency/HSK level)
        val learnedHanzi = (context.learnedRoadmapWords.mapNotNull { it.word.hanzi } +
                context.savedWords.mapNotNull { it.hanzi }).toSet()

        val unlearnedCommon = catalogWords
            .filter { !learnedHanzi.contains(it.hanzi) }
            .filter { isEligible(it) }

        for (w in unlearnedCommon) {
            if (selected.size >= 3) return
            if (isEligible(w)) {
                selected.add(w)
            }
        }

        // Fallback emergency safety: if still not 3 distractors, take any remaining eligible catalog word
        for (w in catalogWords) {
            if (selected.size >= 3) return
            if (isEligible(w)) {
                selected.add(w)
            }
        }
    }

    // ---------------------------------------------------------------------------------------------
    // Helpers
    // ---------------------------------------------------------------------------------------------

    private fun computeSeed(lessonId: String, attemptIndex: Int, questionIndex: Int): Long {
        val str = "$lessonId:$attemptIndex:$questionIndex"
        return str.hashCode().toLong()
    }

    private fun similarityScore(candidate: Word, answer: Word, confusableList: List<String>): Int {
        var score = 0
        val cHanzi = candidate.hanzi.orEmpty()
        val aHanzi = answer.hanzi.orEmpty()

        if (confusableList.contains(cHanzi) || (cHanzi.isNotEmpty() && aHanzi.contains(cHanzi))) {
            score += 15
        }

        val cBase = stripToneMarks(candidate.pinyin)
        val aBase = stripToneMarks(answer.pinyin)
        if (cBase.isNotEmpty() && cBase == aBase) {
            score += 10
        } else if (cBase.isNotEmpty() && aBase.isNotEmpty() &&
            (cBase.take(1) == aBase.take(1) || cBase.takeLast(2) == aBase.takeLast(2))
        ) {
            score += 3
        }

        return score
    }

    private fun stripToneMarks(pinyin: String?): String {
        if (pinyin.isNullOrBlank()) return ""
        val decomposed = Normalizer.normalize(
            pinyin.trim().lowercase(Locale.ROOT),
            Normalizer.Form.NFD
        )
        return decomposed.replace(Regex("\\p{M}"), "").replace(Regex("[1-5]"), "").trim()
    }

    private fun normalizePinyin(pinyin: String?): String {
        if (pinyin.isNullOrBlank()) return ""
        val normalized = Normalizer.normalize(
            pinyin.trim().lowercase(Locale.ROOT),
            Normalizer.Form.NFC
        )
        return normalized.replace(Regex("\\s+"), " ")
    }

    private fun isPinyinIdentical(p1: String?, p2: String?): Boolean {
        val n1 = normalizePinyin(p1)
        val n2 = normalizePinyin(p2)
        return n1.isNotEmpty() && n1 == n2
    }

    private fun Word.hasAudio(): Boolean = !audio.isNullOrBlank() || !audioId.isNullOrBlank()
    private fun Word.hasDisplayableHanzi(): Boolean = !hanzi.isNullOrBlank()

    companion object {
        val BUILT_IN_CONFUSABLES: Map<String, List<String>> = mapOf(
            "好" to listOf("女", "子", "妈", "如", "妹"),
            "你" to listOf("他", "她", "们", "什", "尔"),
            "我" to listOf("找", "钱", "俄", "戈", "代"),
            "他" to listOf("她", "你", "地", "也", "们"),
            "她" to listOf("他", "妈", "妹", "姐", "好"),
            "女" to listOf("子", "好", "妈", "如", "妹"),
            "子" to listOf("女", "好", "字", "了"),
            "妈" to listOf("妹", "姐", "好", "女", "马"),
            "不" to listOf("木", "本", "下", "否"),
            "很" to listOf("得", "行", "往", "德"),
            "是" to listOf("足", "定", "走", "题"),
            "的" to listOf("白", "勺", "百"),
            "大" to listOf("太", "犬", "天", "小"),
            "太" to listOf("大", "犬", "天"),
            "小" to listOf("少", "水", "大"),
            "少" to listOf("小", "多", "步"),
            "人" to listOf("入", "八", "个", "大"),
            "八" to listOf("人", "入", "六"),
            "十" to listOf("千", "土", "士"),
            "看" to listOf("着", "见", "目", "手"),
            "见" to listOf("贝", "视", "看", "规"),
            "请" to listOf("清", "情", "晴", "说", "语"),
            "说" to listOf("话", "请", "读", "语"),
            "话" to listOf("说", "语", "活"),
            "吃" to listOf("叫", "喝", "口", "吧"),
            "喝" to listOf("唱", "吃", "渴"),
            "家" to listOf("字", "安", "定", "宝"),
            "学" to listOf("字", "子", "教"),
            "字" to listOf("子", "学", "安"),
            "有" to listOf("友", "月", "右"),
            "钱" to listOf("浅", "线", "我"),
            "买" to listOf("卖", "头"),
            "卖" to listOf("买", "读")
        )

        /**
         * Standard catalog words pool (HSK 0/1) sorted by lower frequency rank / HSK level.
         * All words have valid Hanzi, Pinyin, Vietnamese meaning, and audioId.
         */
        val BUILT_IN_CATALOG_WORDS: List<Word> = listOf(
            Word(hanzi = "我", pinyin = "wǒ", reading = "ngã", meaning = "tôi, mình", partOfSpeech = "pron", notes = null, audioId = "audio_wo"),
            Word(hanzi = "你", pinyin = "nǐ", reading = "nhĩ", meaning = "bạn, cậu", partOfSpeech = "pron", notes = null, audioId = "audio_ni"),
            Word(hanzi = "好", pinyin = "hǎo", reading = "hảo", meaning = "tốt, ổn, khỏe", partOfSpeech = "adj", notes = null, audioId = "audio_hao"),
            Word(hanzi = "他", pinyin = "tā", reading = "tha", meaning = "anh ấy, cậu ấy", partOfSpeech = "pron", notes = null, audioId = "audio_ta"),
            Word(hanzi = "她", pinyin = "tā", reading = "tha", meaning = "cô ấy, chị ấy", partOfSpeech = "pron", notes = null, audioId = "audio_ta2"),
            Word(hanzi = "们", pinyin = "men", reading = "môn", meaning = "các, chúng", partOfSpeech = "affix", notes = null, audioId = "audio_men"),
            Word(hanzi = "不", pinyin = "bù", reading = "bất", meaning = "không, chẳng", partOfSpeech = "adv", notes = null, audioId = "audio_bu"),
            Word(hanzi = "很", pinyin = "hěn", reading = "khẩn", meaning = "rất, lắm", partOfSpeech = "adv", notes = null, audioId = "audio_hen"),
            Word(hanzi = "是", pinyin = "shì", reading = "thị", meaning = "là, phải", partOfSpeech = "v", notes = null, audioId = "audio_shi"),
            Word(hanzi = "的", pinyin = "de", reading = "đích", meaning = "của", partOfSpeech = "part", notes = null, audioId = "audio_de"),
            Word(hanzi = "女", pinyin = "nǚ", reading = "nữ", meaning = "nữ, con gái", partOfSpeech = "n", notes = null, audioId = "audio_nv"),
            Word(hanzi = "子", pinyin = "zǐ", reading = "tử", meaning = "con, đứa bé", partOfSpeech = "n", notes = null, audioId = "audio_zi"),
            Word(hanzi = "妈", pinyin = "mā", reading = "mã", meaning = "mẹ", partOfSpeech = "n", notes = null, audioId = "audio_ma"),
            Word(hanzi = "爸", pinyin = "bà", reading = "ba", meaning = "bố, ba", partOfSpeech = "n", notes = null, audioId = "audio_ba"),
            Word(hanzi = "人", pinyin = "rén", reading = "nhân", meaning = "người", partOfSpeech = "n", notes = null, audioId = "audio_ren"),
            Word(hanzi = "大", pinyin = "dà", reading = "đại", meaning = "lớn, to", partOfSpeech = "adj", notes = null, audioId = "audio_da"),
            Word(hanzi = "小", pinyin = "xiǎo", reading = "tiểu", meaning = "nhỏ, bé", partOfSpeech = "adj", notes = null, audioId = "audio_xiao"),
            Word(hanzi = "吃", pinyin = "chī", reading = "ngật", meaning = "ăn", partOfSpeech = "v", notes = null, audioId = "audio_chi"),
            Word(hanzi = "喝", pinyin = "hē", reading = "hát", meaning = "uống", partOfSpeech = "v", notes = null, audioId = "audio_he"),
            Word(hanzi = "茶", pinyin = "chá", reading = "trà", meaning = "trà", partOfSpeech = "n", notes = null, audioId = "audio_cha"),
            Word(hanzi = "水", pinyin = "shuǐ", reading = "thủy", meaning = "nước", partOfSpeech = "n", notes = null, audioId = "audio_shui"),
            Word(hanzi = "看", pinyin = "kàn", reading = "khán", meaning = "nhìn, xem", partOfSpeech = "v", notes = null, audioId = "audio_kan"),
            Word(hanzi = "听", pinyin = "tīng", reading = "thính", meaning = "nghe", partOfSpeech = "v", notes = null, audioId = "audio_ting"),
            Word(hanzi = "说", pinyin = "shuō", reading = "thuyết", meaning = "nói", partOfSpeech = "v", notes = null, audioId = "audio_shuo"),
            Word(hanzi = "写", pinyin = "xiě", reading = "tả", meaning = "viết", partOfSpeech = "v", notes = null, audioId = "audio_xie"),
            Word(hanzi = "字", pinyin = "zì", reading = "tự", meaning = "chữ", partOfSpeech = "n", notes = null, audioId = "audio_zi2"),
            Word(hanzi = "学", pinyin = "xué", reading = "học", meaning = "học", partOfSpeech = "v", notes = null, audioId = "audio_xue"),
            Word(hanzi = "家", pinyin = "jiā", reading = "gia", meaning = "nhà, gia đình", partOfSpeech = "n", notes = null, audioId = "audio_jia"),
            Word(hanzi = "有", pinyin = "yǒu", reading = "hữu", meaning = "có", partOfSpeech = "v", notes = null, audioId = "audio_you"),
            Word(hanzi = "没", pinyin = "méi", reading = "một", meaning = "không có, chưa", partOfSpeech = "adv", notes = null, audioId = "audio_mei"),
            Word(hanzi = "这", pinyin = "zhè", reading = "giá", meaning = "đây, này", partOfSpeech = "pron", notes = null, audioId = "audio_zhe"),
            Word(hanzi = "那", pinyin = "nà", reading = "na", meaning = "đó, kia", partOfSpeech = "pron", notes = null, audioId = "audio_na"),
            Word(hanzi = "叫", pinyin = "jiào", reading = "khiếu", meaning = "gọi là, tên là", partOfSpeech = "v", notes = null, audioId = "audio_jiao"),
            Word(hanzi = "在", pinyin = "zài", reading = "tại", meaning = "ở, tại, đang", partOfSpeech = "prep", notes = null, audioId = "audio_zai"),
            Word(hanzi = "来", pinyin = "lái", reading = "lai", meaning = "đến, lại", partOfSpeech = "v", notes = null, audioId = "audio_lai"),
            Word(hanzi = "去", pinyin = "qù", reading = "khứ", meaning = "đi", partOfSpeech = "v", notes = null, audioId = "audio_qu"),
            Word(hanzi = "多", pinyin = "duō", reading = "đa", meaning = "nhiều", partOfSpeech = "adj", notes = null, audioId = "audio_duo"),
            Word(hanzi = "少", pinyin = "shǎo", reading = "thiểu", meaning = "ít", partOfSpeech = "adj", notes = null, audioId = "audio_shao"),
            Word(hanzi = "钱", pinyin = "qián", reading = "tiền", meaning = "tiền", partOfSpeech = "n", notes = null, audioId = "audio_qian"),
            Word(hanzi = "点", pinyin = "diǎn", reading = "điểm", meaning = "chút, giờ", partOfSpeech = "n", notes = null, audioId = "audio_dian"),
            Word(hanzi = "谁", pinyin = "shéi", reading = "thùy", meaning = "ai", partOfSpeech = "pron", notes = null, audioId = "audio_shei"),
            Word(hanzi = "么", pinyin = "me", reading = "ma", meaning = "gì, sao", partOfSpeech = "part", notes = null, audioId = "audio_me"),
            Word(hanzi = "什", pinyin = "shén", reading = "thập", meaning = "gì", partOfSpeech = "pron", notes = null, audioId = "audio_shen"),
            Word(hanzi = "吗", pinyin = "ma", reading = "ma", meaning = "không, chăng", partOfSpeech = "part", notes = null, audioId = "audio_ma_part"),
            Word(hanzi = "呢", pinyin = "ne", reading = "ni", meaning = "thế, còn", partOfSpeech = "part", notes = null, audioId = "audio_ne"),
            Word(hanzi = "吧", pinyin = "ba", reading = "ba", meaning = "nhé, đi", partOfSpeech = "part", notes = null, audioId = "audio_ba_part"),
            Word(hanzi = "一", pinyin = "yī", reading = "nhất", meaning = "một", partOfSpeech = "num", notes = null, audioId = "audio_yi"),
            Word(hanzi = "二", pinyin = "èr", reading = "nhị", meaning = "hai", partOfSpeech = "num", notes = null, audioId = "audio_er"),
            Word(hanzi = "三", pinyin = "sān", reading = "tam", meaning = "ba", partOfSpeech = "num", notes = null, audioId = "audio_san"),
            Word(hanzi = "四", pinyin = "sì", reading = "tứ", meaning = "bốn", partOfSpeech = "num", notes = null, audioId = "audio_si"),
            Word(hanzi = "五", pinyin = "wǔ", reading = "ngũ", meaning = "năm", partOfSpeech = "num", notes = null, audioId = "audio_wu"),
            Word(hanzi = "六", pinyin = "liù", reading = "lục", meaning = "sáu", partOfSpeech = "num", notes = null, audioId = "audio_liu"),
            Word(hanzi = "七", pinyin = "qī", reading = "thất", meaning = "bảy", partOfSpeech = "num", notes = null, audioId = "audio_qi"),
            Word(hanzi = "八", pinyin = "bā", reading = "bát", meaning = "tám", partOfSpeech = "num", notes = null, audioId = "audio_ba8"),
            Word(hanzi = "九", pinyin = "jiǔ", reading = "cửu", meaning = "chín", partOfSpeech = "num", notes = null, audioId = "audio_jiu"),
            Word(hanzi = "十", pinyin = "shí", reading = "thập", meaning = "mười", partOfSpeech = "num", notes = null, audioId = "audio_shi2")
        )
    }
}

