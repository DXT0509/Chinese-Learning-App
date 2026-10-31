package com.example.chineselearningapp.feature.review

internal data class LearnerPrompt(val meaning: String, val cue: String? = null)

/** Only shorten known generated templates; preserve editorial prompts verbatim. */
internal fun learnerPrompt(prompt: String): LearnerPrompt {
    val marker = "Nghĩa trong danh mục: "
    val generated = prompt.startsWith("Viết từ đã học có âm Hán-Việt «") ||
        prompt.startsWith("Viết mục từ đã học (")
    if (!generated || marker !in prompt) return LearnerPrompt(prompt)
    val prefix = prompt.substringBefore(marker)
    val rest = prompt.substringAfter(marker)
        .removeSuffix("Ở bước từ loại, chọn tất cả từ loại của mục từ này trong danh mục.").trim()
    val glosses = rest.substringBefore("Ngữ cảnh minh họa:").trim().trimEnd('.')
        .split(';').map { it.trim() }.filter { it.isNotEmpty() }.distinctBy { it.lowercase() }
    if (glosses.isEmpty()) return LearnerPrompt(prompt)
    val meanings = glosses.filter { short -> glosses.none { long -> long != short && long.equals("con $short", ignoreCase = true) } }
    val sino = Regex("«([^»]+)»").find(prefix)?.groupValues?.get(1)
    val count = Regex("\\((\\d+) chữ Hán\\)").find(prefix)?.groupValues?.get(1)
    // These cues are part of the installed grading policy, not optional decorations.
    val cues = listOfNotNull(sino?.let { "Hán-Việt: $it" }, count?.let { "$it chữ" },
        rest.takeIf { "Ngữ cảnh minh họa:" in it }?.substringAfter("Ngữ cảnh minh họa:")?.trim())
    return LearnerPrompt(meanings.joinToString("; "), cues.joinToString(" · ").ifEmpty { null })
}
