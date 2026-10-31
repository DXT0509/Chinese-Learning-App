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
