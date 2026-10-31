package com.example.chineselearningapp

import com.example.chineselearningapp.domain.repository.*

/** Synthetic geometry for ViewModel transport/recovery tests; recognition is tested separately. */
internal fun sampleReviewInk() = ReviewInkEvidence(characters = listOf(
    ReviewInkCharacter(listOf(listOf(ReviewInkPoint(1f, 1f, 0), ReviewInkPoint(5f, 5f, 10))),
        listOf("学"), "学")))
