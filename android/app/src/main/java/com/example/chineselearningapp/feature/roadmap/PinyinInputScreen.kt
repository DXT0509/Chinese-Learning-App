package com.example.chineselearningapp.feature.roadmap

import android.widget.Toast
import androidx.activity.compose.BackHandler
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.keyframes
import androidx.compose.animation.core.tween
import androidx.compose.animation.slideInVertically
import androidx.compose.animation.slideOutVertically
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.focus.onFocusChanged
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.layout.boundsInRoot
import androidx.compose.ui.layout.onGloballyPositioned
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.TextRange
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardCapitalization
import androidx.compose.ui.text.input.TextFieldValue
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.em
import androidx.compose.ui.unit.sp
import com.example.chineselearningapp.R
import com.example.chineselearningapp.core.datastore.AppPreferences
import com.example.chineselearningapp.core.designsystem.*
import com.example.chineselearningapp.domain.model.RoadmapWord
import kotlinx.coroutines.launch

private val SUCCESS_TITLES = listOf("Chuẩn rồi!", "Tuyệt vời!", "Giỏi lắm!")

private data class ToneKeyData(
    val tone: Int,
    val char: String,
    val label: String
)

private val TONE_KEYS = listOf(
    ToneKeyData(1, "ā", "thanh 1"),
    ToneKeyData(2, "á", "thanh 2"),
    ToneKeyData(3, "ǎ", "thanh 3"),
    ToneKeyData(4, "à", "thanh 4"),
    ToneKeyData(5, "a", "nhẹ")
)

@Composable
internal fun PinyinInputScreen(
    word: RoadmapWord,
    state: LessonState,
    enabled: Boolean,
    edit: (String) -> Unit,
    check: () -> Unit,
    next: () -> Unit,
    back: () -> Unit,
    modifier: Modifier = Modifier,
    progress: Float = 4f / 9f,
    onKnownWord: () -> Unit = {},
    onLeaveLesson: () -> Unit = {},
    onPauseLesson: () -> Unit = {},
    onResumeLesson: () -> Unit = {},
    status: @Composable () -> Unit = {}
) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    val focusManager = LocalFocusManager.current
    val focusRequester = remember { FocusRequester() }
    val scrollState = rememberScrollState()

    val appPreferences = remember(context) { AppPreferences(context.applicationContext) }
    val audioVolume by appPreferences.audioVolume.collectAsState(initial = 1.0f)
    val speech = rememberWordSpeech(word.simplified, volume = audioVolume)
    val feedbackPlayer = rememberWritingFeedbackPlayer { audioVolume }

    var showSettingsSheet by rememberSaveable { mutableStateOf(false) }
    var attemptCount by rememberSaveable(word.id) { mutableIntStateOf(0) }

    var showSuccessBanner by remember { mutableStateOf(false) }
    var showErrorBanner by remember { mutableStateOf(false) }
    val isBannerShowing = showSuccessBanner || showErrorBanner

    var successTitle by remember { mutableStateOf(SUCCESS_TITLES.first()) }
    var isFieldCorrect by remember { mutableStateOf(false) }
    var isFieldError by remember { mutableStateOf(false) }
    var isFocused by remember { mutableStateOf(false) }

    var textFieldValue by rememberSaveable(stateSaver = TextFieldValue.Saver) {
        mutableStateOf(TextFieldValue(state.pinyin, TextRange(state.pinyin.length)))
    }

    // Autoplay audio once upon entering the screen
    var autoPlayed by rememberSaveable(word.id) { mutableStateOf(false) }
    LaunchedEffect(speech.ready) {
        if (speech.ready && !autoPlayed) {
            autoPlayed = true
            speech.speak()
        }
    }

    // Animation drivers
    val shakeAnim = remember { Animatable(0f) }
    val scaleAnim = remember { Animatable(1f) }
    val speakerRippleAnim = remember { Animatable(0f) }
    var confettiTrigger by remember { mutableIntStateOf(0) }
    var fieldCenter by remember { mutableStateOf(Offset.Zero) }

    fun handleBack() {
        back()
    }

    BackHandler(enabled = !showSettingsSheet) {
        handleBack()
    }

    LaunchedEffect(showSettingsSheet) {
        if (showSettingsSheet) {
            speech.stop()
            onPauseLesson()
        } else {
            onResumeLesson()
        }
    }

    fun handleCheck() {
        val input = textFieldValue.text
        if (input.isBlank() || isBannerShowing) return

        focusManager.clearFocus()

        val isCorrect = PinyinToneConverter.isCorrectAnswer(input, word.pinyin)
        if (isCorrect) {
            isFieldError = false
            isFieldCorrect = true
            check()
            feedbackPlayer.playCorrect()
            confettiTrigger++
            coroutineScope.launch {
                scaleAnim.snapTo(1f)
                scaleAnim.animateTo(
                    targetValue = 1f,
                    animationSpec = keyframes {
                        durationMillis = 700
                        1f at 0
                        1.03f at 350
                        1f at 700
                    }
                )
            }
            successTitle = SUCCESS_TITLES.random()
            showSuccessBanner = true
        } else {
            attemptCount++
            isFieldCorrect = false
            isFieldError = true
            check()
            feedbackPlayer.playIncorrect()
            speech.speak()

            coroutineScope.launch {
                shakeAnim.snapTo(0f)
                shakeAnim.animateTo(
                    targetValue = 0f,
                    animationSpec = keyframes {
                        durationMillis = 500
                        0f at 0
                        -10f at 60
                        10f at 140
                        -8f at 220
                        8f at 300
                        -4f at 380
                        0f at 500
                    }
                )
            }

            if (attemptCount == 1) {
                coroutineScope.launch {
                    speakerRippleAnim.snapTo(0f)
                    speakerRippleAnim.animateTo(
                        targetValue = 3f,
                        animationSpec = tween(durationMillis = 1800, easing = LinearEasing)
                    )
                }
            }
            showErrorBanner = true
        }
    }

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(Surface0)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .imePadding()
        ) {
            // 1. LessonTopBar (progress according to scene)
            LessonTopBar(
                progress = progress,
                canGoBack = true,
                onBack = ::handleBack,
                onSettings = { showSettingsSheet = true }
            )

            status()

            Column(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth()
                    .verticalScroll(scrollState)
                    .padding(horizontal = 20.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // 2. Chip "🔤 GÕ PINYIN": căn giữa, margin top 14dp, nền #e8f0ff, viền 1.5dp #b9c9f0, chữ #2b4a9a 11sp weight 500
                Box(
                    modifier = Modifier
                        .padding(top = 14.dp)
                        .background(StructureChipBg, RoundedCornerShape(20.dp))
                        .border(1.5.dp, StructureChipBorder, RoundedCornerShape(20.dp))
                        .padding(horizontal = 12.dp, vertical = 4.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = "🔤 GÕ PINYIN",
                        color = StructureChipText,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Medium,
                        letterSpacing = 0.06.em
                    )
                }

                Spacer(modifier = Modifier.height(14.dp))

                // 3. Thẻ chữ Hán: 150×150dp, bo 24dp, nền trắng, viền 2dp #d6e9de, bottom shadow 6dp #c8e0d2 + elevation mờ xanh
                Box(
                    modifier = Modifier.size(width = 150.dp, height = 156.dp),
                    contentAlignment = Alignment.TopCenter
                ) {
                    // Bottom shadow
                    Box(
                        modifier = Modifier
                            .offset(y = 6.dp)
                            .size(150.dp)
                            .background(LessonShadow, RoundedCornerShape(24.dp))
                    )
                    // Surface
                    Box(
                        modifier = Modifier
                            .size(150.dp)
                            .shadow(
                                elevation = 6.dp,
                                shape = RoundedCornerShape(24.dp),
                                spotColor = Color(0xFF34C478).copy(alpha = 0.25f),
                                ambientColor = Color(0xFF34C478).copy(alpha = 0.15f)
                            )
                            .background(Color.White, RoundedCornerShape(24.dp))
                            .border(2.dp, LessonBorder, RoundedCornerShape(24.dp)),
                        contentAlignment = Alignment.Center
                    ) {
                        TianZiGeGridCanvas(
                            modifier = Modifier.fillMaxSize(),
                            inset = 8.dp,
                            cornerRadius = 16.dp
                        )
                        Text(
                            text = word.simplified,
                            fontSize = 88.sp,
                            fontFamily = FontFamily.Serif,
                            fontWeight = FontWeight.Normal,
                            color = TextPrimary
                        )
                    }
                }

                // 4. Nút loa tròn: 54dp, nền Primary, bottom shadow 4dp #0f5533, icon loa trắng 26dp, căn giữa, margin top 14dp
                val speakerInteractionSource = remember { MutableInteractionSource() }
                val isSpeakerPressed by speakerInteractionSource.collectIsPressedAsState()
                val speakerPressed = isSpeakerPressed && !isBannerShowing

                Box(
                    modifier = Modifier
                        .padding(top = 14.dp)
                        .size(width = 54.dp, height = 58.dp),
                    contentAlignment = Alignment.TopCenter
                ) {
                    // Wave ripple when SAI lần 1
                    if (speakerRippleAnim.value in 0.001f..2.999f) {
                        val cycle = speakerRippleAnim.value % 1f
                        val rippleScale = 0.9f + 0.7f * cycle
                        val rippleAlpha = (1f - cycle) * 0.55f
                        Box(
                            modifier = Modifier
                                .size(54.dp)
                                .graphicsLayer {
                                    scaleX = rippleScale
                                    scaleY = rippleScale
                                    alpha = rippleAlpha
                                }
                                .background(Primary, CircleShape)
                        )
                    }

                    // Shadow 4dp
                    if (!speakerPressed) {
                        Box(
                            modifier = Modifier
                                .offset(y = 4.dp)
                                .size(54.dp)
                                .background(PrimaryDark, CircleShape)
                        )
                    }

                    // Surface
                    Box(
                        modifier = Modifier
                            .offset(y = if (speakerPressed) 3.dp else 0.dp)
                            .size(54.dp)
                            .background(Primary, CircleShape)
                            .clickable(
                                interactionSource = speakerInteractionSource,
                                indication = null,
                                enabled = !isBannerShowing && enabled,
                                onClick = { speech.speak() }
                            ),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            painter = painterResource(R.drawable.ic_volume),
                            contentDescription = "Nghe lại phát âm",
                            tint = Color.White,
                            modifier = Modifier.size(26.dp)
                        )
                    }
                }

                // 5. Ô nhập (PinyinField): margin top 18dp
                val fieldBorderColor = when {
                    isFieldCorrect -> CorrectGlowColor
                    isFieldError -> ErrorColor
                    isFocused -> CorrectGlowColor
                    else -> LessonBorder
                }

                val fieldShadowColor = when {
                    isFieldCorrect -> CorrectGlowColor
                    isFieldError -> DangerCardShadow
                    isFocused -> PinyinBorder
                    else -> LessonShadow
                }

                val outerRingWidth = when {
                    isFieldCorrect -> 5.dp
                    isFieldError -> 4.dp
                    isFocused -> 4.dp
                    else -> 0.dp
                }

                val outerRingColor = when {
                    isFieldCorrect -> CorrectGlowColor.copy(alpha = 0.25f)
                    isFieldError -> ErrorColor.copy(alpha = 0.15f)
                    isFocused -> CorrectGlowColor.copy(alpha = 0.18f)
                    else -> Color.Transparent
                }

                val fieldTextColor = when {
                    isFieldCorrect -> PrimaryDark
                    isFieldError -> PinyinErrorText
                    else -> TextPrimary
                }

                Box(
                    modifier = Modifier
                        .padding(top = 18.dp)
                        .fillMaxWidth()
                        .graphicsLayer {
                            translationX = shakeAnim.value.dp.toPx()
                            scaleX = scaleAnim.value
                            scaleY = scaleAnim.value
                        }
                        .onGloballyPositioned { coordinates ->
                            val bounds = coordinates.boundsInRoot()
                            fieldCenter = bounds.center
                        },
                    contentAlignment = Alignment.Center
                ) {
                    // Outer glow ring
                    if (outerRingWidth > 0.dp) {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(65.dp + outerRingWidth * 2)
                                .background(outerRingColor, RoundedCornerShape(18.dp + outerRingWidth))
                        )
                    }

                    // 3D Box container
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(65.dp),
                        contentAlignment = Alignment.TopCenter
                    ) {
                        // Bottom shadow 5dp
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .offset(y = 5.dp)
                                .height(60.dp)
                                .background(fieldShadowColor, RoundedCornerShape(18.dp))
                        )

                        // Input field surface
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(60.dp)
                                .background(Color.White, RoundedCornerShape(18.dp))
                                .border(2.dp, fieldBorderColor, RoundedCornerShape(18.dp))
                                .padding(horizontal = 16.dp),
                            contentAlignment = Alignment.Center
                        ) {
                            BasicTextField(
                                value = textFieldValue,
                                onValueChange = { newTv ->
                                    if (!isBannerShowing) {
                                        val processed = PinyinToneConverter.processTextFieldValue(newTv)
                                        textFieldValue = processed
                                        edit(processed.text)
                                        if (isFieldError) isFieldError = false
                                    }
                                },
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .focusRequester(focusRequester)
                                    .onFocusChanged { focusState ->
                                        isFocused = focusState.isFocused
                                    }
                                    .testTag("lesson_pinyin"),
                                enabled = !isBannerShowing && enabled,
                                singleLine = true,
                                keyboardOptions = KeyboardOptions(
                                    autoCorrectEnabled = false,
                                    capitalization = KeyboardCapitalization.None
                                ),
                                keyboardActions = KeyboardActions(
                                    onDone = { handleCheck() }
                                ),
                                textStyle = TextStyle(
                                    fontSize = 30.sp,
                                    fontWeight = FontWeight.Medium,
                                    color = fieldTextColor,
                                    textAlign = TextAlign.Center
                                ),
                                cursorBrush = SolidColor(Primary),
                                decorationBox = { innerTextField ->
                                    Box(
                                        modifier = Modifier.fillMaxWidth(),
                                        contentAlignment = Alignment.Center
                                    ) {
                                        if (textFieldValue.text.isEmpty()) {
                                            Text(
                                                text = "gõ pinyin…",
                                                fontSize = 20.sp,
                                                color = PinyinPlaceholder,
                                                textAlign = TextAlign.Center
                                            )
                                        }
                                        innerTextField()
                                    }
                                }
                            )
                        }
                    }
                }

                // 6. Thanh phím dấu thanh (ToneBar): margin top 14dp, 5 phím ngang bằng nhau, gap 8dp
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(top = 14.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    for (item in TONE_KEYS) {
                        ToneKeyButton(
                            data = item,
                            enabled = !isBannerShowing && enabled,
                            onClick = {
                                val updated = PinyinToneConverter.applyToneToCurrentSyllable(textFieldValue, item.tone)
                                textFieldValue = updated
                                edit(updated.text)
                                if (isFieldError) isFieldError = false
                            },
                            modifier = Modifier.weight(1f)
                        )
                    }
                }

                // Dòng gợi ý dưới ToneBar: "Hoặc gõ số: hao3 → hǎo" 11sp #7a9a88, căn giữa, margin top 8dp
                Text(
                    text = "Hoặc gõ số: hao3 → hǎo",
                    fontSize = 11.sp,
                    color = SubtitleCaptionColor,
                    textAlign = TextAlign.Center,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(top = 8.dp)
                )

                // 7. Spacer, hàng mascot (TigerMascot nhỏ + bubble)
                Spacer(modifier = Modifier.weight(1f).defaultMinSize(minHeight = 20.dp))

                TigerMascot(
                    message = "Nghe lại rồi nhập pinyin có dấu thanh nhé! 👂",
                    modifier = Modifier.fillMaxWidth()
                )

                Spacer(modifier = Modifier.height(14.dp))

                // 8. PrimaryButton 3D "Kiểm tra": disabled (opacity 0.4) khi ô nhập trống
                LessonPrimary3DButton(
                    text = "Kiểm tra",
                    onClick = { handleCheck() },
                    enabled = !isBannerShowing && textFieldValue.text.isNotBlank() && enabled,
                    modifier = Modifier
                        .fillMaxWidth()
                        .testTag("pinyin_check_button")
                )

                Spacer(modifier = Modifier.height(18.dp).navigationBarsPadding())
            }
        }

        // Confetti Canvas Overlay
        ConfettiOverlay(
            trigger = confettiTrigger,
            originCenter = fieldCenter
        )

        // ResultBanner: Correct
        AnimatedVisibility(
            visible = showSuccessBanner,
            enter = slideInVertically(initialOffsetY = { it }),
            exit = slideOutVertically(targetOffsetY = { it }),
            modifier = Modifier.align(Alignment.BottomCenter)
        ) {
            ResultBanner(
                isCorrect = true,
                title = successTitle,
                subtitle = "Nhớ cả dấu thanh, đỉnh thật 👏",
                buttonText = "Tiếp tục",
                onButton = { next() }
            )
        }

        // ResultBanner: Incorrect
        AnimatedVisibility(
            visible = showErrorBanner,
            enter = slideInVertically(initialOffsetY = { it }),
            exit = slideOutVertically(targetOffsetY = { it }),
            modifier = Modifier.align(Alignment.BottomCenter)
        ) {
            if (attemptCount == 1) {
                // SAI lần 1
                ResultBanner(
                    isCorrect = false,
                    title = "Chưa đúng rồi",
                    subtitle = "Nghe lại rồi thử nữa nhé 👂",
                    buttonText = "Thử lại",
                    onButton = {
                        showErrorBanner = false
                        textFieldValue = textFieldValue.copy(
                            selection = TextRange(0, textFieldValue.text.length)
                        )
                        focusRequester.requestFocus()
                    }
                )
            } else {
                // SAI lần 2: Hiện ĐÁP ÁN
                ResultBanner(
                    isCorrect = false,
                    title = "Đáp án là",
                    answerChip = word.pinyin,
                    onPlayAudio = { speech.speak() },
                    subtitle = "Ghi nhớ nhé, lần sau sẽ nhớ thôi!",
                    buttonText = "Tiếp tục",
                    onButton = { next() }
                )
            }
        }

        // Lesson Settings BottomSheet
        if (showSettingsSheet) {
            LessonSettingsSheet(
                onKnownWord = onKnownWord,
                onLeaveLesson = onLeaveLesson,
                onDismiss = { showSettingsSheet = false }
            )
        }
    }
}

@Composable
private fun ToneKeyButton(
    data: ToneKeyData,
    enabled: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val interactionSource = remember { MutableInteractionSource() }
    val isPressed by interactionSource.collectIsPressedAsState()
    val pressed = isPressed && enabled
    val offsetY = if (pressed) 3.dp else 0.dp
    val bgColor = if (pressed) PinyinBg else Color.White

    Box(
        modifier = modifier.height(53.dp),
        contentAlignment = Alignment.TopCenter
    ) {
        if (!pressed) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .offset(y = 3.dp)
                    .height(50.dp)
                    .background(LessonShadow, RoundedCornerShape(14.dp))
            )
        }
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .offset(y = offsetY)
                .height(50.dp)
                .background(bgColor, RoundedCornerShape(14.dp))
                .border(2.dp, LessonBorder, RoundedCornerShape(14.dp))
                .clickable(
                    interactionSource = interactionSource,
                    indication = null,
                    enabled = enabled,
                    onClick = onClick
                ),
            contentAlignment = Alignment.Center
        ) {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                Text(
                    text = data.char,
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Medium,
                    color = Primary
                )
                Text(
                    text = data.label,
                    fontSize = 9.sp,
                    color = SubtitleCaptionColor
                )
            }
        }
    }
}
