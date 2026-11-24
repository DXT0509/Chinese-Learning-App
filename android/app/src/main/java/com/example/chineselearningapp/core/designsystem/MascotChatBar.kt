package com.example.chineselearningapp.core.designsystem

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier

/** Shared learning companion. The avatar is the Tiger Mascot; the message carries its meaning. */
@Composable
fun MascotChatBar(message: String, modifier: Modifier = Modifier) {
    TigerMascot(message = message, modifier = modifier)
}
