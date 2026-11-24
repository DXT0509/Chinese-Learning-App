package com.example.chineselearningapp.domain.model

data class ReviewSession(
    val groupId: String,
    val words: List<ReviewWord> // 3–5 từ
)

data class ReviewWord(
    val hanzi: String,
    val pinyin: String,
    val meaning: String, // tiếng Việt
    val distractors: List<String> // 3 nghĩa sai cho trắc nghiệm
)

/**
 * Review session XP formula:
 * baseXP = 50 (ôn tập ít hơn bài mới)
 * finalXP = 50 * max(0.1, 1 - mistakeCount * 0.1)
 */
fun calculateReviewXp(mistakeCount: Int, baseXP: Int = 50): Int {
    val factor = maxOf(0.1, 1.0 - mistakeCount * 0.1)
    return (baseXP * factor).toInt()
}

