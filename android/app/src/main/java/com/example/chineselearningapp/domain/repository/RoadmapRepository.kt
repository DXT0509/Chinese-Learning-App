package com.example.chineselearningapp.domain.repository

import com.example.chineselearningapp.domain.model.*

interface RoadmapRepository {
    suspend fun catalog(offset: Int = 0): RoadmapCatalog
    suspend fun nodes(roadmap: Roadmap, after: Int = -1): RoadmapPage
    suspend fun lesson(nodeVersionId: String): RoadmapLesson
    suspend fun start(nodeVersionId: String, replayKey: String? = null): RoadmapRun
    suspend fun submit(runId: String, evidence: RoadmapEvidence): Boolean
    suspend fun complete(runId: String): RoadmapCompletion
    suspend fun skip(nodeVersionId: String): RoadmapCompletion
    suspend fun media(nodeVersionId: String, assetId: String): RoadmapMedia
}
