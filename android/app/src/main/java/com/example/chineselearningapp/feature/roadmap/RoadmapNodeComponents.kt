package com.example.chineselearningapp.feature.roadmap

import androidx.compose.animation.core.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.drawWithContent
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.*
import androidx.compose.ui.graphics.drawscope.Fill
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.stateDescription
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.chineselearningapp.R
import com.example.chineselearningapp.core.designsystem.*
import com.example.chineselearningapp.domain.model.RoadmapNode

/**
 * 4 States for Roadmap nodes
 */
enum class NodeState {
    DONE, CURRENT, LOCKED, REVIEW
}

/**
 * Shimmer shine modifier:
 * Sweeps from left to right with white overlay opacity 0 -> 0.2 -> 0.
 */
fun Modifier.shimmerShine(progress: Float, cornerRadius: Dp): Modifier = this.drawWithContent {
    drawContent()
    val width = size.width
    val height = size.height
    val bandWidth = width * 0.7f
    val startX = -bandWidth + progress * (width + 2f * bandWidth)
    val endX = startX + bandWidth

    val travelRatio = (progress * 2f).coerceAtMost(2f - progress * 2f).coerceIn(0f, 1f)
    val maxAlpha = 0.2f * travelRatio

    val shimmerBrush = Brush.linearGradient(
        colors = listOf(
            Color.White.copy(alpha = 0f),
            Color.White.copy(alpha = maxAlpha),
            Color.White.copy(alpha = 0f)
        ),
        start = Offset(startX, 0f),
        end = Offset(endX, height)
    )
    drawRoundRect(
        brush = shimmerBrush,
        size = size,
        cornerRadius = CornerRadius(cornerRadius.toPx(), cornerRadius.toPx())
    )
}

/**
 * Base 3D pressable node container with bottom shadow plate + elevation shadow.
 */
@Composable
fun Node3DButton(
    modifier: Modifier = Modifier,
    width: Dp,
    height: Dp,
    bottomShadowHeight: Dp,
    cornerRadius: Dp,
    bottomShadowColor: Color,
    elevationShadowColor: Color,
    onClick: () -> Unit,
    enabled: Boolean = true,
    content: @Composable BoxScope.() -> Unit
) {
    Box(
        modifier = modifier.size(width = width, height = height + bottomShadowHeight)
    ) {
        // Bottom 3D shadow plate
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(height)
                .offset(y = bottomShadowHeight)
                .background(
                    color = bottomShadowColor,
                    shape = RoundedCornerShape(cornerRadius)
                )
        )
        // Top surface button with elevation shadow
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(height)
                .shadow(
                    elevation = if (width > 65.dp) 10.dp else 7.dp,
                    shape = RoundedCornerShape(cornerRadius),
                    ambientColor = elevationShadowColor,
                    spotColor = elevationShadowColor
                )
                .clickable(enabled = enabled, onClick = onClick),
            content = content
        )
    }
}

/**
 * Checkmark badge for DONE node:
 * Circle 20dp top-right, fill white, stroke 2dp #1a7a4a, checkmark icon Primary 10sp.
 */
@Composable
fun DoneCheckmarkBadge(modifier: Modifier = Modifier) {
    Canvas(modifier = modifier.size(20.dp)) {
        val w = size.width
        val h = size.height
        drawCircle(color = Color.White)
        drawCircle(
            color = Color(0xFF1A7A4A),
            radius = (w / 2f) - 1.dp.toPx(),
            style = Stroke(width = 2.dp.toPx())
        )
        val checkPath = Path().apply {
            moveTo(w * 0.28f, h * 0.52f)
            lineTo(w * 0.44f, h * 0.68f)
            lineTo(w * 0.72f, h * 0.36f)
        }
        drawPath(
            path = checkPath,
            color = Color(0xFF1A7A4A),
            style = Stroke(width = 2.dp.toPx(), cap = StrokeCap.Round)
        )
    }
}

/**
 * Lightning badge for CURRENT node:
 * ⚡ bolt shape, top right, #ffe066, yellow glow, flash opacity 0->1->0 + scale 0.7->1.2->0.9.
 */
@Composable
fun CurrentLightningBadge(
    scale: Float,
    alpha: Float,
    modifier: Modifier = Modifier
) {
    Canvas(
        modifier = modifier
            .size(24.dp)
            .graphicsLayer {
                scaleX = scale
                scaleY = scale
                this.alpha = alpha
            }
    ) {
        val w = size.width
        val h = size.height
        drawCircle(
            color = Color(0xFFFFE066).copy(alpha = 0.5f),
            radius = w * 0.58f
        )
        drawCircle(
            color = Color(0xFFFFF9E6),
            radius = w * 0.44f
        )
        drawCircle(
            color = Color(0xFFFFE066),
            radius = w * 0.44f,
            style = Stroke(1.5.dp.toPx())
        )
        val boltPath = Path().apply {
            moveTo(w * 0.52f, h * 0.14f)
            lineTo(w * 0.26f, h * 0.52f)
            lineTo(w * 0.48f, h * 0.52f)
            lineTo(w * 0.40f, h * 0.88f)
            lineTo(w * 0.74f, h * 0.44f)
            lineTo(w * 0.52f, h * 0.44f)
            close()
        }
        drawPath(path = boltPath, color = Color(0xFFFFB300), style = Fill)
    }
}

/**
 * Locked padlock icon for LOCKED node (pure Canvas)
 */
@Composable
fun LockedPadlockIcon(modifier: Modifier = Modifier) {
    Canvas(modifier = modifier.size(24.dp)) {
        val w = size.width
        val h = size.height
        val lockColor = Color(0xFF888780)

        val shacklePath = Path().apply {
            moveTo(w * 0.33f, h * 0.46f)
            lineTo(w * 0.33f, h * 0.28f)
            arcTo(
                rect = androidx.compose.ui.geometry.Rect(
                    w * 0.33f, h * 0.12f,
                    w * 0.67f, h * 0.44f
                ),
                startAngleDegrees = 180f,
                sweepAngleDegrees = 180f,
                forceMoveTo = false
            )
            lineTo(w * 0.67f, h * 0.46f)
        }
        drawPath(
            path = shacklePath,
            color = lockColor,
            style = Stroke(width = 2.4.dp.toPx(), cap = StrokeCap.Round)
        )

        val bodyWidth = w * 0.62f
        val bodyHeight = h * 0.44f
        val bodyLeft = (w - bodyWidth) / 2f
        val bodyTop = h * 0.44f
        drawRoundRect(
            color = lockColor,
            topLeft = Offset(bodyLeft, bodyTop),
            size = Size(bodyWidth, bodyHeight),
            cornerRadius = CornerRadius(4.dp.toPx(), 4.dp.toPx())
        )

        drawCircle(
            color = Color.White,
            radius = 1.8.dp.toPx(),
            center = Offset(w * 0.5f, h * 0.62f)
        )
        drawLine(
            color = Color.White,
            start = Offset(w * 0.5f, h * 0.62f),
            end = Offset(w * 0.5f, h * 0.74f),
            strokeWidth = 1.8.dp.toPx(),
            cap = StrokeCap.Round
        )
    }
}

/**
 * Animated Star Icon for REVIEW node:
 * 5-pointed solid star (★) drawn with Canvas drawPath in Primary (#1A7A4A).
 * Stands still 3s -> rotates 360° in 0.8s -> stands still again, infinite loop.
 */
@Composable
fun ReviewStarIcon(modifier: Modifier = Modifier) {
    val reviewTransition = rememberInfiniteTransition(label = "ReviewRotation")
    val reviewRotation by reviewTransition.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(
            animation = keyframes {
                durationMillis = 3800
                0f at 0
                0f at 3000 using FastOutSlowInEasing
                360f at 3800
            },
            repeatMode = RepeatMode.Restart
        ),
        label = "ReviewRotate"
    )

    Canvas(
        modifier = modifier
            .size(26.dp)
            .graphicsLayer { rotationZ = reviewRotation }
    ) {
        val w = size.width
        val h = size.height
        val cx = w / 2f
        val cy = h / 2f
        val rOuter = w * 0.46f
        val rInner = rOuter * 0.40f
        val primaryColor = Color(0xFF1A7A4A)

        val starPath = Path().apply {
            for (i in 0 until 10) {
                val angleDeg = -90f + i * 36f
                val angleRad = Math.toRadians(angleDeg.toDouble())
                val r = if (i % 2 == 0) rOuter else rInner
                val x = cx + (r * kotlin.math.cos(angleRad)).toFloat()
                val y = cy + (r * kotlin.math.sin(angleRad)).toFloat()
                if (i == 0) moveTo(x, y) else lineTo(x, y)
            }
            close()
        }
        drawPath(path = starPath, color = primaryColor, style = Fill)
    }
}

/** Legacy alias for ReviewStarIcon */
@Composable
fun ReviewRefreshIcon(modifier: Modifier = Modifier) = ReviewStarIcon(modifier)

/**
 * Tooltip card displayed below CURRENT node (automatically visible).
 */
@Composable
fun CurrentNodeTooltip(
    node: RoadmapNode,
    enabled: Boolean,
    onStart: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier.widthIn(max = 240.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Canvas(modifier = Modifier.size(width = 14.dp, height = 7.dp)) {
            val trianglePath = Path().apply {
                moveTo(size.width / 2f, 0f)
                lineTo(size.width, size.height)
                lineTo(0f, size.height)
                close()
            }
            drawPath(trianglePath, color = Color.White)
        }
        Surface(
            shape = RoundedCornerShape(12.dp),
            color = Color.White,
            border = BorderStroke(0.5.dp, Border),
            shadowElevation = 3.dp
        ) {
            Column(
                modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Text(
                    text = "${node.title} · ${node.section}",
                    style = TextStyle(
                        fontSize = 13.sp,
                        fontWeight = FontWeight.Medium,
                        color = TextPrimary
                    ),
                    maxLines = 1
                )
                Text(
                    text = stringResource(R.string.roadmap_available),
                    style = TextStyle(fontSize = 11.sp, color = TextMuted)
                )
                Button(
                    onClick = onStart,
                    enabled = enabled,
                    modifier = Modifier.height(30.dp),
                    shape = RoundedCornerShape(8.dp),
                    contentPadding = PaddingValues(horizontal = 12.dp, vertical = 0.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = Primary)
                ) {
                    Text(
                        text = "Bắt đầu →",
                        style = TextStyle(
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Medium,
                            color = Color.White
                        )
                    )
                }
            }
        }
    }
}

/**
 * Floating sparkle particles background:
 * Vertical gradient [#e8f5ee, #f4f9f6, #eef4f1] + 6 ✦ sparkles floating up and fading.
 */
@Composable
fun FloatingSparklesBackground(modifier: Modifier = Modifier) {
    val infiniteTransition = rememberInfiniteTransition(label = "Sparkles")
    val masterTime by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 4000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "SparklesMaster"
    )

    val bgGradient = remember {
        Brush.verticalGradient(
            listOf(
                Color(0xFFE8F5EE),
                Color(0xFFF4F9F6),
                Color(0xFFEEF4F1)
            )
        )
    }

    val delays = remember { floatArrayOf(0f, 0.8f, 1.5f, 2.1f, 2.8f, 1.2f) }
    val positions = remember {
        arrayOf(
            0.12f to 0.18f,
            0.85f to 0.32f,
            0.20f to 0.54f,
            0.80f to 0.70f,
            0.45f to 0.86f,
            0.90f to 0.14f
        )
    }

    Canvas(modifier = modifier.background(bgGradient)) {
        val w = size.width
        val h = size.height

        for (i in delays.indices) {
            val delayFrac = delays[i] / 4.0f
            val particleProgress = (masterTime - delayFrac + 1f) % 1f
            val translateY = -40.dp.toPx() * particleProgress
            val alpha = (if (particleProgress < 0.5f) particleProgress * 2f else (1f - particleProgress) * 2f) * 0.4f

            val (relX, relY) = positions[i]
            val cx = relX * w
            val cy = relY * h + translateY
            val starRadius = (if (i % 2 == 0) 7.dp else 9.dp).toPx()

            val sparklePath = Path().apply {
                val inner = starRadius * 0.22f
                moveTo(cx, cy - starRadius)
                quadraticTo(cx + inner, cy - inner, cx + starRadius, cy)
                quadraticTo(cx + inner, cy + inner, cx, cy + starRadius)
                quadraticTo(cx - inner, cy + inner, cx - starRadius, cy)
                quadraticTo(cx - inner, cy - inner, cx, cy - starRadius)
                close()
            }
            drawPath(
                path = sparklePath,
                color = Color(0xFF1A7A4A).copy(alpha = alpha),
                style = Fill
            )
        }
    }
}

/**
 * Streak banner underneath AppBar:
 * Row: bg white, radius 12dp, border 0.5dp Border, padding 8 12
 * - 🔥 icon 20sp
 * - Column: số ngày streak 14sp weight 500 #e8700a / text phụ 11sp muted
 * - Spacer
 * - ⚡ icon + tổng XP 13sp weight 500 #ba7517
 */
@Composable
fun RoadmapStreakBanner(
    modifier: Modifier = Modifier,
    streakDays: Int = 3,
    totalXp: Int = 120
) {
    Surface(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        color = Color.White,
        border = BorderStroke(0.5.dp, Border),
        shadowElevation = 2.dp
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "🔥",
                fontSize = 20.sp,
                modifier = Modifier.padding(end = 8.dp)
            )
            Column {
                Text(
                    text = "$streakDays ngày streak",
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Medium,
                    color = Color(0xFFE8700A)
                )
                Text(
                    text = "Học đều đặn mỗi ngày",
                    fontSize = 11.sp,
                    color = TextMuted
                )
            }
            Spacer(Modifier.weight(1f))
            Text(
                text = "⚡",
                fontSize = 18.sp,
                modifier = Modifier.padding(end = 4.dp)
            )
            Text(
                text = "$totalXp XP",
                fontSize = 13.sp,
                fontWeight = FontWeight.Medium,
                color = Color(0xFFBA7517)
            )
        }
    }
}

/**
 * Calculates the emptiest spot between two consecutive nodes (node A and node B)
 * so that the floating mascot does not overlap the node or the connecting Bezier path.
 */
internal fun calculateMascotPlacement(
    posA: Int,
    posB: Int,
    isCurrent: Boolean
): Pair<Alignment, Modifier> {
    val topPadding = if (isCurrent) 28.dp else 18.dp
    return when (posA) {
        0 -> Alignment.TopEnd to Modifier.padding(end = 28.dp, top = topPadding)
        1 -> Alignment.TopStart to Modifier.padding(start = 28.dp, top = topPadding)
        else -> {
            // Node A is centered
            if (posB == 0) {
                // Exit curve bends left -> right side is emptiest
                Alignment.TopEnd to Modifier.padding(end = 20.dp, top = if (isCurrent) 36.dp else 24.dp)
            } else if (posB == 1) {
                // Exit curve bends right -> left side is emptiest
                Alignment.TopStart to Modifier.padding(start = 20.dp, top = if (isCurrent) 36.dp else 24.dp)
            } else {
                // Straight path down the middle -> choose side alternating by posA
                if (posA == 2) {
                    Alignment.TopStart to Modifier.padding(start = 20.dp, top = if (isCurrent) 36.dp else 24.dp)
                } else {
                    Alignment.TopEnd to Modifier.padding(end = 20.dp, top = if (isCurrent) 36.dp else 24.dp)
                }
            }
        }
    }
}

/**
 * RoadmapPathNode:
 * Renders a node in the roadmap with zigzag positioning, curved connection paths,
 * and state-specific styling & animations.
 */
@Composable
fun RoadmapPathNode(
    node: RoadmapNode,
    index: Int,
    previousNode: RoadmapNode?,
    nextNode: RoadmapNode?,
    current: Boolean,
    currentPosition: Int?,
    enabled: Boolean,
    showMascot: Boolean = false,
    open: () -> Unit
) {
    val nodeState = when {
        current -> NodeState.CURRENT
        node.type == "REVIEW" -> NodeState.REVIEW
        node.status == "COMPLETED" || node.status == "SKIPPED" -> NodeState.DONE
        !node.canOpen -> NodeState.LOCKED
        else -> NodeState.LOCKED
    }

    val label = stringResource(
        when {
            node.status == "COMPLETED" -> R.string.roadmap_completed
            node.status == "SKIPPED" -> R.string.roadmap_skipped
            node.status == "IN_PROGRESS" -> R.string.roadmap_in_progress
            !node.available -> R.string.roadmap_locked
            else -> R.string.roadmap_available
        }
    )

    // Zigzag position: 0 -> left (paddingStart 24dp), 1 -> right (paddingEnd 24dp), 2 -> center, 3 -> center
    val pos = (node.position % 4 + 4) % 4
    val itemAlignment = when (pos) {
        0 -> Alignment.TopStart
        1 -> Alignment.TopEnd
        else -> Alignment.TopCenter
    }
    val nodePadding = when (pos) {
        0 -> Modifier.padding(start = 24.dp)
        1 -> Modifier.padding(end = 24.dp)
        else -> Modifier
    }

    val isCurrent = nodeState == NodeState.CURRENT
    val nodeWidth = if (isCurrent) 70.dp else 62.dp
    val nodeHeight = if (isCurrent) 70.dp else 62.dp
    val bottomShadow = if (isCurrent) 6.dp else 5.dp
    val cornerRadius = if (isCurrent) 20.dp else 18.dp

    // Item height
    val itemHeight = if (isCurrent) 220.dp else 150.dp

    // Shimmer animation for DONE (3s) and CURRENT (2s)
    val shimmerCycleMs = if (isCurrent) 2000 else 3000
    val infiniteTransition = rememberInfiniteTransition(label = "NodeShimmer_$index")
    val shimmerProgress by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = shimmerCycleMs, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "ShimmerProgress"
    )

    // Bounce & Lightning animations for CURRENT (cycle 2.4s)
    val bounceY by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 0f,
        animationSpec = infiniteRepeatable(
            animation = keyframes {
                durationMillis = 2400
                0f at 0
                -5f at 600 using FastOutSlowInEasing
                1f at 1200 using FastOutSlowInEasing
                -1f at 1600 using FastOutSlowInEasing
                0f at 2000
                0f at 2400
            },
            repeatMode = RepeatMode.Restart
        ),
        label = "BounceY"
    )
    val lightningScale by infiniteTransition.animateFloat(
        initialValue = 0.7f,
        targetValue = 0.7f,
        animationSpec = infiniteRepeatable(
            animation = keyframes {
                durationMillis = 2400
                0.7f at 0
                0.7f at 400
                1.2f at 600
                0.9f at 850
                0.7f at 1100
                0.7f at 2400
            },
            repeatMode = RepeatMode.Restart
        ),
        label = "LightningScale"
    )
    val lightningAlpha by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 0f,
        animationSpec = infiniteRepeatable(
            animation = keyframes {
                durationMillis = 2400
                0f at 0
                0f at 400
                1f at 600
                0.6f at 850
                0f at 1100
                0f at 2400
            },
            repeatMode = RepeatMode.Restart
        ),
        label = "LightningAlpha"
    )

    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(itemHeight)
    ) {
        // Winding Bezier Path Canvas
        Canvas(modifier = Modifier.fillMaxSize()) {
            val w = size.width
            val h = size.height

            val xCurrent = when (pos) {
                0 -> 24.dp.toPx() + nodeWidth.toPx() / 2f
                1 -> w - 24.dp.toPx() - nodeWidth.toPx() / 2f
                else -> w / 2f
            }
            val yCurrent = (nodeHeight + bottomShadow).toPx() / 2f

            // 1. Entry line from previous item
            if (previousNode != null) {
                val prevIsDone = previousNode.status == "COMPLETED" || previousNode.status == "SKIPPED"
                val prevColor = if (prevIsDone) Color(0xFFC8E6D4) else Color(0xFFD8D6CE)
                val prevStroke = if (prevIsDone) {
                    Stroke(width = 3.dp.toPx(), cap = StrokeCap.Round)
                } else {
                    Stroke(
                        width = 3.dp.toPx(),
                        pathEffect = PathEffect.dashPathEffect(floatArrayOf(5.dp.toPx(), 4.dp.toPx())),
                        cap = StrokeCap.Round
                    )
                }
                drawLine(
                    color = prevColor,
                    start = Offset(xCurrent, 0f),
                    end = Offset(xCurrent, yCurrent),
                    strokeWidth = prevStroke.width,
                    cap = StrokeCap.Round,
                    pathEffect = prevStroke.pathEffect
                )
            }

            // 2. Exit curve to next item
            if (nextNode != null) {
                val nextPos = ((pos + 1) % 4 + 4) % 4
                val nextIsCurrent = nextNode.position == currentPosition
                val nextNodeWidth = if (nextIsCurrent) 70.dp else 62.dp
                val xNext = when (nextPos) {
                    0 -> 24.dp.toPx() + nextNodeWidth.toPx() / 2f
                    1 -> w - 24.dp.toPx() - nextNodeWidth.toPx() / 2f
                    else -> w / 2f
                }

                val thisIsDone = nodeState == NodeState.DONE
                val exitColor = if (thisIsDone) Color(0xFFC8E6D4) else Color(0xFFD8D6CE)
                val exitStroke = if (thisIsDone) {
                    Stroke(width = 3.dp.toPx(), cap = StrokeCap.Round)
                } else {
                    Stroke(
                        width = 3.dp.toPx(),
                        pathEffect = PathEffect.dashPathEffect(floatArrayOf(5.dp.toPx(), 4.dp.toPx())),
                        cap = StrokeCap.Round
                    )
                }

                val path = Path().apply {
                    moveTo(xCurrent, yCurrent)
                    val midY = (yCurrent + h) / 2f
                    cubicTo(
                        xCurrent, midY,
                        xNext, midY,
                        xNext, h
                    )
                }
                drawPath(path = path, color = exitColor, style = exitStroke)
            }
        }

        // Floating Tiger Mascot companion in the emptiest space between consecutive nodes
        if (showMascot) {
            val nextPos = if (nextNode != null) {
                ((nextNode.position % 4 + 4) % 4)
            } else {
                ((pos + 1) % 4 + 4) % 4
            }
            val (mascotAlignment, mascotPadding) = remember(pos, nextPos, isCurrent) {
                calculateMascotPlacement(pos, nextPos, isCurrent)
            }
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .then(mascotPadding),
                contentAlignment = mascotAlignment
            ) {
                TigerCanvas()
            }
        }

        // Node Content Column
        Box(
            modifier = Modifier
                .fillMaxSize()
                .then(nodePadding),
            contentAlignment = itemAlignment
        ) {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                modifier = Modifier
                    .widthIn(max = 240.dp)
                    .graphicsLayer {
                        if (isCurrent) {
                            translationY = bounceY.dp.toPx()
                        }
                    }
            ) {
                // 3D Pressable Node Button
                when (nodeState) {
                    NodeState.DONE -> {
                        Node3DButton(
                            width = nodeWidth,
                            height = nodeHeight,
                            bottomShadowHeight = bottomShadow,
                            cornerRadius = cornerRadius,
                            bottomShadowColor = Color(0xFF0F5533),
                            elevationShadowColor = Color(0x4D1A7A4A),
                            onClick = open,
                            enabled = enabled,
                            modifier = Modifier.semantics { stateDescription = label }
                        ) {
                            Box(
                                modifier = Modifier
                                    .fillMaxSize()
                                    .background(Color(0xFF1A7A4A), RoundedCornerShape(cornerRadius))
                                    .shimmerShine(shimmerProgress, cornerRadius),
                                contentAlignment = Alignment.Center
                            ) {
                                Text(
                                    text = node.title.take(1).ifEmpty { "字" },
                                    fontSize = 24.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = Color.White
                                )
                                DoneCheckmarkBadge(
                                    modifier = Modifier
                                        .align(Alignment.TopEnd)
                                        .offset(x = 4.dp, y = (-4).dp)
                                )
                            }
                        }
                    }
                    NodeState.CURRENT -> {
                        val currentGradient = remember {
                            Brush.linearGradient(
                                colors = listOf(Color(0xFF22A05E), Color(0xFF1A7A4A)),
                                start = Offset.Zero,
                                end = Offset(180f, 180f)
                            )
                        }
                        Node3DButton(
                            width = nodeWidth,
                            height = nodeHeight,
                            bottomShadowHeight = bottomShadow,
                            cornerRadius = cornerRadius,
                            bottomShadowColor = Color(0xFF0F5533),
                            elevationShadowColor = Color(0x661A7A4A),
                            onClick = open,
                            enabled = enabled,
                            modifier = Modifier.semantics { stateDescription = label }
                        ) {
                            Box(
                                modifier = Modifier
                                    .fillMaxSize()
                                    .background(currentGradient, RoundedCornerShape(cornerRadius))
                                    .shimmerShine(shimmerProgress, cornerRadius),
                                contentAlignment = Alignment.Center
                            ) {
                                Text(
                                    text = node.title.take(1).ifEmpty { "字" },
                                    fontSize = 28.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = Color.White
                                )
                                CurrentLightningBadge(
                                    scale = lightningScale,
                                    alpha = lightningAlpha,
                                    modifier = Modifier
                                        .align(Alignment.TopEnd)
                                        .offset(x = 6.dp, y = (-6).dp)
                                )
                            }
                        }
                    }
                    NodeState.LOCKED -> {
                        Node3DButton(
                            width = nodeWidth,
                            height = nodeHeight,
                            bottomShadowHeight = bottomShadow,
                            cornerRadius = cornerRadius,
                            bottomShadowColor = Color(0xFFB4B2A9),
                            elevationShadowColor = Color.Transparent,
                            onClick = open,
                            enabled = enabled,
                            modifier = Modifier.semantics { stateDescription = label }
                        ) {
                            Box(
                                modifier = Modifier
                                    .fillMaxSize()
                                    .background(Color(0xFFD8D6CE), RoundedCornerShape(cornerRadius)),
                                contentAlignment = Alignment.Center
                            ) {
                                LockedPadlockIcon()
                            }
                        }
                    }
                    NodeState.REVIEW -> {
                        Node3DButton(
                            width = nodeWidth,
                            height = nodeHeight,
                            bottomShadowHeight = bottomShadow,
                            cornerRadius = cornerRadius,
                            bottomShadowColor = Color(0xFFC8E6D4),
                            elevationShadowColor = Color(0x261A7A4A),
                            onClick = open,
                            enabled = enabled,
                            modifier = Modifier.semantics { stateDescription = label }
                        ) {
                            Box(
                                modifier = Modifier
                                    .fillMaxSize()
                                    .background(Color.White, RoundedCornerShape(cornerRadius))
                                    .border(
                                        BorderStroke(2.5.dp, Color(0xFF1A7A4A)),
                                        RoundedCornerShape(cornerRadius)
                                    ),
                                contentAlignment = Alignment.Center
                            ) {
                                ReviewStarIcon()
                            }
                        }
                    }
                }

                // Node Details / Tooltip
                if (isCurrent) {
                    Spacer(Modifier.height(6.dp))
                    CurrentNodeTooltip(
                        node = node,
                        enabled = enabled,
                        onStart = open
                    )
                } else {
                    Spacer(Modifier.height(6.dp))
                    Text(
                        text = node.title,
                        maxLines = 1,
                        style = TextStyle(
                            fontSize = 13.sp,
                            fontWeight = FontWeight.Medium,
                            color = if (nodeState == NodeState.LOCKED) TextMuted else TextPrimary
                        )
                    )
                    Text(
                        text = if (node.type == "REVIEW") stringResource(R.string.roadmap_review_state, label) else label,
                        style = TextStyle(
                            fontSize = 11.sp,
                            color = TextMuted
                        )
                    )
                }
            }
        }
    }
}
