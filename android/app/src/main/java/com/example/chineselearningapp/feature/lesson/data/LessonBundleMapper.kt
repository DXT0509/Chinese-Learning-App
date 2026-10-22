package com.example.chineselearningapp.feature.lesson.data

import com.example.chineselearningapp.domain.model.*
import com.google.gson.JsonObject

/** Only finite known contracts are rendered. No storage keys or remote URLs become UI actions. */
object LessonBundleMapper {
    private fun JsonObject.text(key: String): String? = get(key)?.takeIf { it.isJsonPrimitive && it.asJsonPrimitive.isString }?.asString?.takeIf { it.isNotBlank() }
    private fun JsonObject.obj(key: String) = get(key)?.takeIf { it.isJsonObject }?.asJsonObject ?: JsonObject()
    private fun JsonObject.objects(key: String) = get(key)?.takeIf { it.isJsonArray }?.asJsonArray?.filter { it.isJsonObject }?.map { it.asJsonObject }.orEmpty()
    private fun JsonObject.strings(key: String) = get(key)?.takeIf { it.isJsonArray }?.asJsonArray?.filter { it.isJsonPrimitive && it.asJsonPrimitive.isString }?.map { it.asString }.orEmpty()
    private fun JsonObject.number(key: String): Int? = get(key)?.takeIf {
        it.isJsonPrimitive && it.asJsonPrimitive.isNumber
    }?.asString?.toIntOrNull()
    fun map(raw: JsonObject, expectedVersion: String): LessonBundle {
        val lesson = raw.obj("lesson")
        require(lesson.text("version_id") == expectedVersion) { "Bundle version mismatch" }
        val vocabulary = raw.obj("vocabulary")
        val assets = raw.objects("assets").associateBy { it.text("id") }
        fun asset(id: String?, prefix: String) = id?.takeIf { assets[it]?.text("media_type")?.startsWith(prefix) == true }
        val word = Word(vocabulary.text("simplified"), vocabulary.text("pinyin"), vocabulary.text("sino_vietnamese"),
            vocabulary.text("vietnamese_meaning"), vocabulary.text("part_of_speech"), vocabulary.text("notes"),
            asset(vocabulary.text("audio_asset_id"), "audio/"))
        val characters = raw.objects("characters").associateBy { it.text("id") }
        val pages = raw.objects("occurrences").sortedBy { it.number("position") ?: 0 }.map { occurrence ->
            val character = characters[occurrence.text("character_id")] ?: JsonObject()
            CharacterPage(character.text("hanzi"), character.number("stroke_count"),
                if (character.text("analysis_status") == "REVIEWED") character.strings("components") else emptyList(),
                asset(character.text("stroke_order_asset_id"), "image/"))
        }
        val keys = mutableSetOf<String>()
        val scenes = raw.objects("scenes").sortedBy { it.number("position") ?: 0 }.mapIndexed { index, scene ->
            val key = scene.text("scene_key") ?: "missing-$index"
            val config = scene.obj("config")
            val valid = raw.number("schema_version") == 1 && lesson.text("lesson_type") == "VOCABULARY" &&
                scene.number("contract_version") == 1 && config.obj("vocabulary_ref").text("id") == vocabulary.text("id") &&
                config.obj("vocabulary_ref").text("kind") == "VOCABULARY" && keys.add(key) && !key.startsWith("missing-")
            val content = if (!valid) SceneContent.Unsupported else when (scene.text("scene_type")) {
                "VOCABULARY_INTRODUCTION" -> SceneContent.Introduction(word, config.get("show_meaning")?.let { it.isJsonPrimitive && it.asJsonPrimitive.isBoolean && it.asBoolean } ?: true)
                "VOCABULARY_INFORMATION" -> SceneContent.Information(word, config.strings("fields").toSet())
                "CHARACTER_ANALYSIS" -> SceneContent.Analysis(
                    if (config.text("pagination") == "ONE_COMPONENT_PER_PAGE") pages.flatMap { character ->
                        if (character.components.isEmpty()) listOf(character)
                        else character.components.map { component -> character.copy(components = listOf(component)) }
                    } else pages)
                "STROKE_ANIMATION" -> SceneContent.Stroke(pages)
                "HANDWRITING_PRACTICE" -> SceneContent.Handwriting(word.hanzi)
                else -> SceneContent.Unsupported
            }
            LessonScene(key, content)
        }
        return LessonBundle(expectedVersion, lesson.text("title").orEmpty(), scenes)
    }
}
