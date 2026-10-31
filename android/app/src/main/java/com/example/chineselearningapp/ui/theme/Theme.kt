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
    primary = com.example.chineselearningapp.core.designsystem.Primary,
    onPrimary = com.example.chineselearningapp.core.designsystem.Surface2,
    primaryContainer = com.example.chineselearningapp.core.designsystem.PrimaryLight,
    onPrimaryContainer = com.example.chineselearningapp.core.designsystem.PrimaryDark,
    secondary = com.example.chineselearningapp.core.designsystem.TextSecondary,
    secondaryContainer = com.example.chineselearningapp.core.designsystem.PrimaryMuted,
    onSecondaryContainer = com.example.chineselearningapp.core.designsystem.PrimaryDark,
    tertiary = com.example.chineselearningapp.core.designsystem.Primary,
    background = com.example.chineselearningapp.core.designsystem.Surface0,
    onBackground = com.example.chineselearningapp.core.designsystem.TextPrimary,
    surface = com.example.chineselearningapp.core.designsystem.Surface2,
    onSurface = com.example.chineselearningapp.core.designsystem.TextPrimary,
    surfaceVariant = com.example.chineselearningapp.core.designsystem.Surface1,
    onSurfaceVariant = com.example.chineselearningapp.core.designsystem.TextSecondary,
    outline = com.example.chineselearningapp.core.designsystem.Border,
    outlineVariant = com.example.chineselearningapp.core.designsystem.BorderStrong
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
