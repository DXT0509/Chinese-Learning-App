package com.example.chineselearningapp

import com.example.chineselearningapp.domain.model.*
import com.example.chineselearningapp.feature.lesson.data.LessonBundleMapper
import com.google.gson.JsonParser
import org.junit.Assert.*
import org.junit.Test

class LessonBundleMapperTest {
    private fun bundle(type: String, config: String = "", contract: Int = 1) = JsonParser.parseString("""{
        "schema_version":1, "lesson":{"version_id":"pinned","lesson_type":"VOCABULARY","title":"Ni"},
        "vocabulary":{"id":"word","simplified":"ni","pinyin":"ni","vietnamese_meaning":"ban"},
        "scenes":[{"scene_key":"scene","position":10,"scene_type":"$type","contract_version":$contract,
          "config":{"vocabulary_ref":{"kind":"VOCABULARY","id":"word"}$config}}]
    }""").asJsonObject
    @Test fun mapsAllFiveSceneContracts() {
        val types = mapOf("VOCABULARY_INTRODUCTION" to SceneContent.Introduction::class.java,
            "VOCABULARY_INFORMATION" to SceneContent.Information::class.java,
            "CHARACTER_ANALYSIS" to SceneContent.Analysis::class.java,
            "STROKE_ANIMATION" to SceneContent.Stroke::class.java,
            "HANDWRITING_PRACTICE" to SceneContent.Handwriting::class.java)
        types.forEach { (type, expected) -> assertEquals(expected, LessonBundleMapper.map(bundle(type), "pinned").scenes.single().content.javaClass) }
    }
    @Test fun meaningVisibilityAndMissingFieldsAreRespected() {
        val intro = LessonBundleMapper.map(bundle("VOCABULARY_INTRODUCTION", """, "show_meaning":false"""), "pinned").scenes.single().content as SceneContent.Introduction
        assertFalse(intro.showMeaning)
        assertNull(intro.word.reading)
        assertNull(intro.word.audioId)
    }
    @Test fun unsupportedTypesAndContractVersionsAreSafe() {
        listOf("LISTENING_TRANSCRIPTION", "SENTENCE_TRANSLATION", "UNKNOWN").forEach {
            assertEquals(SceneContent.Unsupported, LessonBundleMapper.map(bundle(it), "pinned").scenes.single().content)
        }
        assertEquals(SceneContent.Unsupported, LessonBundleMapper.map(bundle("VOCABULARY_INFORMATION", contract = 2), "pinned").scenes.single().content)
    }
    @Test fun missingAnalysisIsEmptyAndMalformedFieldsDoNotCrash() {
        val raw = bundle("CHARACTER_ANALYSIS")
        raw.add("occurrences", JsonParser.parseString("""[{"position":0,"character_id":"missing"}]"""))
        val analysis = LessonBundleMapper.map(raw, "pinned").scenes.single().content as SceneContent.Analysis
        assertEquals(1, analysis.characters.size)
        assertTrue(analysis.characters.single().components.isEmpty())
        assertNull(analysis.characters.single().hanzi)
    }
    @Test fun reviewedComponentsCanUseOneComponentPerPage() {
        val raw = bundle("CHARACTER_ANALYSIS", ", \"pagination\":\"ONE_COMPONENT_PER_PAGE\"")
        raw.add("occurrences", JsonParser.parseString("""[{"position":0,"character_id":"c"}]"""))
        raw.add("characters", JsonParser.parseString("""[{"id":"c","hanzi":"ni","analysis_status":"REVIEWED","components":["left","right"]}]"""))
        val pages = (LessonBundleMapper.map(raw, "pinned").scenes.single().content as SceneContent.Analysis).characters
        assertEquals(listOf("left", "right"), pages.flatMap { it.components })
        assertEquals(2, pages.size)
    }
    @Test(expected = IllegalArgumentException::class) fun rejectsWrongPinnedBundle() {
        LessonBundleMapper.map(bundle("VOCABULARY_INFORMATION"), "different-version")
    }
}
