package com.example.chineselearningapp.core.designsystem

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.awaitEachGesture
import androidx.compose.foundation.gestures.awaitFirstDown
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.StrokeJoin
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.compose.LifecycleEventEffect
import com.example.chineselearningapp.R
import com.example.chineselearningapp.core.navigation.Destination
import com.example.chineselearningapp.domain.repository.ReviewMasteryCount
import com.example.chineselearningapp.feature.dictionary.handwriting.HandwritingPoint
import com.example.chineselearningapp.feature.dictionary.handwriting.HandwritingStroke
import com.example.chineselearningapp.feature.dictionary.handwriting.StrokeCollector

// ==========================================
// 2. REUSABLE COMPONENTS
// ==========================================

/**
 * PrimaryButton: full width, height 52dp, border-radius 14dp, bg Primary, text white 16sp weight 500
 */
@Composable
fun PrimaryButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    loading: Boolean = false
) {
    Button(
        onClick = onClick,
        enabled = enabled && !loading,
        shape = RoundedCornerShape(14.dp),
        colors = ButtonDefaults.buttonColors(
            containerColor = Primary,
            contentColor = Color.White,
            disabledContainerColor = Primary.copy(alpha = 0.45f),
            disabledContentColor = Color.White.copy(alpha = 0.7f)
        ),
        modifier = modifier
            .fillMaxWidth()
            .height(52.dp)
    ) {
        if (loading) {
            CircularProgressIndicator(
                modifier = Modifier.size(20.dp),
                strokeWidth = 2.dp,
                color = Color.White
            )
            Spacer(Modifier.width(SpaceSM))
        }
        Text(
            text = text,
            fontSize = 16.sp,
            fontWeight = FontWeight.Medium,
            color = Color.White
        )
    }
}

/**
 * SecondaryButton: full width, height 46dp, border-radius 14dp, border 1dp Primary, text Primary 14sp weight 500, bg transparent
 */
@Composable
fun SecondaryButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true
) {
    OutlinedButton(
        onClick = onClick,
        enabled = enabled,
        shape = RoundedCornerShape(14.dp),
        border = BorderStroke(1.dp, if (enabled) Primary else Primary.copy(alpha = 0.35f)),
        colors = ButtonDefaults.outlinedButtonColors(
            containerColor = Color.Transparent,
            contentColor = Primary,
            disabledContentColor = Primary.copy(alpha = 0.35f)
        ),
        modifier = modifier
            .fillMaxWidth()
            .height(46.dp)
    ) {
        Text(
            text = text,
            fontSize = 14.sp,
            fontWeight = FontWeight.Medium,
            color = if (enabled) Primary else Primary.copy(alpha = 0.35f)
        )
    }
}

/**
 * ProgressBar: height 6dp, border-radius 3dp, bg Surface0, fill Primary
 */
@Composable
fun AppProgressBar(
    progress: Float,
    modifier: Modifier = Modifier
) {
    val clamped = progress.coerceIn(0f, 1f)
    val animatedProgress by animateFloatAsState(targetValue = clamped, label = "progressBar")
    Box(
        modifier = modifier
            .fillMaxWidth()
            .height(6.dp)
            .clip(RoundedCornerShape(3.dp))
            .background(Surface0)
    ) {
        Box(
            modifier = Modifier
                .fillMaxHeight()
                .fillMaxWidth(animatedProgress)
                .clip(RoundedCornerShape(3.dp))
                .background(Primary)
        )
    }
}

/**
 * MiniProgressBar: height 4dp, fill màu theo level
 */
@Composable
fun MiniProgressBar(
    progress: Float,
    fillColor: Color = Primary,
    modifier: Modifier = Modifier
) {
    val clamped = progress.coerceIn(0f, 1f)
    val animatedProgress by animateFloatAsState(targetValue = clamped, label = "miniProgressBar")
    Box(
        modifier = modifier
            .fillMaxWidth()
            .height(4.dp)
            .clip(RoundedCornerShape(2.dp))
            .background(Surface0)
    ) {
        Box(
            modifier = Modifier
                .fillMaxHeight()
                .fillMaxWidth(animatedProgress)
                .clip(RoundedCornerShape(2.dp))
                .background(fillColor)
        )
    }
}

/**
 * SectionLabel: 12sp UPPERCASE letterSpacing 0.06em, color TextSecondary
 */
@Composable
fun SectionLabel(
    text: String,
    modifier: Modifier = Modifier
) {
    Text(
        text = text.uppercase(),
        style = FontCaption.copy(
            fontWeight = FontWeight.Medium,
            letterSpacing = 0.06.sp,
            color = TextSecondary
        ),
        modifier = modifier
    )
}

/**
 * BottomNav: 4 tab (Trang chủ / Học tập / Ôn tập / Hồ sơ), icon 24dp, label 10sp, active color Primary
 */
data class NavTabItem(
    val destination: Destination,
    val iconRes: Int,
    val label: String
)

@Composable
fun AppBottomNav(
    selected: Destination?,
    onSelect: (Destination) -> Unit,
    modifier: Modifier = Modifier
) {
    val tabs = listOf(
        NavTabItem(Destination.Home, R.drawable.ic_home, stringResource(R.string.nav_home)),
        NavTabItem(Destination.Learning, R.drawable.ic_book, stringResource(R.string.nav_learning)),
        NavTabItem(Destination.Review, R.drawable.ic_review, stringResource(R.string.review)),
        NavTabItem(Destination.Profile, R.drawable.ic_person, stringResource(R.string.profile))
    )

    Surface(
        modifier = modifier
            .fillMaxWidth()
            .testTag("main_navigation"),
        color = Surface2,
        border = BorderStroke(1.dp, Border)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .navigationBarsPadding()
                .height(60.dp),
            horizontalArrangement = Arrangement.SpaceAround,
            verticalAlignment = Alignment.CenterVertically
        ) {
            tabs.forEach { tab ->
                val isSelected = selected == tab.destination
                val tintColor = if (isSelected) Primary else TextMuted
                Column(
                    modifier = Modifier
                        .weight(1f)
                        .fillMaxHeight()
                        .clickable { onSelect(tab.destination) }
                        .testTag("tab_${tab.destination.name}"),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center
                ) {
                    Icon(
                        painter = painterResource(tab.iconRes),
                        contentDescription = tab.label,
                        tint = tintColor,
                        modifier = Modifier.size(24.dp)
                    )
                    Spacer(Modifier.height(2.dp))
                    Text(
                        text = tab.label,
                        fontSize = 10.sp,
                        fontWeight = if (isSelected) FontWeight.Medium else FontWeight.Normal,
                        color = tintColor,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                }
            }
        }
    }
}

/**
 * TodayRow: label "Hôm nay" + ProgressBar (flex 1) + "12 / 20 phút" (caption) — nằm ngang 1 hàng
 */
@Composable
fun TodayRow(
    activeMinutes: Int,
    targetMinutes: Int,
    modifier: Modifier = Modifier
) {
    val progress = if (targetMinutes > 0) activeMinutes.toFloat() / targetMinutes else 0f
    Row(
        modifier = modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(SpaceMD)
    ) {
        Text(
            text = "Hôm nay",
            style = FontLabel.copy(fontWeight = FontWeight.Medium, color = TextPrimary)
        )
        Box(modifier = Modifier.weight(1f)) {
            AppProgressBar(progress = progress)
        }
        Text(
            text = "$activeMinutes / $targetMinutes phút",
            style = FontCaption.copy(color = TextSecondary)
        )
    }
}

/**
 * HeroCard (border-radius 20dp, gradient bg từ Primary → PrimaryDark, padding 20dp):
 * - Góc phải trên: emoji ⏰ size 120sp opacity 0.08 (decorative)
 * - Caption "ĐẾN HẠN ÔN TẬP"
 * - Số lớn: số từ đến hạn, 48sp weight 500, màu white
 * - Sub: "từ cần ôn · khoảng X phút", white opacity 0.75
 * - Detail: "Ôn sau: Y từ nữa", white opacity 0.6
 */
@Composable
fun HeroCard(
    dueCount: Int,
    estimatedMinutes: Int,
    laterCount: Int,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(RadiusXL))
            .background(
                Brush.verticalGradient(
                    colors = listOf(Primary, PrimaryDark)
                )
            )
            .padding(SpaceXL)
    ) {
        // Decorative background emoji
        Text(
            text = "⏰",
            fontSize = 120.sp,
            lineHeight = 120.sp,
            modifier = Modifier
                .align(Alignment.TopEnd)
                .offset(x = 18.dp, y = (-20).dp)
                .alpha(0.08f)
        )
        Column(
            modifier = Modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(SpaceXS)
        ) {
            Text(
                text = "ĐẾN HẠN ÔN TẬP",
                style = FontCaption.copy(
                    fontWeight = FontWeight.Medium,
                    letterSpacing = 0.05.sp,
                    color = Color.White.copy(alpha = 0.85f)
                )
            )
            Spacer(Modifier.height(SpaceXS))
            Text(
                text = "$dueCount",
                fontSize = 48.sp,
                fontWeight = FontWeight.Medium,
                color = Color.White,
                lineHeight = 52.sp
            )
            Text(
                text = "từ cần ôn · khoảng $estimatedMinutes phút",
                fontSize = 15.sp,
                fontWeight = FontWeight.Normal,
                color = Color.White.copy(alpha = 0.75f)
            )
            Spacer(Modifier.height(SpaceSM))
            Text(
                text = "Ôn sau: $laterCount từ nữa",
                fontSize = 13.sp,
                fontWeight = FontWeight.Normal,
                color = Color.White.copy(alpha = 0.60f)
            )
        }
    }
}

/**
 * MasteryList — 6 row, mỗi row gồm:
 * - Icon container 32×32dp border-radius 8dp, bg = màu bg theo level, emoji icon
 * - Column: tên mức (13sp weight 500) + MiniProgressBar (width = count/maxCount * 100%)
 * - Số từ (13sp weight 500, màu theo level)
 * - Emoji icons: 🌱 📖 ✏️ 💡 ⭐ 🏆
 * - Tên: "Mới học", "Bắt đầu nhớ", "Đang luyện", "Khá thuộc", "Thuộc tốt", "Thành thạo"
 */
@Composable
fun MasteryList(
    distribution: List<ReviewMasteryCount>?,
    modifier: Modifier = Modifier
) {
    val countsByLevel = distribution?.associate { it.level to it.count } ?: emptyMap()
    val maxCount = maxOf(1, MasteryLevels.maxOf { countsByLevel[it.level] ?: 0 })

    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(SpaceSM)
    ) {
        MasteryLevels.forEach { token ->
            val count = countsByLevel[token.level] ?: 0
            val ratio = if (maxCount > 0) count.toFloat() / maxCount else 0f
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(RadiusMedium))
                    .background(Surface1)
                    .border(1.dp, Border, RoundedCornerShape(RadiusMedium))
                    .padding(horizontal = SpaceMD, vertical = SpaceSM),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(SpaceMD)
            ) {
                Box(
                    modifier = Modifier
                        .size(32.dp)
                        .clip(RoundedCornerShape(RadiusSmall))
                        .background(token.iconBgColor),
                    contentAlignment = Alignment.Center
                ) {
                    Text(text = token.emoji, fontSize = 16.sp)
                }
                Column(
                    modifier = Modifier.weight(1f),
                    verticalArrangement = Arrangement.spacedBy(SpaceXS)
                ) {
                    Text(
                        text = token.name,
                        fontSize = 13.sp,
                        fontWeight = FontWeight.Medium,
                        color = TextPrimary
                    )
                    MiniProgressBar(
                        progress = ratio,
                        fillColor = token.barColor
                    )
                }
                Text(
                    text = "$count từ",
                    fontSize = 13.sp,
                    fontWeight = FontWeight.Medium,
                    color = token.barColor
                )
            }
        }
    }
}

/**
 * WordCard (Surface1 bg, border-radius 16dp, padding 16dp):
 * - Nghĩa từ: 16sp weight 500, TextPrimary
 * - Ví dụ: 13sp TextMuted
 */
@Composable
fun WordCard(
    meaning: String,
    exampleOrCue: String? = null,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(RadiusLarge))
            .background(Surface1)
            .border(1.dp, Border, RoundedCornerShape(RadiusLarge))
            .padding(SpaceLG),
        verticalArrangement = Arrangement.spacedBy(SpaceXS)
    ) {
        Text(
            text = meaning,
            fontSize = 16.sp,
            fontWeight = FontWeight.Medium,
            color = TextPrimary
        )
        if (!exampleOrCue.isNullOrBlank()) {
            Text(
                text = exampleOrCue,
                fontSize = 13.sp,
                fontWeight = FontWeight.Normal,
                color = TextMuted
            )
        }
    }
}

/**
 * ModeTabs — 2 tab ngang ("1. Chữ Hán" / "2. Pinyin"), border 1dp Border, active: border Primary, text Primary, bg PrimaryLight
 */
@Composable
fun ModeTabs(
    selectedTab: String,
    onSelectTab: (String) -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true
) {
    Row(
        modifier = modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(SpaceSM)
    ) {
        val tabs = listOf("HANZI" to "1. Chữ Hán", "PINYIN" to "2. Pinyin")
        tabs.forEach { (code, title) ->
            val isSelected = selectedTab == code
            Box(
                modifier = Modifier
                    .weight(1f)
                    .clip(RoundedCornerShape(RadiusMedium))
                    .background(if (isSelected) PrimaryLight else Surface1)
                    .border(
                        1.dp,
                        if (isSelected) Primary else Border,
                        RoundedCornerShape(RadiusMedium)
                    )
                    .clickable(enabled = enabled) { onSelectTab(code) }
                    .padding(vertical = SpaceMD),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = title,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Medium,
                    color = if (isSelected) Primary else TextSecondary
                )
            }
        }
    }
}

/**
 * CanvasArea (Surface1 bg, border-radius 16dp, padding 12dp):
 * - DrawingCanvas: bg Surface0, border-radius 12dp, aspect ratio 4:3
 * - Canvas có lưới 2×2 (đường kẻ nét mờ border-color)
 * - Placeholder: chữ Hán gợi ý mờ ở giữa (opacity 0.15) nếu cần
 * - ActionRow bên dưới canvas: 2 ghost button "Hoàn tác" + "Xóa nét" (weight đều nhau)
 */
@Composable
fun CanvasArea(
    strokes: List<HandwritingStroke>,
    enabled: Boolean,
    onBeginStroke: () -> Unit,
    onCompleteStroke: (HandwritingStroke?) -> Unit,
    onUndo: () -> Unit,
    onClear: () -> Unit,
    placeholder: String? = null,
    modifier: Modifier = Modifier,
    preserveInterrupted: Boolean = false,
    undoEnabled: Boolean = strokes.isNotEmpty(),
    clearEnabled: Boolean = strokes.isNotEmpty()
) {
    Surface(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(RadiusLarge),
        color = Surface1,
        border = BorderStroke(1.dp, Border)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(SpaceMD),
            verticalArrangement = Arrangement.spacedBy(SpaceSM)
        ) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .aspectRatio(4f / 3f)
                    .clip(RoundedCornerShape(RadiusMedium))
                    .background(Surface0)
            ) {
                if (!placeholder.isNullOrBlank()) {
                    Text(
                        text = placeholder,
                        fontSize = 84.sp,
                        color = TextPrimary.copy(alpha = 0.15f),
                        modifier = Modifier.align(Alignment.Center)
                    )
                }
                DrawingGridCanvas(
                    strokes = strokes,
                    enabled = enabled,
                    onBegin = onBeginStroke,
                    onComplete = onCompleteStroke,
                    preserveInterrupted = preserveInterrupted
                )
            }
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(SpaceSM)
            ) {
                TextButton(
                    onClick = onUndo,
                    enabled = enabled && undoEnabled,
                    modifier = Modifier.weight(1f)
                ) {
                    Text(
                        text = "Hoàn tác",
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Medium,
                        color = if (enabled && undoEnabled) Primary else TextMuted
                    )
                }
                TextButton(
                    onClick = onClear,
                    enabled = enabled && clearEnabled,
                    modifier = Modifier.weight(1f)
                ) {
                    Text(
                        text = "Xóa nét",
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Medium,
                        color = if (enabled && clearEnabled) Primary else TextMuted
                    )
                }
            }
        }
    }
}

@Composable
internal fun DrawingGridCanvas(
    strokes: List<HandwritingStroke>,
    enabled: Boolean,
    onBegin: () -> Unit,
    onComplete: (HandwritingStroke?) -> Unit,
    preserveInterrupted: Boolean = false
) {
    val active = remember { mutableStateListOf<HandwritingPoint>() }
    var gestureEpoch by remember { mutableIntStateOf(0) }
    val currentBegin by rememberUpdatedState(onBegin)
    val currentComplete by rememberUpdatedState(onComplete)

    LifecycleEventEffect(if (preserveInterrupted) Lifecycle.Event.ON_PAUSE else Lifecycle.Event.ON_STOP) {
        if (preserveInterrupted && active.isNotEmpty()) {
            currentComplete(HandwritingStroke(active.toList()))
            active.clear()
        }
        gestureEpoch++
    }

    val inkColor = TextPrimary
    val gridColor = Border
    val description = stringResource(R.string.ink_canvas)

    Canvas(
        modifier = Modifier
            .fillMaxSize()
            .testTag("handwriting_canvas")
            .semantics { contentDescription = description }
            .pointerInput(enabled, gestureEpoch) {
                if (!enabled) return@pointerInput
                val collector = StrokeCollector()
                try {
                    awaitEachGesture {
                        val down = awaitFirstDown(requireUnconsumed = false)
                        fun point(position: Offset, time: Long) = HandwritingPoint(
                            (position.x / size.width * 1000f).coerceIn(0f, 1000f),
                            (position.y / size.height * 1000f).coerceIn(0f, 1000f),
                            time
                        )
                        down.consume()
                        val first = point(down.position, down.uptimeMillis)
                        collector.start(first)
                        active.clear()
                        active.add(first)
                        currentBegin()
                        var finished = false
                        try {
                            while (true) {
                                val event = awaitPointerEvent()
                                val change = event.changes.firstOrNull { it.id == down.id } ?: break
                                if (change.isConsumed) break
                                change.historical.forEach { sample ->
                                    val historical = point(sample.position, sample.uptimeMillis)
                                    collector.move(historical)
                                    active.add(historical)
                                }
                                val next = point(change.position, change.uptimeMillis)
                                change.consume()
                                if (!change.pressed) {
                                    currentComplete(collector.finish(next))
                                    finished = true
                                    break
                                }
                                collector.move(next)
                                active.add(next)
                            }
                        } finally {
                            if (!finished) currentComplete(if (preserveInterrupted && active.isNotEmpty()) HandwritingStroke(active.toList()) else null)
                            collector.cancel()
                            active.clear()
                        }
                    }
                } finally {
                    collector.cancel()
                    active.clear()
                    currentComplete(null)
                }
            }
    ) {
        // Lưới 2x2: đường kẻ nét mờ border-color
        drawLine(
            color = gridColor,
            start = Offset(size.width / 2f, 0f),
            end = Offset(size.width / 2f, size.height),
            strokeWidth = 1.dp.toPx()
        )
        drawLine(
            color = gridColor,
            start = Offset(0f, size.height / 2f),
            end = Offset(size.width, size.height / 2f),
            strokeWidth = 1.dp.toPx()
        )

        fun renderStroke(points: List<HandwritingPoint>) {
            if (points.isEmpty()) return
            fun offset(p: HandwritingPoint) = Offset(p.x / 1000f * size.width, p.y / 1000f * size.height)
            val first = offset(points.first())
            if (points.size == 1 || points.all { it.x == points.first().x && it.y == points.first().y }) {
                drawCircle(inkColor, 2.dp.toPx(), first)
                return
            }
            val path = Path().apply {
                moveTo(first.x, first.y)
                points.zipWithNext().forEach { (prev, next) ->
                    val p = offset(prev)
                    val n = offset(next)
                    quadraticTo(p.x, p.y, (p.x + n.x) / 2f, (p.y + n.y) / 2f)
                }
                val last = offset(points.last())
                lineTo(last.x, last.y)
            }
            drawPath(path, inkColor, style = Stroke(4.dp.toPx(), cap = StrokeCap.Round, join = StrokeJoin.Round))
        }

        strokes.forEach { renderStroke(it.points) }
        renderStroke(active)
    }
}

/**
 * ChipRow (hiện ra sau khi nhận diện): các chip chữ Hán được suggest, tap để chọn
 * - Chip style: border 1dp Border, border-radius 20dp, padding 6dp 14dp, font 18sp
 * - Selected: border Primary, bg PrimaryMuted, text Primary
 */
@Composable
fun ChipRow(
    candidates: List<String>,
    selected: String?,
    onSelect: (String) -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true
) {
    if (candidates.isEmpty()) return
    Row(
        modifier = modifier
            .fillMaxWidth()
            .horizontalScroll(rememberScrollState()),
        horizontalArrangement = Arrangement.spacedBy(SpaceSM)
    ) {
        candidates.forEach { candidate ->
            val isSelected = candidate == selected
            Box(
                modifier = Modifier
                    .clip(RoundedCornerShape(RadiusXL))
                    .background(if (isSelected) PrimaryMuted else Surface2)
                    .border(
                        1.dp,
                        if (isSelected) Primary else Border,
                        RoundedCornerShape(RadiusXL)
                    )
                    .clickable(enabled = enabled) { onSelect(candidate) }
                    .padding(horizontal = 14.dp, vertical = 6.dp),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = candidate,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Medium,
                    color = if (isSelected) Primary else TextPrimary
                )
            }
        }
    }
}
