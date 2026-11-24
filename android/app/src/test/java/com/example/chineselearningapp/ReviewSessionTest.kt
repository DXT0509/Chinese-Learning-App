package com.example.chineselearningapp

import androidx.lifecycle.SavedStateHandle
import com.example.chineselearningapp.domain.model.*
import com.example.chineselearningapp.feature.roadmap.LessonStep
import com.example.chineselearningapp.feature.roadmap.LessonViewModel
import com.example.chineselearningapp.feature.roadmap.ReviewSessionData
import com.example.chineselearningapp.feature.roadmap.toReviewSession
import org.junit.Assert.*
import org.junit.Test

class ReviewSessionTest {

    @Test
    fun testReviewSessionModelAndSeedData() {
        val session = ReviewSessionData.HSK0_TOI_BAN_TOT
        assertEquals("hsk0-toi-ban-tot", session.groupId)
        assertEquals(5, session.words.size)

        val word1 = session.words[0]
        assertEquals("我", word1.hanzi)
        assertEquals("wǒ", word1.pinyin)
        assertEquals("Tôi / Mình", word1.meaning)
        assertEquals(listOf("Bạn / Cậu", "Tốt / Ổn", "Không"), word1.distractors)

        val word2 = session.words[1]
        assertEquals("你", word2.hanzi)
        assertEquals("nǐ", word2.pinyin)
        assertEquals("Bạn / Cậu", word2.meaning)
        assertEquals(listOf("Tôi / Mình", "Anh ấy", "Tốt / Ổn"), word2.distractors)

        val word3 = session.words[2]
        assertEquals("好", word3.hanzi)
        assertEquals("hǎo", word3.pinyin)
        assertEquals("Tốt / Ổn", word3.meaning)
        assertEquals(listOf("Xấu / Tệ", "Tôi / Mình", "Có"), word3.distractors)

        val word4 = session.words[3]
        assertEquals("不", word4.hanzi)
        assertEquals("bù", word4.pinyin)
        assertEquals("Không / Chẳng", word4.meaning)
        assertEquals(listOf("Có", "Tốt / Ổn", "Rất"), word4.distractors)

        val word5 = session.words[4]
        assertEquals("很", word5.hanzi)
        assertEquals("hěn", word5.pinyin)
        assertEquals("Rất / Lắm", word5.meaning)
        assertEquals(listOf("Không", "Ít", "Bạn / Cậu"), word5.distractors)

        assertEquals(session, ReviewSessionData.getByGroupId("hsk0-toi-ban-tot"))
        assertNull(ReviewSessionData.getByGroupId("unknown-group"))
    }

    @Test
    fun testReviewXpFormula() {
        // baseXP = 50
        // finalXP = 50 * max(0.1, 1 - mistakeCount * 0.1)

        // 0 mistakes: 50 * max(0.1, 1.0) = 50
        assertEquals(50, calculateReviewXp(mistakeCount = 0, baseXP = 50))

        // 1 mistake: 50 * max(0.1, 0.9) = 45
        assertEquals(45, calculateReviewXp(mistakeCount = 1, baseXP = 50))

        // 2 mistakes: 50 * max(0.1, 0.8) = 40
        assertEquals(40, calculateReviewXp(mistakeCount = 2, baseXP = 50))

        // 5 mistakes: 50 * max(0.1, 0.5) = 25
        assertEquals(25, calculateReviewXp(mistakeCount = 5, baseXP = 50))

        // 9 mistakes: 50 * max(0.1, 0.1) = 5
        assertEquals(5, calculateReviewXp(mistakeCount = 9, baseXP = 50))

        // 10 mistakes: 50 * max(0.1, 0.0) = 50 * 0.1 = 5 (floor at 0.1)
        assertEquals(5, calculateReviewXp(mistakeCount = 10, baseXP = 50))

        // 15 mistakes: floor at 0.1 = 5
        assertEquals(5, calculateReviewXp(mistakeCount = 15, baseXP = 50))
    }

    @Test
    fun testLessonViewModelResetReviewSessionAndCumulativeMistakes() {
        val saved = SavedStateHandle()
        val vm = LessonViewModel(saved)

        // Make mistakes in prior lesson
        vm.recordAnswer(false)
        vm.recordAnswer(false)
        assertEquals(2, vm.mistakeCount)
        assertEquals(80, vm.lessonScore)

        // Start new ReviewSession -> mistakeCount re-initialized to 0
        vm.resetReviewSession()
        assertEquals(0, vm.mistakeCount)
        assertEquals(100, vm.lessonScore)
        assertEquals(LessonStep.MultipleChoice, vm.state.value.step)
        assertEquals(50, vm.calculateReviewXp(50))

        // Word 1: 1 mistake in MultipleChoice
        vm.recordAnswer(false)
        assertEquals(1, vm.mistakeCount)
        assertEquals(90, vm.lessonScore)

        // Word 1: correct in Writing
        vm.recordAnswer(true)
        assertEquals(1, vm.mistakeCount)
        assertEquals(90, vm.lessonScore)

        // Move to next review word
        vm.nextReviewWord()
        // Cumulative mistake count is preserved across words in the session
        assertEquals(1, vm.mistakeCount)
        assertEquals(90, vm.lessonScore)
        assertEquals(LessonStep.MultipleChoice, vm.state.value.step)

        // Word 2: speech skip counts as mistake
        vm.skipSpeech()
        assertEquals(2, vm.mistakeCount)
        assertEquals(80, vm.lessonScore)

        // Final XP with 2 mistakes
        assertEquals(40, vm.calculateReviewXp(50))
    }

    @Test
    fun testToReviewSessionWithThreeWordsWoNiHao() {
        val unavailable = LessonEnrichment("UNAVAILABLE", null, null)
        val roadmapLesson = RoadmapLesson(
            nodeVersionId = "hsk0-review-node-id",
            lessonVersionId = "hsk0-review-lesson-id",
            type = "REVIEW",
            title = "Ôn tập",
            words = listOf(
                RoadmapWord("id-1", 1, "我", "wǒ", listOf("tôi", "mình"), "ngã"),
                RoadmapWord("id-2", 1, "你", "nǐ", listOf("bạn", "cậu"), "nhĩ"),
                RoadmapWord("id-3", 1, "好", "hǎo", listOf("tốt", "ổn"), "hảo")
            ),
            activities = emptyList(),
            audio = unavailable,
            examples = unavailable,
            notes = unavailable,
            strokeOrder = unavailable,
            components = emptyList()
        )

        val session = roadmapLesson.toReviewSession()
        assertEquals("hsk0-review-node-id", session.groupId)
        assertEquals(3, session.words.size)

        // Word 1: 我
        val w1 = session.words[0]
        assertEquals("我", w1.hanzi)
        assertEquals("wǒ", w1.pinyin)
        assertEquals("Tôi / Mình", w1.meaning)
        assertEquals(listOf("Bạn / Cậu", "Tốt / Ổn", "Không"), w1.distractors)

        // Word 2: 你
        val w2 = session.words[1]
        assertEquals("你", w2.hanzi)
        assertEquals("nǐ", w2.pinyin)
        assertEquals("Bạn / Cậu", w2.meaning)
        assertEquals(listOf("Tôi / Mình", "Anh ấy", "Tốt / Ổn"), w2.distractors)

        // Word 3: 好
        val w3 = session.words[2]
        assertEquals("好", w3.hanzi)
        assertEquals("hǎo", w3.pinyin)
        assertEquals("Tốt / Ổn", w3.meaning)
        assertEquals(listOf("Xấu / Tệ", "Tôi / Mình", "Có"), w3.distractors)
    }
}


