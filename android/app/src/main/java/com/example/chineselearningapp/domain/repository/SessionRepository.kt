package com.example.chineselearningapp.domain.repository

data class Account(val id: String, val email: String?, val displayName: String = "")
data class CatalogLesson(val versionId: String, val title: String, val version: Int = 1)
data class PreviewRun(val id: String, val versionId: String, val checkpoints: Map<String, Int>)
data class PreviewScene(val key: String, val page: Int)

interface SessionRepository {
    suspend fun authenticate(email: String, password: String, register: Boolean)
    suspend fun account(): Account?
    suspend fun logout()
    suspend fun catalog(): List<CatalogLesson>
    suspend fun runs(): List<PreviewRun>
    suspend fun start(versionId: String, requestId: String): PreviewRun
    suspend fun resume(runId: String): PreviewRun
    suspend fun scenes(versionId: String): List<PreviewScene>
    suspend fun checkpoint(runId: String, sceneKey: String, page: Int): PreviewRun
}
