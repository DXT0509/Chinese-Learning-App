package com.example.chineselearningapp

import com.example.chineselearningapp.feature.review.posLabel
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotEquals
import org.junit.Test

class ReviewGrammarLabelsTest {
    @Test fun everyContextualClassificationHasALocalizedChoiceAndFeedbackLabel() {
        val codes = listOf("subject", "predicate", "object", "attribute", "adverbial",
            "complement", "modal_modifier", "independent_clause", "greeting", "farewell",
            "gratitude", "apology", "wish", "bound_morpheme", "independent_word", "quantity_phrase")
        val labels = codes.map(::posLabel)
        assertEquals(codes.size, labels.toSet().size)
        labels.forEach { assertNotEquals(R.string.srs_pos_unknown, it) }
        assertEquals(R.string.srs_pos_noun, posLabel("noun"))
        assertEquals(R.string.srs_pos_verb, posLabel("verb"))
    }
}
