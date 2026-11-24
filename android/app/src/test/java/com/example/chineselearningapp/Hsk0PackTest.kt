package com.example.chineselearningapp

import com.example.chineselearningapp.core.network.RoadmapLessonDto
import com.example.chineselearningapp.domain.model.RoadmapEvidence
import com.example.chineselearningapp.feature.roadmap.domain
import com.example.chineselearningapp.feature.roadmap.dto
import com.google.gson.Gson
import org.junit.Assert.*
import org.junit.Test

class Hsk0PackTest {
    private fun payloads(): Array<RoadmapLessonDto> = Gson().fromJson(
        checkNotNull(javaClass.getResourceAsStream("/hsk0-lessons.json")).bufferedReader().use { it.readText() },
        Array<RoadmapLessonDto>::class.java
    )
    @Test fun realPackMapsPinnedWordsAssetsComponentsAndExactReviewScope() {
        val lessons = payloads().map { it.domain() }
        assertEquals(listOf("我", "你", "好"), lessons.take(3).map { it.words.single().simplified })
        assertEquals(listOf("wǒ", "nǐ", "hǎo"), lessons.take(3).map { it.words.single().pinyin })
        assertEquals(listOf("ngã", "nhĩ", "hảo"), lessons.take(3).map { it.words.single().sinoVietnamese })
        assertEquals(22, lessons.sumOf { it.activities.size })
        assertEquals(lessons.take(3).flatMap { it.words }, lessons.last().words)
        lessons.take(3).forEach {
            assertTrue(it.audio.available && it.strokeOrder.available)
            assertTrue(it.components.isNotEmpty() && it.examples.available)
            assertEquals(2, it.activities.single { a -> a.kind == "PRONUNCIATION" }.repetitions)
            assertEquals(2, it.activities.count { a -> a.kind == "QUIZ" })
        }
        assertFalse(lessons.last().activities.first().required)
        assertEquals(3, lessons.last().activities.count { it.required })
    }
    @Test fun learnerFixturesNeverContainAnswerKeysAndChoiceUsesExistingWireShape() {
        val json = checkNotNull(javaClass.getResourceAsStream("/hsk0-lessons.json")).bufferedReader().use { it.readText() }
        assertFalse(json.contains("correct_option"))
        val quiz = payloads().first().domain().activities.first { it.kind == "QUIZ" }
        val body = RoadmapEvidence("request", quiz.id, "CHOICE", 0, choice = 1).dto()
        assertEquals(quiz.id, body.activityId); assertEquals(1, body.choice); assertTrue(body.strokes.isEmpty())
    }
}
