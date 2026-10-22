package com.example.chineselearningapp

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.SystemBarStyle
import androidx.activity.viewModels
import com.example.chineselearningapp.core.navigation.AppNavigation
import com.example.chineselearningapp.feature.roadmap.ConnectivityViewModel
import com.example.chineselearningapp.ui.theme.ChineseLearningAppTheme
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    private val connectivityViewModel: ConnectivityViewModel by viewModels()
    private val sessionViewModel: com.example.chineselearningapp.feature.auth.SessionViewModel by viewModels()

    private val lessonViewModel: com.example.chineselearningapp.feature.lesson.LessonPlayerViewModel by viewModels()

    @javax.inject.Inject lateinit var dictionaryRepository: com.example.chineselearningapp.domain.repository.DictionaryRepository
    @javax.inject.Inject lateinit var handwritingRecognizers: javax.inject.Provider<com.example.chineselearningapp.feature.dictionary.handwriting.MlKitHandwritingRecognizer>

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge(
            statusBarStyle = SystemBarStyle.light(android.graphics.Color.TRANSPARENT, android.graphics.Color.BLACK),
            navigationBarStyle = SystemBarStyle.light(android.graphics.Color.TRANSPARENT, android.graphics.Color.BLACK)
        )
        setContent {
            ChineseLearningAppTheme { AppNavigation(connectivityViewModel, sessionViewModel, lessonViewModel, dictionaryRepository, { handwritingRecognizers.get() }) }
        }
    }
}
