package com.example.chineselearningapp.core.designsystem

import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

// ==========================================
// 1. DESIGN TOKENS
// ==========================================

// --- Colors ---
val Primary = Color(0xFF1A7A4A)        // Xanh lá chính — nút CTA, active state, link
val PrimaryDark = Color(0xFF0F5533)    // Gradient dark end, hero card
val PrimaryLight = Color(0xFFF0FAF4)   // Background tint nhẹ
val PrimaryMuted = Color(0xFFE8F5EE)   // Chip selected background

val Surface0 = Color(0xFFF4F4F2)       // Page background
val Surface1 = Color(0xFFF9F9F7)       // Card / input background
val Surface2 = Color(0xFFFFFFFF)       // Elevated card

val TextPrimary = Color(0xFF1A1A18)
val TextSecondary = Color(0xFF5F5E5A)
val TextMuted = Color(0xFFA0A09A)
val Border = Color(0x14000000)          // rgba(0, 0, 0, 0.08)
val BorderStrong = Color(0x24000000)    // rgba(0, 0, 0, 0.14)

// --- Lesson Redesign & Scene Tokens ---
val LessonBorder = Color(0xFFD6E9DE)
val LessonShadow = Color(0xFFC8E0D2)
val ProgressGradientStart = Color(0xFF34C478)
val ProgressGradientEnd = Color(0xFF1A7A4A) // Primary
val LessonVolumeBg = Color(0xFFF4FAF6)
val DangerColor = Color(0xFFA32D2D)
val DangerBorder = Color(0xFFF0BCBC)
val DangerBg = Color(0xFFFDECEC)
val SealBorder = Color(0xFFE8A5A5)
val PinyinBg = Color(0xFFE8F5EE)
val PinyinBorder = Color(0xFFB9DFC9)
val NewWordChipBg = Color(0xFFFFF3CC)
val NewWordChipBorder = Color(0xFFF5D27A)
val NewWordChipText = Color(0xFF8A5A00)
val TianZiGeGrid = Color(0xFFCFE5D8)
val MeaningLabel = Color(0xFF7A9A88)
val ScreenGradientTop = Color(0xFFE3F4EA)
val ScreenGradientMid = Color(0xFFF4FAF6)

// --- Writing Redesign Tokens ---
val SuccessStrokeColor = Color(0xFF1A9A58)
val SuccessBannerBg = Color(0xFFDFF5E8)
val DangerBannerBg = Color(0xFFFDE8E8)
val DangerButtonBg = Color(0xFFD63C42)
val DangerCardShadow = Color(0xFFF0A8A8)
val InactiveStrokeColor = Color(0xFFE3E8E5)
val DemoGridColor = Color(0xFFD9EBE0)
val ToolbarTextColor = Color(0xFF5F7A6B)
val SubtitleCaptionColor = Color(0xFF7A9A88)
val CorrectGlowColor = Color(0xFF34C478)
val ErrorColor = Color(0xFFE5484D)
val PinyinPlaceholder = Color(0xFFA9BDB0)
val PinyinErrorText = Color(0xFFC0353A)

// --- Pronunciation & Speaking Redesign Tokens ---
val PronunChipBg = Color(0xFFFDE8F3)
val PronunChipBorder = Color(0xFFF0B6D6)
val PronunChipText = Color(0xFFA0286A)
val MicListeningStart = Color(0xFFFF8A8A)
val MicListeningEnd = Color(0xFFE5484D)
val MicProcessingStart = Color(0xFF8FD4FF)
val MicProcessingEnd = Color(0xFF2B84F0)
val MicProcessingShadow = Color(0xFF124A99)
val PronunNoteText = Color(0xFF8AA597)

// --- Scene 2 Structure Tokens ---
val StructureChipBg = Color(0xFFE8F0FF)
val StructureChipBorder = Color(0xFFB9C9F0)
val StructureChipText = Color(0xFF2B4A9A)

val SemanticBg = Color(0xFFFFF3CC)
val SemanticBorder = Color(0xFFF5D27A)
val SemanticText = Color(0xFF7A4A00)

val ComponentTagBg = Color(0xFFE8F0FF)
val ComponentTagBorder = Color(0xFFB9C9F0)
val ComponentTagText = Color(0xFF2B4A9A)

val MnemonicBgStart = Color(0xFFFFFBE6)
val MnemonicBgEnd = Color(0xFFFFF4C2)
val MnemonicBorder = Color(0xFFF5D27A)
val MnemonicShadow = Color(0xFFE8C25A)
val FormulaOperatorColor = Color(0xFFC47A1A)

// --- Listening Choice Screen Tokens ---
val ListeningChipBg = Color(0xFFEFE8FF)
val ListeningChipBorder = Color(0xFFCDBDF2)
val ListeningPurple = Color(0xFF5B36B0)
val ListeningSpeakerStart = Color(0xFF8A63E0)
val ListeningSpeakerShadow = Color(0xFF3C2278)
val ListeningWaveIdle = Color(0xFFD8CDF3)
val ListeningQuestionText = Color(0xFF3B4A42)


// --- Mastery Level Colors & Metadata ---
data class MasteryLevelToken(
    val level: Int,
    val barColor: Color,
    val iconBgColor: Color,
    val emoji: String,
    val name: String
)

val MasteryLevels = listOf(
    MasteryLevelToken(0, Color(0xFF888780), Color(0xFFF1EFEA), "🌱", "Mới học"),
    MasteryLevelToken(1, Color(0xFFBA7517), Color(0xFFFDF3E7), "📖", "Bắt đầu nhớ"),
    MasteryLevelToken(2, Color(0xFFA32D2D), Color(0xFFFCE8E8), "✏️", "Đang luyện"),
    MasteryLevelToken(3, Color(0xFF185FA5), Color(0xFFE8F4FD), "💡", "Khá thuộc"),
    MasteryLevelToken(4, Color(0xFF1A7A4A), Color(0xFFEDF7EE), "⭐", "Thuộc tốt"),
    MasteryLevelToken(5, Color(0xFF534AB7), Color(0xFFF0EEFE), "🏆", "Thành thạo")
)

fun masteryLevelToken(level: Int): MasteryLevelToken {
    val clamped = level.coerceIn(0, 5)
    return MasteryLevels[clamped]
}

// --- Typography ---
val FontTitle = TextStyle(
    fontFamily = FontFamily.Default,
    fontWeight = FontWeight.Medium, // 500
    fontSize = 22.sp,
    lineHeight = 28.sp,
    color = TextPrimary
)

val FontHeading = TextStyle(
    fontFamily = FontFamily.Default,
    fontWeight = FontWeight.Medium, // 500
    fontSize = 18.sp,
    lineHeight = 24.sp,
    color = TextPrimary
)

val FontBody = TextStyle(
    fontFamily = FontFamily.Default,
    fontWeight = FontWeight.Normal, // 400
    fontSize = 15.sp,
    lineHeight = 22.sp,
    color = TextPrimary
)

val FontLabel = TextStyle(
    fontFamily = FontFamily.Default,
    fontWeight = FontWeight.Normal, // 400
    fontSize = 13.sp,
    lineHeight = 18.sp,
    color = TextSecondary
)

val FontCaption = TextStyle(
    fontFamily = FontFamily.Default,
    fontWeight = FontWeight.Normal, // 400
    fontSize = 12.sp,
    lineHeight = 16.sp,
    letterSpacing = 0.05.sp,
    color = TextSecondary
)

// --- Shape ---
val RadiusSmall = 8.dp
val RadiusMedium = 12.dp
val RadiusLarge = 16.dp
val RadiusXL = 20.dp

// --- Spacing ---
val SpaceXS = 4.dp
val SpaceSM = 8.dp
val SpaceMD = 12.dp
val SpaceLG = 16.dp
val SpaceXL = 20.dp
val Space2XL = 24.dp
