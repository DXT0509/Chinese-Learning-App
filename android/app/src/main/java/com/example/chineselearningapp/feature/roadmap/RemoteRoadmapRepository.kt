package com.example.chineselearningapp.feature.roadmap

import com.example.chineselearningapp.core.network.*
import com.example.chineselearningapp.domain.model.*
import com.example.chineselearningapp.domain.repository.RoadmapRepository
import com.example.chineselearningapp.feature.auth.data.RemoteSessionRepository
import javax.inject.Inject

class RemoteRoadmapRepository @Inject constructor(private val api: RoadmapApi,
    private val session: RemoteSessionRepository) : RoadmapRepository {
    // Owned by the protected graph, never a singleton cache of learner progress.
    override suspend fun catalog(offset: Int) = session.authorized { api.catalog(it, offset) }.let { page ->
        RoadmapCatalog(page.items.map { Roadmap(it.id, it.versionId, it.title) }, page.nextOffset)
    }
    override suspend fun nodes(roadmap: Roadmap, after: Int) = session.authorized {
        api.nodes(it, roadmap.id, roadmap.versionId, after)
    }.let { page -> RoadmapPage(page.versionId, page.items.map {
        RoadmapNode(it.id, it.versionId, it.position, it.type, it.title, it.section, it.status, it.available)
    }, page.nextPosition, page.currentPosition, page.sections.orEmpty()) }
    override suspend fun lesson(nodeVersionId: String) = session.authorized { api.lesson(it, nodeVersionId) }.domain()
    override suspend fun start(nodeVersionId: String, replayKey: String?) = session.authorized {
        api.start(it, nodeVersionId, RoadmapStartDto(replayKey != null, replayKey))
    }.let { RoadmapRun(it.id, it.nodeVersionId, it.replay, it.completedAt != null,
        it.accepted.orEmpty().mapValues { entry -> entry.value.toSet() }) }
    override suspend fun submit(runId: String, evidence: RoadmapEvidence) = session.authorized {
        api.submit(it, runId, evidence.dto())
    }.accepted
    override suspend fun complete(runId: String) = session.authorized { api.complete(it, runId) }.let { RoadmapCompletion(it.status, it.exp) }
    override suspend fun skip(nodeVersionId: String) = session.authorized { api.skip(it, nodeVersionId) }.let { RoadmapCompletion(it.status, it.exp) }
    override suspend fun media(nodeVersionId: String, assetId: String) = session.authorized { api.media(it, nodeVersionId, assetId).use { body ->
        require(body.contentLength() <= 16 * 1024 * 1024) // Bounded published assets; streaming limit below handles unknown length.
        val bytes = body.byteStream().readNBytesCompat(16 * 1024 * 1024)
        RoadmapMedia(bytes, body.contentType()?.toString().orEmpty())
    } }
}
private fun java.io.InputStream.readNBytesCompat(limit: Int): ByteArray {
    val output = java.io.ByteArrayOutputStream()
    val buffer = ByteArray(8192)
    while (true) {
        val count = read(buffer)
        if (count < 0) break
        require(output.size() + count <= limit)
        output.write(buffer, 0, count)
    }
    return output.toByteArray()
}
fun RoadmapEvidence.dto() = RoadmapEvidenceDto(requestId, activityId, kind, repetition, choice,
    strokes.map { stroke -> stroke.map { RoadmapPointDto(it.x, it.y) } }, durationMs)
fun RoadmapLessonDto.domain(): RoadmapLesson {
    val content = definition.lesson
    require(definition.type != "NEW_WORD" || vocabulary.size == 1)
    return RoadmapLesson(nodeVersionId, lessonVersionId, definition.type, definition.title,
        vocabulary.map { word -> RoadmapWord(word.id, word.version, word.simplified, word.pinyin, word.meanings, word.sinoVietnamese,
            word.examples.orEmpty().map { RoadmapExample(it.simplified, it.pinyin, it.vietnamese) }) },
        content.activities.map { RoadmapActivity(it.id, it.kind, it.required, it.prompt, it.repetitions, it.options) },
        content.audio.domain(), content.examples.domain(), content.notes.domain(), content.strokeOrder.domain(),
        content.components.map { LessonComponent(it.position, it.component, it.role, it.explanation.domain()) },
        content.exercises?.domain())
}
private fun LessonExercisesDto.domain(): LessonExercisesConfig {
    return LessonExercisesConfig(
        listening = listening?.let { l ->
            ListeningExerciseConfig(
                items = l.items.orEmpty().map { ExerciseItemConfig(it.answer, it.distractors.orEmpty()) },
                skipSecond = l.skipSecond
            )
        },
        skipSecond = skipSecond
    )
}
private fun RoadmapEnrichmentDto.domain() = LessonEnrichment(status, text.takeIf { status == "AVAILABLE" }, assetId.takeIf { status == "AVAILABLE" })
