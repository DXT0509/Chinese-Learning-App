package com.example.chineselearningapp.core.designsystem

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxScope
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.LocalContentColor
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.drawWithCache
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import kotlin.math.min

/** Soft aurora washes shared by auth and Home, with no bitmap or offscreen blur layer. */
@Composable
fun AuroraBackground(
    modifier: Modifier = Modifier,
    content: @Composable BoxScope.() -> Unit
) {
    val colors = MaterialTheme.colorScheme
    CompositionLocalProvider(LocalContentColor provides colors.onBackground) {
        Box(
            modifier.fillMaxSize().drawWithCache {
                val shortEdge = min(size.width, size.height).coerceAtLeast(1f)
                val base = Brush.verticalGradient(
                    0f to colors.surface,
                    0.55f to colors.surface,
                    1f to colors.background
                )
                // Transparent edges retain the tint's RGB, avoiding a grey/dark halo.
                // Brushes are cached until the viewport or palette changes.
                val upperGlow = Brush.radialGradient(
                    0f to colors.secondaryContainer.copy(alpha = 0.65f),
                    0.35f to colors.secondaryContainer.copy(alpha = 0.32f),
                    0.7f to colors.secondaryContainer.copy(alpha = 0.09f),
                    1f to colors.secondaryContainer.copy(alpha = 0f),
                    center = Offset(size.width * 1.05f, size.height * 0.10f),
                    radius = shortEdge * 1.05f
                )
                val leftGlow = Brush.radialGradient(
                    0f to colors.surfaceVariant.copy(alpha = 0.48f),
                    0.45f to colors.surfaceVariant.copy(alpha = 0.18f),
                    1f to colors.surfaceVariant.copy(alpha = 0f),
                    center = Offset(-size.width * 0.18f, size.height * 0.52f),
                    radius = shortEdge * 0.95f
                )
                val lowerGlow = Brush.radialGradient(
                    0f to colors.secondaryContainer.copy(alpha = 0.60f),
                    0.4f to colors.secondaryContainer.copy(alpha = 0.26f),
                    1f to colors.secondaryContainer.copy(alpha = 0f),
                    center = Offset(size.width * 0.95f, size.height * 0.95f),
                    radius = shortEdge * 1.20f
                )
                val softCenter = Brush.radialGradient(
                    0f to colors.surface.copy(alpha = 0.72f),
                    1f to colors.surface.copy(alpha = 0f),
                    center = Offset(size.width * 0.42f, size.height * 0.36f),
                    radius = shortEdge * 0.85f
                )
                onDrawBehind {
                    drawRect(base)
                    drawRect(upperGlow)
                    drawRect(leftGlow)
                    drawRect(lowerGlow)
                    drawRect(softCenter)
                }
            },
            content = content
        )
    }
}
