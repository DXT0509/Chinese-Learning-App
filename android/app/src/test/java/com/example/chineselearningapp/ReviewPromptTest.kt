package com.example.chineselearningapp

import com.example.chineselearningapp.feature.review.learnerPrompt
import org.junit.Assert.*
import org.junit.Test

class ReviewPromptTest {
    @Test fun shortMeaningKeepsRequiredPolicyCues() {
        val result = learnerPrompt("Viết từ đã học có âm Hán-Việt «mã» (1 chữ Hán). Nghĩa trong danh mục: con ngựa; ngựa; con ngựa.")
        assertEquals("con ngựa", result.meaning)
        assertEquals("Hán-Việt: mã · 1 chữ", result.cue)
    }
    @Test fun editorialSenseAndUnrelatedMeaningsArePreserved() {
        val editorial = "Chỉ ngân hàng, không phải bờ sông."
        assertEquals(editorial, learnerPrompt(editorial).meaning)
        val result = learnerPrompt("Viết mục từ đã học (1 chữ Hán). Nghĩa trong danh mục: nước; đất nước. Ngữ cảnh minh họa: Trong nước. Ở bước từ loại, chọn tất cả từ loại của mục từ này trong danh mục.")
        assertEquals("nước; đất nước", result.meaning)
        assertTrue(result.cue!!.contains("Trong nước."))
    }
}
