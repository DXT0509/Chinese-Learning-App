package com.example.chineselearningapp.feature.roadmap

import com.example.chineselearningapp.domain.model.ReviewSession
import com.example.chineselearningapp.domain.model.ReviewWord
import com.example.chineselearningapp.domain.model.RoadmapLesson

object ReviewSessionData {
    val HSK0_TOI_BAN_TOT = ReviewSession(
        groupId = "hsk0-toi-ban-tot",
        words = listOf(
            ReviewWord(
                hanzi = "我",
                pinyin = "wǒ",
                meaning = "Tôi / Mình",
                distractors = listOf("Bạn / Cậu", "Tốt / Ổn", "Không")
            ),
            ReviewWord(
                hanzi = "你",
                pinyin = "nǐ",
                meaning = "Bạn / Cậu",
                distractors = listOf("Tôi / Mình", "Anh ấy", "Tốt / Ổn")
            ),
            ReviewWord(
                hanzi = "好",
                pinyin = "hǎo",
                meaning = "Tốt / Ổn",
                distractors = listOf("Xấu / Tệ", "Tôi / Mình", "Có")
            ),
            ReviewWord(
                hanzi = "不",
                pinyin = "bù",
                meaning = "Không / Chẳng",
                distractors = listOf("Có", "Tốt / Ổn", "Rất")
            ),
            ReviewWord(
                hanzi = "很",
                pinyin = "hěn",
                meaning = "Rất / Lắm",
                distractors = listOf("Không", "Ít", "Bạn / Cậu")
            )
        )
    )

    val DUI_BU_QI = ReviewWord(
        hanzi = "对不起",
        pinyin = "duì bu qǐ",
        meaning = "Xin lỗi",
        distractors = listOf("Cảm ơn", "Không có gì", "Tạm biệt")
    )

    fun getByGroupId(groupId: String): ReviewSession? = when (groupId) {
        HSK0_TOI_BAN_TOT.groupId -> HSK0_TOI_BAN_TOT
        else -> null
    }
}

fun RoadmapLesson.toReviewSession(): ReviewSession {
    val curatedMap = (ReviewSessionData.HSK0_TOI_BAN_TOT.words + ReviewSessionData.DUI_BU_QI).associateBy { it.hanzi }
    val reviewWords = if (words.isEmpty()) {
        ReviewSessionData.HSK0_TOI_BAN_TOT.words.take(3)
    } else {
        words.map { word ->
            curatedMap[word.simplified] ?: ReviewWord(
                hanzi = word.simplified,
                pinyin = word.pinyin,
                meaning = word.meanings.firstOrNull()?.replaceFirstChar { it.uppercase() } ?: word.simplified,
                distractors = listOf("Bạn / Cậu", "Tốt / Ổn", "Tôi / Mình").filter { it != word.meanings.firstOrNull() }.take(3)
            )
        }
    }
    return ReviewSession(
        groupId = nodeVersionId,
        words = reviewWords
    )
}


