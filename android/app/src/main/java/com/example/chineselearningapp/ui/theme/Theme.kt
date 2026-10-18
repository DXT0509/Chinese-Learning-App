package com.example.chineselearningapp.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.Shapes
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp

private val DarkColorScheme = darkColorScheme(
    primary = NightPrimary,
    onPrimary = Color(0xFF00391C),
    primaryContainer = NightContainer,
    onPrimaryContainer = Color(0xFFC3F5D3),
    secondary = Color(0xFFB0D0BB),
    secondaryContainer = NightContainer,
    onSecondaryContainer = NightText,
    tertiary = FreshGreen,
    background = NightBackground,
    onBackground = NightText,
    surface = NightSurface,
    onSurface = NightText,
    surfaceVariant = Color(0xFF293D30),
    onSurfaceVariant = Color(0xFFBDD0C2),
    outline = Color(0xFF8CA393),
    outlineVariant = Color(0xFF3E5547)
)

private val LightColorScheme = lightColorScheme(
    primary = ForestGreen,
    onPrimary = WhiteSurface,
    primaryContainer = MintMist,
    onPrimaryContainer = InkGreen,
    secondary = MutedGreen,
    secondaryContainer = SoftMint,
    onSecondaryContainer = InkGreen,
    tertiary = FreshGreen,
    background = MintBackground,
    onBackground = InkGreen,
    surface = WhiteSurface,
    onSurface = InkGreen,
    surfaceVariant = MintContainer,
    onSurfaceVariant = MutedGreen,
    outline = Color(0xFF738A7B),
    outlineVariant = Color(0xFFC4DCCD)
)

@Composable
fun ChineseLearningAppTheme(
    // The white/mint aurora is the app's default appearance, also on night-mode devices.
    // Explicit dark previews remain available without changing the device's settings.
    darkTheme: Boolean = false,
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        shapes = Shapes(
            small = RoundedCornerShape(12.dp), medium = RoundedCornerShape(20.dp),
            large = RoundedCornerShape(28.dp), extraLarge = RoundedCornerShape(32.dp)
        ),
        content = content
    )
}
