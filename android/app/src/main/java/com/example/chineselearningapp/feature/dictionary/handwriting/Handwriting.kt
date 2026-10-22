package com.example.chineselearningapp.feature.dictionary.handwriting

data class HandwritingPoint(val x: Float, val y: Float, val timeMillis: Long)
data class HandwritingStroke(val points: List<HandwritingPoint>) {
    val isValid: Boolean get() = points.isNotEmpty() && points.all { it.x.isFinite() && it.y.isFinite() } &&
        points.zipWithNext().all { (a, b) -> a.timeMillis <= b.timeMillis }
}

/** Owns the in-progress gesture locally; only completed immutable snapshots leave the canvas. */
class StrokeCollector {
    private val points = mutableListOf<HandwritingPoint>()
    fun start(point: HandwritingPoint) { points.clear(); points.add(point) }
    fun move(point: HandwritingPoint) { if (points.isNotEmpty()) points.add(point) }
    fun cancel() { points.clear() }
    fun finish(point: HandwritingPoint): HandwritingStroke? {
        if (points.isEmpty()) return null
        points.add(point)
        val stroke = HandwritingStroke(points.toList())
        cancel()
        return stroke.takeIf { it.isValid }
    }
}

interface HandwritingRecognizer : AutoCloseable {
    suspend fun prepareModel(onDownload: () -> Unit)
    suspend fun recognize(strokes: List<HandwritingStroke>): List<String>
}

/** Keep complete ranked Han strings, including multi-character results; never truncate UTF-16. */
fun handwritingCandidates(results: List<String>): List<String> = results.filter { text ->
    text.isNotEmpty() && text.codePoints().allMatch { Character.UnicodeScript.of(it) == Character.UnicodeScript.HAN }
}.distinct().take(10)
