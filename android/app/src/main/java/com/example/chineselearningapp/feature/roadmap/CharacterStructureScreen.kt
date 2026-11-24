package com.example.chineselearningapp.feature.roadmap

import androidx.activity.compose.BackHandler
import androidx.compose.animation.Crossfade
import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.zIndex
import com.example.chineselearningapp.core.designsystem.*
import com.example.chineselearningapp.domain.model.LessonComponent
import com.example.chineselearningapp.domain.model.RoadmapLesson
import com.example.chineselearningapp.domain.model.RoadmapWord
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

/**
 * Scene 2: CharacterStructureScreen (Cấu tạo chữ)
 * Step-by-step reveal: Character card -> Each component/radical piece -> Formula & Mnemonic
 */
@Composable
fun CharacterStructureScreen(
    word: RoadmapWord,
    lesson: RoadmapLesson,
    enabled: Boolean,
    onBack: () -> Unit,
    onContinue: () -> Unit,
    onSkip: () -> Unit = {},
    canSkip: Boolean = false,
    modifier: Modifier = Modifier,
    status: @Composable () -> Unit = {},
    progress: Float = 1f / 9f,
    onKnownWord: () -> Unit = {},
    onLeaveLesson: () -> Unit = {},
    onPauseLesson: () -> Unit = {},
    onResumeLesson: () -> Unit = {},
) {
    val components = remember(lesson.components) {
        lesson.components.filter { it.explanation.available }
    }
    val mnemonic = remember(word.simplified, lesson.lessonVersionId) {
        resolveMnemonic(word, lesson)
    }

    val hasComponents = components.isNotEmpty()
    val hasMnemonic = !mnemonic.isNullOrBlank()
    val finalStep = if (hasComponents) {
        components.size + if (hasMnemonic) 1 else 0
    } else {
        if (hasMnemonic) 1 else 0
    }

    var step by rememberSaveable(word.id, word.contentVersion, lesson.lessonVersionId) {
        mutableIntStateOf(0)
    }
    var showSettingsSheet by rememberSaveable { mutableStateOf(false) }

    val ready = step >= finalStep
    val allPiecesRevealed = hasComponents && step >= components.size
    val isFormulaStep = step > components.size || (!hasComponents && step >= finalStep && hasMnemonic)

    val scrollState = rememberScrollState()
    LaunchedEffect(step, scrollState.maxValue) {
        if (step > 0) {
            scrollState.animateScrollTo(scrollState.maxValue)
        }
    }

    // Back handling: decrement reveal step if > 0, otherwise go to previous scene
    fun handleBack() {
        if (step > 0) {
            step--
        } else {
            onBack()
        }
    }

    BackHandler(enabled = !showSettingsSheet) {
        handleBack()
    }

    LaunchedEffect(showSettingsSheet) {
        if (showSettingsSheet) {
            onPauseLesson()
        }
    }

    // Hanzi Card Bounce animation when all pieces are revealed:
    // scale 1 -> 1.12 -> 1, rotation -3° -> 0, spring overshoot
    val hanziBounceScale = remember { Animatable(1f) }
    val hanziBounceRotation = remember { Animatable(0f) }

    LaunchedEffect(allPiecesRevealed) {
        if (allPiecesRevealed) {
            hanziBounceRotation.snapTo(-3f)
            launch {
                hanziBounceRotation.animateTo(
                    targetValue = 0f,
                    animationSpec = spring(
                        dampingRatio = 0.5f,
                        stiffness = Spring.StiffnessMediumLow
                    )
                )
            }
            hanziBounceScale.animateTo(
                targetValue = 1.12f,
                animationSpec = spring(
                    dampingRatio = 0.5f,
                    stiffness = Spring.StiffnessMediumLow
                )
            )
            hanziBounceScale.animateTo(
                targetValue = 1f,
                animationSpec = spring(
                    dampingRatio = 0.55f,
                    stiffness = Spring.StiffnessLow
                )
            )
        }
    }

    // Formula tokens & sequential highlight animation
    val formulaTokens = remember(components, word.simplified) {
        buildFormulaTokens(components, word.simplified)
    }
    var highlightIndex by remember { mutableIntStateOf(-1) }
    LaunchedEffect(isFormulaStep) {
        if (isFormulaStep && formulaTokens.isNotEmpty()) {
            delay(350L) // wait for card entrance spring
            for (i in formulaTokens.indices) {
                highlightIndex = i
                delay(120L)
            }
            highlightIndex = -1
        }
    }

    val mascotMessage = getMascotMessage(step, components, finalStep)
    val isCompact = components.size > 3

    val screenBackgroundBrush = Brush.verticalGradient(
        colorStops = arrayOf(
            0.0f to ScreenGradientTop,
            0.55f to ScreenGradientMid,
            1.0f to Color.White
        )
    )

    Box(modifier = modifier.fillMaxSize()) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .background(screenBackgroundBrush)
                .statusBarsPadding(),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // 1. LessonTopBar
            LessonTopBar(
                progress = progress,
                canGoBack = true,
                onBack = ::handleBack,
                onSettings = { showSettingsSheet = true }
            )

            // Status slot for network errors / loading
            status()

            // Scrollable center viewport
            BoxWithConstraints(
                modifier = Modifier
                    .weight(1f)
                    .widthIn(max = 680.dp)
                    .fillMaxWidth()
            ) {
                val minHeight = maxHeight
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .verticalScroll(scrollState)
                        .heightIn(min = minHeight)
                        .padding(horizontal = 24.dp, vertical = 6.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Top
                ) {
                    // 2. Chip "🧩 CẤU TẠO CHỮ"
                    Box(
                        modifier = Modifier
                            .padding(top = 14.dp)
                            .background(StructureChipBg, RoundedCornerShape(20.dp))
                            .border(1.5.dp, StructureChipBorder, RoundedCornerShape(20.dp))
                            .padding(horizontal = 12.dp, vertical = 4.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            PuzzlePieceCanvas(modifier = Modifier.size(13.dp))
                            Text(
                                text = "CẤU TẠO CHỮ",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Medium,
                                letterSpacing = 0.06.sp,
                                color = StructureChipText
                            )
                        }
                    }

                    Spacer(Modifier.height(14.dp))

                    // 3. Thẻ chữ Hán nhỏ (luôn hiện): 150×150dp, bo 24dp, bottom shadow 6dp #c8e0d2, lưới 田字格
                    Box(
                        modifier = Modifier
                            .size(width = 150.dp, height = 156.dp)
                            .graphicsLayer {
                                scaleX = hanziBounceScale.value
                                scaleY = hanziBounceScale.value
                                rotationZ = hanziBounceRotation.value
                            },
                        contentAlignment = Alignment.TopCenter
                    ) {
                        // Bottom shadow 6dp #c8e0d2
                        Box(
                            modifier = Modifier
                                .offset(y = 6.dp)
                                .size(150.dp)
                                .background(LessonShadow, RoundedCornerShape(24.dp))
                        )
                        // Card surface
                        Box(
                            modifier = Modifier
                                .size(150.dp)
                                .background(Color.White, RoundedCornerShape(24.dp))
                                .border(2.dp, LessonBorder, RoundedCornerShape(24.dp)),
                            contentAlignment = Alignment.Center
                        ) {
                            TianZiGeGridCanvas(
                                modifier = Modifier.fillMaxSize(),
                                inset = 10.dp,
                                cornerRadius = 12.dp
                            )
                            Text(
                                text = word.simplified,
                                fontSize = 84.sp,
                                fontFamily = FontFamily.Serif,
                                color = TextPrimary,
                                textAlign = TextAlign.Center
                            )
                        }
                    }

                    // 4 & 5. Danh sách mảnh ghép (margin top 16dp)
                    if (hasComponents) {
                        Spacer(Modifier.height(16.dp))

                        Column(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            components.forEachIndexed { index, component ->
                                key(component.position, index, component.component) {
                                    val isPieceRevealed = step > index

                                    // 5. Nút tròn "+" 26dp giữa 2 PieceCard liên tiếp
                                    if (index > 0) {
                                        StructureRevealContainer(
                                            visible = isPieceRevealed,
                                            delayMillis = 0,
                                            modifier = Modifier
                                                .offset(y = (-2).dp)
                                                .zIndex(1f)
                                        ) {
                                            Box(
                                                modifier = Modifier.size(width = 26.dp, height = 28.dp),
                                                contentAlignment = Alignment.TopCenter
                                            ) {
                                                // Bottom shadow 2dp #0f5533
                                                Box(
                                                    modifier = Modifier
                                                        .offset(y = 2.dp)
                                                        .size(26.dp)
                                                        .background(PrimaryDark, CircleShape)
                                                )
                                                // Button surface
                                                Box(
                                                    modifier = Modifier
                                                        .size(26.dp)
                                                        .background(Primary, CircleShape),
                                                    contentAlignment = Alignment.Center
                                                ) {
                                                    Text(
                                                        text = "+",
                                                        color = Color.White,
                                                        fontSize = 15.sp,
                                                        fontWeight = FontWeight.Bold,
                                                        textAlign = TextAlign.Center
                                                    )
                                                }
                                            }
                                        }
                                    }

                                    // 4. PieceCard (staggered 80ms after + button)
                                    StructureRevealContainer(
                                        visible = isPieceRevealed,
                                        delayMillis = if (index > 0) 80 else 0,
                                        modifier = Modifier.fillMaxWidth()
                                    ) {
                                        PieceCard(
                                            component = component,
                                            isCompact = isCompact
                                        )
                                    }
                                }
                            }
                        }
                    }

                    // 6. Thẻ công thức + mẹo nhớ (reveal cuối cùng)
                    if (hasMnemonic || formulaTokens.isNotEmpty()) {
                        Spacer(Modifier.height(12.dp))

                        StructureRevealContainer(
                            visible = isFormulaStep,
                            delayMillis = 0,
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            FormulaMnemonicCard(
                                tokens = formulaTokens,
                                highlightIndex = highlightIndex,
                                mnemonic = mnemonic
                            )
                        }
                    }

                    // 7. Spacer đẩy phần dưới xuống đáy
                    Spacer(Modifier.height(20.dp))
                }
            }

            // 8. Hàng mascot + 9. PrimaryButton 3D ở đáy
            Column(
                modifier = Modifier
                    .widthIn(max = 680.dp)
                    .fillMaxWidth()
                    .navigationBarsPadding()
                    .padding(start = 20.dp, end = 20.dp, bottom = 16.dp, top = 8.dp),
                verticalArrangement = Arrangement.spacedBy(14.dp)
            ) {
                // Hàng mascot: TigerMascot nhỏ (46×56dp) + bubble chat
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    TigerCanvas(width = 46.dp, height = 56.dp)
                    Surface(
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(
                            topStart = 14.dp,
                            topEnd = 14.dp,
                            bottomEnd = 14.dp,
                            bottomStart = 4.dp
                        ),
                        color = Color.White,
                        border = BorderStroke(1.5.dp, LessonBorder)
                    ) {
                        Crossfade(
                            targetState = mascotMessage,
                            animationSpec = tween(200),
                            label = "structureTigerMessageAnim"
                        ) { text ->
                            Text(
                                text = text,
                                modifier = Modifier.padding(horizontal = 14.dp, vertical = 10.dp),
                                fontSize = 12.sp,
                                lineHeight = 17.sp,
                                color = TextPrimary
                            )
                        }
                    }
                }

                // 9. PrimaryButton 3D full width
                LessonPrimary3DButton(
                    text = if (ready) "Hiểu rồi, tiếp tục →" else "Tiếp tục",
                    onClick = {
                        if (ready) {
                            onContinue()
                        } else {
                            step++
                        }
                    },
                    enabled = enabled
                )
            }
        }

        // Lesson Settings Bottom Sheet
        if (showSettingsSheet) {
            LessonSettingsSheet(
                onKnownWord = onKnownWord,
                onLeaveLesson = onLeaveLesson,
                onDismiss = {
                    showSettingsSheet = false
                    onResumeLesson()
                }
            )
        }
    }
}

/**
 * PieceCard for an individual component or radical.
 * Left: 56x56dp (or 44x44dp compact) character box with 3dp bottom shadow.
 * Right: Text column with tag ("BIỂU NGHĨA" / "THÀNH PHẦN"), radical name, and concise meaning (<= 4 words).
 */
@Composable
private fun PieceCard(
    component: LessonComponent,
    isCompact: Boolean,
    modifier: Modifier = Modifier
) {
    val info = remember(component.component, component.role) {
        getComponentInfo(component)
    }

    val bgColor = if (info.isSemantic) SemanticBg else ComponentTagBg
    val borderColor = if (info.isSemantic) SemanticBorder else ComponentTagBorder
    val textColor = if (info.isSemantic) SemanticText else ComponentTagText
    val shadowColor = borderColor

    val boxSize = if (isCompact) 44.dp else 56.dp
    val boxShape = RoundedCornerShape(if (isCompact) 12.dp else 16.dp)
    val charFontSize = if (isCompact) 24.sp else 34.sp

    Box(
        modifier = modifier
            .fillMaxWidth()
            .padding(bottom = 4.dp),
        contentAlignment = Alignment.TopCenter
    ) {
        // Bottom shadow 4dp #c8e0d2
        Box(
            modifier = Modifier
                .matchParentSize()
                .offset(y = 4.dp)
                .background(LessonShadow, RoundedCornerShape(18.dp))
        )
        // Card surface
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(Color.White, RoundedCornerShape(18.dp))
                .border(2.dp, LessonBorder, RoundedCornerShape(18.dp))
                .padding(horizontal = 12.dp, vertical = if (isCompact) 8.dp else 10.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Ô chữ bên trái
                Box(
                    modifier = Modifier.size(width = boxSize, height = boxSize + 3.dp),
                    contentAlignment = Alignment.TopCenter
                ) {
                    // Bottom shadow 3dp cùng tông màu viền
                    Box(
                        modifier = Modifier
                            .offset(y = 3.dp)
                            .size(boxSize)
                            .background(shadowColor, boxShape)
                    )
                    // Surface
                    Box(
                        modifier = Modifier
                            .size(boxSize)
                            .background(bgColor, boxShape)
                            .border(2.dp, borderColor, boxShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = component.component,
                            fontSize = charFontSize,
                            fontFamily = FontFamily.Serif,
                            color = textColor,
                            textAlign = TextAlign.Center
                        )
                    }
                }

                Spacer(Modifier.width(12.dp))

                // Cột text bên phải
                Column(
                    modifier = Modifier.weight(1f),
                    verticalArrangement = Arrangement.spacedBy(2.dp)
                ) {
                    // Thẻ tag nhỏ: 9sp weight 500, letterSpacing 0.07em, bo 6dp, padding 2x6dp
                    Box(
                        modifier = Modifier
                            .background(bgColor, RoundedCornerShape(6.dp))
                            .border(1.dp, borderColor, RoundedCornerShape(6.dp))
                            .padding(horizontal = 6.dp, vertical = 2.dp)
                    ) {
                        Text(
                            text = if (info.isSemantic) "BIỂU NGHĨA" else "THÀNH PHẦN",
                            fontSize = 9.sp,
                            fontWeight = FontWeight.Medium,
                            letterSpacing = 0.07.sp,
                            color = textColor
                        )
                    }

                    // Dòng tên bộ 13sp màu TextSecondary (ẩn khi compact > 3 mảnh)
                    if (!isCompact) {
                        Text(
                            text = info.name,
                            fontSize = 13.sp,
                            color = TextSecondary,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis
                        )
                    }

                    // Dòng nghĩa: 16sp weight 500, tối đa 1 dòng, <= 4 từ
                    if (!info.meaning.isNullOrBlank()) {
                        Text(
                            text = info.meaning,
                            fontSize = if (isCompact) 14.sp else 16.sp,
                            fontWeight = FontWeight.Medium,
                            color = TextPrimary,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis
                        )
                    }
                }
            }
        }
    }
}

/**
 * Thẻ công thức + mẹo nhớ:
 * Nền gradient #fffbe6 -> #fff4c2, viền 2dp #f5d27a, bottom shadow 4dp #e8c25a, bo 18dp.
 * Dòng công thức serif 26sp, dấu + và = màu #c47a1a.
 * Dòng mẹo 13sp weight 500, icon bóng đèn vector.
 */
@Composable
private fun FormulaMnemonicCard(
    tokens: List<FormulaToken>,
    highlightIndex: Int,
    mnemonic: String?,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .fillMaxWidth()
            .padding(bottom = 4.dp),
        contentAlignment = Alignment.TopCenter
    ) {
        // Bottom shadow 4dp #e8c25a
        Box(
            modifier = Modifier
                .matchParentSize()
                .offset(y = 4.dp)
                .background(MnemonicShadow, RoundedCornerShape(18.dp))
        )
        // Surface
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(
                    brush = Brush.verticalGradient(listOf(MnemonicBgStart, MnemonicBgEnd)),
                    shape = RoundedCornerShape(18.dp)
                )
                .border(2.dp, MnemonicBorder, RoundedCornerShape(18.dp))
                .padding(horizontal = 14.dp, vertical = 10.dp),
            contentAlignment = Alignment.Center
        ) {
            Column(
                modifier = Modifier.fillMaxWidth(),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                // Dòng công thức
                if (tokens.isNotEmpty()) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.Center
                    ) {
                        tokens.forEachIndexed { index, token ->
                            val isHighlighted = highlightIndex == index
                            val targetColor = when {
                                isHighlighted -> FormulaOperatorColor
                                token.isOperator -> FormulaOperatorColor
                                else -> TextPrimary
                            }
                            val animColor by animateColorAsState(
                                targetValue = targetColor,
                                animationSpec = tween(durationMillis = 100),
                                label = "formulaTokenColor_$index"
                            )
                            Text(
                                text = token.text,
                                fontSize = 26.sp,
                                fontFamily = FontFamily.Serif,
                                fontWeight = if (token.isOperator) FontWeight.Bold else FontWeight.Normal,
                                color = animColor,
                                modifier = Modifier.graphicsLayer {
                                    val s = if (isHighlighted) 1.15f else 1f
                                    scaleX = s
                                    scaleY = s
                                }
                            )
                        }
                    }
                }

                // Dòng mẹo nhớ với icon bóng đèn vector
                if (!mnemonic.isNullOrBlank()) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.Center,
                        modifier = Modifier.padding(top = 2.dp)
                    ) {
                        LightbulbCanvas(modifier = Modifier.size(14.dp))
                        Spacer(Modifier.width(6.dp))
                        Text(
                            text = mnemonic,
                            fontSize = 13.sp,
                            fontWeight = FontWeight.Medium,
                            color = TextPrimary,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis,
                            textAlign = TextAlign.Center
                        )
                    }
                }
            }
        }
    }
}

/**
 * Animated reveal container for each piece card / formula card.
 * fadeIn + translateY 20dp -> 0 + scale 0.96 -> 1, 450ms spring (dampingRatio 0.6).
 * Reserves its layout space when not visible so surrounding layout never jumps.
 * Blocks touch when not visible.
 */
@Composable
private fun StructureRevealContainer(
    visible: Boolean,
    modifier: Modifier = Modifier,
    delayMillis: Int = 0,
    content: @Composable () -> Unit
) {
    val alphaAnim = remember { Animatable(if (visible) 1f else 0f) }
    val transYAnim = remember { Animatable(if (visible) 0f else 20f) }
    val scaleAnim = remember { Animatable(if (visible) 1f else 0.96f) }

    LaunchedEffect(visible) {
        if (visible) {
            if (delayMillis > 0) delay(delayMillis.toLong())
            launch {
                alphaAnim.animateTo(
                    targetValue = 1f,
                    animationSpec = tween(durationMillis = 450, easing = LinearOutSlowInEasing)
                )
            }
            launch {
                transYAnim.animateTo(
                    targetValue = 0f,
                    animationSpec = spring(
                        dampingRatio = 0.6f,
                        stiffness = Spring.StiffnessLow
                    )
                )
            }
            launch {
                scaleAnim.animateTo(
                    targetValue = 1f,
                    animationSpec = spring(
                        dampingRatio = 0.6f,
                        stiffness = Spring.StiffnessLow
                    )
                )
            }
        } else {
            alphaAnim.snapTo(0f)
            transYAnim.snapTo(20f)
            scaleAnim.snapTo(0.96f)
        }
    }

    Box(
        modifier = modifier
            .graphicsLayer {
                alpha = alphaAnim.value
                translationY = transYAnim.value.dp.toPx()
                scaleX = scaleAnim.value
                scaleY = scaleAnim.value
            },
        contentAlignment = Alignment.Center
    ) {
        Box(
            modifier = if (alphaAnim.value < 0.95f) Modifier.pointerInput(Unit) {
                awaitPointerEventScope {
                    while (true) {
                        val event = awaitPointerEvent()
                        event.changes.forEach { it.consume() }
                    }
                }
            } else Modifier
        ) {
            content()
        }
    }
}

/**
 * Vector canvas drawing a cute jigsaw puzzle piece for the Cấu Tạo Chữ chip.
 */
@Composable
private fun PuzzlePieceCanvas(
    modifier: Modifier = Modifier,
    color: Color = StructureChipText
) {
    Canvas(modifier = modifier) {
        val w = size.width
        val h = size.height
        val path = Path().apply {
            moveTo(w * 0.15f, h * 0.15f)
            lineTo(w * 0.4f, h * 0.15f)
            // top knob
            cubicTo(w * 0.4f, 0f, w * 0.6f, 0f, w * 0.6f, h * 0.15f)
            lineTo(w * 0.85f, h * 0.15f)
            lineTo(w * 0.85f, h * 0.4f)
            // right tab
            cubicTo(w, h * 0.4f, w, h * 0.6f, w * 0.85f, h * 0.6f)
            lineTo(w * 0.85f, h * 0.85f)
            lineTo(w * 0.15f, h * 0.85f)
            close()
        }
        drawPath(path, color = color)
    }
}

/**
 * Vector canvas drawing a small lightbulb icon for mnemonics.
 */
@Composable
private fun LightbulbCanvas(
    modifier: Modifier = Modifier,
    color: Color = FormulaOperatorColor
) {
    Canvas(modifier = modifier) {
        val w = size.width
        val h = size.height
        // Bulb head circle
        drawCircle(
            color = color,
            radius = w * 0.35f,
            center = Offset(w * 0.5f, h * 0.38f)
        )
        // Bulb neck / base
        drawRoundRect(
            color = color,
            topLeft = Offset(w * 0.35f, h * 0.68f),
            size = Size(w * 0.3f, h * 0.24f),
            cornerRadius = CornerRadius(1.5.dp.toPx(), 1.5.dp.toPx())
        )
    }
}

private data class FormulaToken(
    val text: String,
    val isOperator: Boolean
)

private fun buildFormulaTokens(components: List<LessonComponent>, targetChar: String): List<FormulaToken> {
    if (components.isEmpty()) return emptyList()
    val list = mutableListOf<FormulaToken>()
    components.forEachIndexed { index, comp ->
        if (index > 0) {
            list.add(FormulaToken(" + ", isOperator = true))
        }
        list.add(FormulaToken(comp.component, isOperator = false))
    }
    list.add(FormulaToken(" = ", isOperator = true))
    list.add(FormulaToken(targetChar, isOperator = false))
    return list
}

private data class ComponentInfo(
    val name: String,
    val meaning: String?,
    val isSemantic: Boolean,
    val emoji: String,
)

/**
 * Maps Chinese radicals and components to concise, authentic Vietnamese descriptions.
 * Eliminates old generic boilerplate ("Gợi ý về nghĩa của chữ", "Giúp nhận diện hình dạng chữ").
 * Meanings are strictly <= 4 words.
 */
private fun getComponentInfo(comp: LessonComponent): ComponentInfo {
    return when (comp.component) {
        "亻", "人" -> ComponentInfo("Bộ nhân đứng", "Con người", true, "👤")
        "女" -> ComponentInfo("Bộ nữ", "Người phụ nữ", true, "👩")
        "子" -> ComponentInfo("Bộ tử", "Đứa trẻ, con", true, "👶")
        "尔" -> ComponentInfo("Thành phần 尔", null, false, "🧩")
        "口" -> ComponentInfo("Bộ khẩu", "Cái miệng", true, "👄")
        "日" -> ComponentInfo("Bộ nhật", "Mặt trời, ngày", true, "☀️")
        "月" -> ComponentInfo("Bộ nguyệt", "Mặt trăng, tháng", true, "🌙")
        "木" -> ComponentInfo("Bộ mộc", "Cây cối, gỗ", true, "🌳")
        "氵", "水" -> ComponentInfo("Bộ chấm thủy", "Nước sông suối", true, "💧")
        "火", "灬" -> ComponentInfo("Bộ hỏa", "Lửa, nhiệt", true, "🔥")
        "土" -> ComponentInfo("Bộ thổ", "Đất đai", true, "⛰️")
        "心", "忄" -> ComponentInfo("Bộ tâm", "Trái tim, tình cảm", true, "❤️")
        "言", "讠" -> ComponentInfo("Bộ ngôn", "Lời nói, ngôn ngữ", true, "💬")
        "手", "扌" -> ComponentInfo("Bộ thủ", "Bàn tay, động tác", true, "✋")
        "目" -> ComponentInfo("Bộ mục", "Con mắt, nhìn", true, "👀")
        "门", "門" -> ComponentInfo("Bộ môn", "Cửa cổng", true, "🚪")
        "山" -> ComponentInfo("Bộ sơn", "Núi non", true, "⛰️")
        "金", "钅" -> ComponentInfo("Bộ kim", "Kim loại, vàng", true, "🪙")
        "食", "饣" -> ComponentInfo("Bộ thực", "Ăn uống, thức ăn", true, "🍚")
        "犭" -> ComponentInfo("Bộ khuyển", "Loài vật, thú", true, "🐾")
        "辶" -> ComponentInfo("Bộ xước", "Đi lại, di chuyển", true, "🚶")
        "宀" -> ComponentInfo("Bộ miên", "Mái nhà", true, "🏠")
        "十" -> ComponentInfo("Bộ thập", "Số mười", true, "🔟")
        "一" -> ComponentInfo("Bộ nhất", "Số một", true, "1️⃣")
        "力" -> ComponentInfo("Bộ lực", "Sức mạnh", true, "💪")
        "又" -> ComponentInfo("Bộ hựu", "Lại nữa, bàn tay", false, "🧩")
        "寸" -> ComponentInfo("Bộ thốn", "Tấc, đơn vị đo", false, "📏")
        "白" -> ComponentInfo("Bộ bạch", "Màu trắng, sáng", true, "⚪")
        "田" -> ComponentInfo("Bộ điền", "Ruộng đất", true, "🌾")
        "糸", "纟" -> ComponentInfo("Bộ mịch", "Sợi tơ, kết nối", true, "🧵")
        "贝", "貝" -> ComponentInfo("Bộ bối", "Tiền của, báu vật", true, "💰")
        "车", "車" -> ComponentInfo("Bộ xa", "Xe cộ", true, "🚗")
        "马", "馬" -> ComponentInfo("Bộ mã", "Con ngựa", true, "🐎")
        "鸟", "鳥" -> ComponentInfo("Bộ điểu", "Con chim", true, "🐦")
        "鱼", "魚" -> ComponentInfo("Bộ ngư", "Con cá", true, "🐟")
        "虫" -> ComponentInfo("Bộ trùng", "Sâu bọ, côn trùng", true, "🐛")
        "雨" -> ComponentInfo("Bộ vũ", "Mưa thời tiết", true, "🌧️")
        "风", "風" -> ComponentInfo("Bộ phong", "Cơn gió", true, "💨")
        "父" -> ComponentInfo("Bộ phụ", "Người cha", true, "👨")
        "母" -> ComponentInfo("Bộ mẫu", "Người mẹ", true, "👩")
        "王", "玉" -> ComponentInfo("Bộ ngọc", "Ngọc quý, vua", true, "👑")
        "生" -> ComponentInfo("Bộ sinh", "Sinh sống, lớn lên", true, "🌱")
        "走", "赱" -> ComponentInfo("Bộ tẩu", "Đi, chạy nhanh", true, "🏃")
        "足" -> ComponentInfo("Bộ túc", "Chân, bước đi", true, "🦶")
        "禾" -> ComponentInfo("Bộ hòa", "Cây lúa lương thực", true, "🌾")
        "竹", "⺮" -> ComponentInfo("Bộ trúc", "Tre trúc", true, "🎋")
        "米" -> ComponentInfo("Bộ mễ", "Hạt gạo, thóc", true, "🍚")
        "巾" -> ComponentInfo("Bộ cân", "Khăn vải", true, "🧣")
        "广" -> ComponentInfo("Bộ quảng", "Mái nhà rộng", true, "🏠")
        "夕" -> ComponentInfo("Bộ tịch", "Buổi chiều tối", true, "🌆")
        "大" -> ComponentInfo("Bộ đại", "To lớn", true, "🐘")
        "小" -> ComponentInfo("Bộ tiểu", "Nhỏ bé", true, "🐜")
        "弓" -> ComponentInfo("Bộ cung", "Cây cung tên", true, "🏹")
        "斤" -> ComponentInfo("Bộ cân", "Cái rìu", false, "🪓")
        "方" -> ComponentInfo("Bộ phương", "Phương hướng, vuông", false, "🧭")
        "毛" -> ComponentInfo("Bộ mao", "Lông tóc", true, "🪶")
        "气" -> ComponentInfo("Bộ khí", "Hơi thở, không khí", true, "💨")
        "牛", "牜" -> ComponentInfo("Bộ ngưu", "Con trâu bò", true, "🐂")
        "犬" -> ComponentInfo("Bộ khuyển", "Con chó", true, "🐕")
        "甘" -> ComponentInfo("Bộ cam", "Vị ngọt", true, "🍬")
        "立" -> ComponentInfo("Bộ lập", "Đứng thẳng", true, "🧍")
        "羊", "⺶" -> ComponentInfo("Bộ dương", "Con dê, cừu", true, "🐑")
        "羽" -> ComponentInfo("Bộ vũ", "Lông vũ, cánh", true, "🪶")
        "耳" -> ComponentInfo("Bộ nhĩ", "Cái tai, lắng nghe", true, "👂")
        "舌" -> ComponentInfo("Bộ thiệt", "Cái lưỡi", true, "👅")
        "舟" -> ComponentInfo("Bộ chu", "Chiếc thuyền", true, "⛵")
        "艹", "艸" -> ComponentInfo("Bộ thảo", "Cỏ cây hoa lá", true, "🌿")
        "衣", "衤" -> ComponentInfo("Bộ y", "Áo quần trang phục", true, "👗")
        "见", "見" -> ComponentInfo("Bộ kiến", "Trông thấy, gặp", true, "👁️")
        "辛" -> ComponentInfo("Bộ tân", "Cay đắng, vất vả", true, "🌶️")
        "邑", "阝" -> ComponentInfo("Bộ ấp", "Vùng đất, thành thị", true, "🏘️")
        "酉" -> ComponentInfo("Bộ dậu", "Vò rượu, say sưa", true, "🍶")
        "里" -> ComponentInfo("Bộ lý", "Dặm đường, làng xóm", true, "🏡")
        "青" -> ComponentInfo("Bộ thanh", "Màu xanh biếc", true, "🟦")
        "香" -> ComponentInfo("Bộ hương", "Mùi hương thơm", true, "🌸")
        "鬼" -> ComponentInfo("Bộ quỷ", "Ma quỷ", true, "👻")
        "黄" -> ComponentInfo("Bộ hoàng", "Màu vàng", true, "🟡")
        "黑" -> ComponentInfo("Bộ hắc", "Màu đen tối", true, "⚫")
        "龙", "龍" -> ComponentInfo("Bộ long", "Con rồng", true, "🐉")
        else -> {
            val isSemantic = comp.role in listOf("SEMANTIC_RADICAL", "SEMANTIC")
            val defaultName = if (isSemantic) "Bộ ${comp.component}" else "Thành phần ${comp.component}"
            val raw = comp.explanation.text?.trim()
            val cleanMeaning = raw?.takeIf {
                !it.contains("Gợi ý") && !it.contains("Giúp") && !it.contains("nhận diện") && !it.contains("hình dạng")
            }
            ComponentInfo(defaultName, cleanMeaning, isSemantic, if (isSemantic) "💡" else "🧩")
        }
    }
}

/**
 * Returns a concise memory aid (<= 10 words).
 */
private fun resolveMnemonic(word: RoadmapWord, lesson: RoadmapLesson): String? {
    return when (word.simplified) {
        "好" -> "Mẹ có con bên cạnh → điều tốt đẹp"
        "你" -> "Người bạn nhỏ bên cạnh → người bạn"
        "他" -> "Người đứng bên cạnh → anh ấy"
        "她" -> "Người phụ nữ bên cạnh → cô ấy"
        "吗", "嗎" -> "Thêm miệng hỏi han → câu hỏi"
        "们", "們" -> "Nhiều người đứng cạnh cửa → chúng tôi"
        else -> {
            val noteText = lesson.notes.takeIf { it.available }?.text?.trim()
            if (!noteText.isNullOrBlank()) {
                val words = noteText.split(Regex("\\s+"))
                if (words.size > 10) words.take(10).joinToString(" ") else noteText
            } else null
        }
    }
}

/**
 * Tiger mascot speech bubble messages according to the current reveal step.
 */
private fun getMascotMessage(step: Int, components: List<LessonComponent>, finalStep: Int): String {
    return when {
        step == 0 -> "Chữ này được ghép từ nhiều mảnh, cùng khám phá nhé! 🧩"
        step > components.size || (components.isEmpty() && step >= finalStep) -> "Hiểu cách ghép thì nhớ lâu hơn nhiều đó 🧠"
        step in 1..components.size -> {
            val idx = step - 1
            val comp = components[idx]
            val info = getComponentInfo(comp)
            val hint = info.meaning ?: info.name
            "Mảnh $step/${components.size}: ${comp.component} $hint ${info.emoji}"
        }
        else -> "Hiểu cách ghép thì nhớ lâu hơn nhiều đó 🧠"
    }
}
