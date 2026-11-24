package com.example.chineselearningapp.domain.model

data class LessonBundle(val versionId: String, val title: String, val scenes: List<LessonScene>)
data class LessonScene(val key: String, val content: SceneContent)
data class Word(val hanzi: String?, val pinyin: String?, val reading: String?, val meaning: String?,
    val partOfSpeech: String?, val notes: String?, val audioId: String? = null, val audio: String? = audioId)

data class ListeningQuestion(
    val answerWord: Word,            // từ đúng (có hanzi, pinyin, nghĩa, audio)
    val options: List<Word>,         // ĐÚNG 4 phần tử, đã xáo trộn, có answerWord
    val questionIndex: Int,          // 0-based
    val questionCount: Int           // thường là 2
)
data class CharacterPage(val hanzi: String?, val strokeCount: Int?, val components: List<String>,
    val strokeAssetId: String?)
sealed interface SceneContent {
    data class Introduction(val word: Word, val showMeaning: Boolean) : SceneContent
    data class Information(val word: Word, val fields: Set<String>) : SceneContent
    data class Analysis(val characters: List<CharacterPage>) : SceneContent
    data class Stroke(val characters: List<CharacterPage>) : SceneContent
    data class Handwriting(val hanzi: String?) : SceneContent
    data object Unsupported : SceneContent
}
