package com.example.chineselearningapp.feature.review

import androidx.compose.runtime.Composable
import com.example.chineselearningapp.R
import com.example.chineselearningapp.core.designsystem.*

@Composable
fun ReviewScreen() {
    PageColumn { FeatureEmptyState(R.string.review, R.string.review_empty, R.drawable.ic_review) }
}
