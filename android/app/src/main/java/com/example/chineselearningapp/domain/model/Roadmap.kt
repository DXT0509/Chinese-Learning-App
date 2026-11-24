package com.example.chineselearningapp.domain.model

data class Roadmap(val id: String, val versionId: String, val title: String)
data class RoadmapCatalog(val items: List<Roadmap>, val nextOffset: Int?)
data class RoadmapNode(val id: String, val versionId: String, val position: Int,
    val type: String, val title: String, val section: String, val status: String, val available: Boolean) {
    val canOpen get() = available || status in setOf("COMPLETED", "SKIPPED")
}
data class RoadmapPage(val versionId: String, val items: List<RoadmapNode>, val nextPosition: Int?,
    val currentPosition: Int?, val sections: Map<String, Int>)
data class LessonEnrichment(val status: String, val text: String?, val assetId: String?) {
    val available get() = status == "AVAILABLE"
}
data class LessonComponent(val position: Int, val component: String, val role: String, val explanation: LessonEnrichment)
data class RoadmapActivity(val id: String, val kind: String, val required: Boolean, val prompt: String,
    val repetitions: Int, val options: List<String>)
data class RoadmapWord(val id: String, val contentVersion: Int, val simplified: String, val pinyin: String,
    val meanings: List<String>, val sinoVietnamese: String?, val examples: List<RoadmapExample> = emptyList())

data class RoadmapExample(val simplified: String, val pinyin: String, val vietnamese: String)
data class RoadmapLesson(val nodeVersionId: String, val lessonVersionId: String, val type: String, val title: String,
    val words: List<RoadmapWord>, val activities: List<RoadmapActivity>, val audio: LessonEnrichment,
    val examples: LessonEnrichment, val notes: LessonEnrichment, val strokeOrder: LessonEnrichment,
    val components: List<LessonComponent>, val exercises: LessonExercisesConfig? = null)
data class RoadmapRun(val id: String, val nodeVersionId: String, val replay: Boolean, val completed: Boolean,
    val accepted: Map<String, Set<Int>>)
data class RoadmapPoint(val x: Float, val y: Float)
data class RoadmapEvidence(val requestId: String, val activityId: String, val kind: String, val repetition: Int,
    val choice: Int? = null, val strokes: List<List<RoadmapPoint>> = emptyList(), val durationMs: Int = 0)
data class RoadmapCompletion(val status: String, val exp: Int)
data class RoadmapMedia(val bytes: ByteArray, val mediaType: String)
