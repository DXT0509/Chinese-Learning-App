package com.example.chineselearningapp.core.navigation

import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.core.tween
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.lifecycle.createSavedStateHandle
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.lifecycle.viewmodel.initializer
import androidx.lifecycle.viewmodel.viewModelFactory
import androidx.navigation.NavType
import androidx.navigation.navArgument
import com.example.chineselearningapp.feature.dictionary.*
import com.example.chineselearningapp.feature.vocabulary.*
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import com.example.chineselearningapp.feature.dictionary.handwriting.*
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.navigation.compose.*
import com.example.chineselearningapp.R
import com.example.chineselearningapp.core.designsystem.*
import com.example.chineselearningapp.feature.auth.*
import com.example.chineselearningapp.feature.home.HomeScreen
import com.example.chineselearningapp.feature.lesson.*
import com.example.chineselearningapp.feature.roadmap.*
import com.example.chineselearningapp.feature.learning.LearningScreen
import com.example.chineselearningapp.feature.review.*
import com.example.chineselearningapp.feature.profile.ProfileScreen

@OptIn(ExperimentalMaterial3Api::class)
@Composable
internal fun ProtectedGraph(state: SessionState, actions: SessionActions,
    connectivity: ConnectivityState, retryConnection: () -> Unit, lessonViewModel: LessonPlayerViewModel?, dictionaryRepository: com.example.chineselearningapp.domain.repository.DictionaryRepository? = null,
    handwritingFactory: (() -> HandwritingRecognizer)? = null,
    wordbookRepository: com.example.chineselearningapp.domain.repository.PersonalVocabularyRepository? = null,
    reviewRepository: com.example.chineselearningapp.domain.repository.ReviewRepository? = null) {
    val controller = rememberNavController()
    val entry by controller.currentBackStackEntryAsState()
    val destination = Destination.entries.firstOrNull { it.name == entry?.destination?.route }
    val topLevel = destination in mainDestinations
    val playerOpen = entry?.destination?.route == "player"
    val open: (Destination) -> Unit = { target ->
        if (target in mainDestinations) controller.openMainDestination(target)
        else controller.navigate(target.name) { launchSingleTop = true }
    }
    Scaffold(containerColor = MaterialTheme.colorScheme.surface.copy(alpha = 0f),
        bottomBar = { if (topLevel) MainBottomBar(destination, open) },
        topBar = {
            if (!topLevel && !playerOpen && destination != null) {
                TopAppBar(title = { Text(stringResource(destination.title)) }, navigationIcon = {
                    TextButton(onClick = { controller.popBackStack() }) { Text(stringResource(R.string.screen_back)) }
                }, colors = TopAppBarDefaults.topAppBarColors(containerColor = MaterialTheme.colorScheme.surface.copy(alpha = 0f)))
            }
        }) { padding ->
        NavHost(controller, startDestination = Destination.Home.name, modifier = Modifier.padding(padding),
            enterTransition = { fadeIn(tween(180)) }, exitTransition = { fadeOut(tween(120)) }) {
            composable(Destination.Home.name) {
                HomeScreen(state, { open(Destination.Lessons) }, { open(Destination.Learning) },
                    { open(Destination.Vocabulary) }, { open(Destination.Review) }, { open(Destination.Profile) },
                    actions.reload)
            }
            composable(Destination.Lessons.name) {
                PreviewLessonsScreen(state, { version ->
                    if (lessonViewModel == null) actions.start(version) else {
                        lessonViewModel.open(version)
                        controller.navigate("player") { launchSingleTop = true }
                    }
                }, { run ->
                    if (lessonViewModel == null) actions.resume(run) else {
                        lessonViewModel.open(null, run)
                        controller.navigate("player") { launchSingleTop = true }
                    }
                }, actions.checkpoint, actions.reload)
            }
            composable("player") {
                if (lessonViewModel != null) {
                    val player by lessonViewModel.state.collectAsStateWithLifecycle()
                    LaunchedEffect(player.loading, player.bundle, player.error) {
                        // A process restart may restore this route without its in-memory run.
                        if (!player.loading && player.bundle == null && player.error == null) controller.popBackStack()
                    }
                    LaunchedEffect(player.closed, player.expired) {
                        if (player.expired) actions.reload()
                        else if (player.closed) { controller.popBackStack(); actions.reload() }
                    }
                    LessonPlayerScreen(player, lessonViewModel::move, lessonViewModel::exit,
                        lessonViewModel::retry, lessonViewModel::persist, lessonViewModel::ink, lessonViewModel::loadMedia)
                }
            }
            composable(Destination.Roadmap.name) {
                PageColumn { RoadmapScreen(connectivity, retryConnection) }
            }
            composable(Destination.Learning.name) {
                LearningScreen({ open(Destination.Lessons) }, { open(Destination.Roadmap) }, {
                    controller.navigate(DICTIONARY_SEARCH_ROUTE) { launchSingleTop = true }
                }, { open(Destination.Vocabulary) })
            }
            composable(DICTIONARY_SEARCH_ROUTE) { backStackEntry ->
                if (dictionaryRepository != null) {
                    val model: DictionarySearchViewModel = viewModel(viewModelStoreOwner = backStackEntry,
                        factory = viewModelFactory { initializer {
                            DictionarySearchViewModel(dictionaryRepository, createSavedStateHandle())
                        } })
                    val search by model.state.collectAsStateWithLifecycle()
                    val handwriting: HandwritingViewModel? = if (handwritingFactory == null) null else
                        viewModel(viewModelStoreOwner = backStackEntry, factory = viewModelFactory {
                            initializer { HandwritingViewModel(handwritingFactory()) }
                        })
                    LaunchedEffect(search.phase) { if (search.phase == DictionaryPhase.Expired) actions.reload() }
                    DictionarySearchScreen(search, model::edit, model::retry, model::loadMore, {
                        controller.navigate(dictionaryDetailRoute(it)) { launchSingleTop = true }
                    }, { controller.popBackStack() }, handwriting)
                }
            }
            composable(DICTIONARY_DETAIL_ROUTE, arguments = listOf(navArgument("entryId") { type = NavType.StringType })) { backStackEntry ->
                if (dictionaryRepository != null) {
                    val model: DictionaryDetailViewModel = viewModel(viewModelStoreOwner = backStackEntry,
                        factory = viewModelFactory { initializer {
                            DictionaryDetailViewModel(dictionaryRepository, createSavedStateHandle())
                        } })
                    val detail by model.state.collectAsStateWithLifecycle()
                    LaunchedEffect(detail.phase) { if (detail.phase == DictionaryPhase.Expired) actions.reload() }
                    val savedModel: SavedEntryViewModel? = wordbookRepository?.let { repository ->
                        viewModel(viewModelStoreOwner = backStackEntry, factory = viewModelFactory { initializer {
                            SavedEntryViewModel(repository, checkNotNull(backStackEntry.arguments?.getString("entryId")))
                        } })
                    }
                    val saved = savedModel?.state?.collectAsStateWithLifecycle()?.value
                    LaunchedEffect(saved?.expired) { if (saved?.expired == true) actions.reload() }
                    DictionaryDetailScreen(detail, model::retry, { controller.popBackStack() }) {
                        if (saved != null) SavedVocabularyAction(saved, savedModel::save, savedModel::refresh)
                    }
                }
            }
            composable(Destination.Review.name) { backStackEntry ->
                if (reviewRepository != null) {
                    // The protected graph owns the attempt, including when Back pops this tab.
                    // SessionNavigation discards this owner on logout or identity change.
                    val reviewOwner = remember(backStackEntry) { controller.getBackStackEntry(controller.graph.id) }
                    val model: ReviewViewModel = viewModel(viewModelStoreOwner = reviewOwner,
                        factory = viewModelFactory { initializer {
                            ReviewViewModel(reviewRepository, createSavedStateHandle(), checkNotNull(state.account).id)
                        } })
                    val review by model.state.collectAsStateWithLifecycle()
                    LaunchedEffect(review.signedOut) { if (review.signedOut) actions.reload() }
                    DisposableEffect(backStackEntry, model) {
                        val observer = LifecycleEventObserver { _, event ->
                            if (event == Lifecycle.Event.ON_RESUME) model.onResume()
                        }
                        backStackEntry.lifecycle.addObserver(observer)
                        onDispose { backStackEntry.lifecycle.removeObserver(observer) }
                    }
                    val ink: ReviewHandwritingViewModel? = if (handwritingFactory == null) null else
                        viewModel(viewModelStoreOwner = reviewOwner, factory = viewModelFactory { initializer {
                            ReviewHandwritingViewModel(handwritingFactory(), createSavedStateHandle(), checkNotNull(state.account).id)
                        } })
                    ReviewScreen(review, model, ink, onLearnNewWords = { open(Destination.Learning) })
                }
            }
            composable(Destination.Profile.name) { ProfileScreen(state, actions.logout) }
            composable(Destination.Vocabulary.name) { backStackEntry ->
                if (wordbookRepository != null) {
                    val model: PersonalVocabularyViewModel = viewModel(viewModelStoreOwner = backStackEntry,
                        factory = viewModelFactory { initializer {
                            PersonalVocabularyViewModel(wordbookRepository, createSavedStateHandle())
                        } })
                    val words by model.state.collectAsStateWithLifecycle()
                    LaunchedEffect(words.expired) { if (words.expired) actions.reload() }
                    DisposableEffect(backStackEntry, model) {
                        val observer = LifecycleEventObserver { _, event ->
                            if (event == Lifecycle.Event.ON_RESUME) model.refresh()
                        }
                        backStackEntry.lifecycle.addObserver(observer)
                        onDispose { backStackEntry.lifecycle.removeObserver(observer) }
                    }
                    MyVocabularyScreen(words, model::edit, model::refresh, model::more,
                        { controller.navigate(dictionaryDetailRoute(it)) },
                        { controller.navigate(DICTIONARY_SEARCH_ROUTE) { launchSingleTop = true } },
                        model::askRemove, model::cancelRemove, model::confirmRemove)
                }
            }
        }
    }
}
