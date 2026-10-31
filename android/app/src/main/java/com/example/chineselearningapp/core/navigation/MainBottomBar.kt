package com.example.chineselearningapp.core.navigation

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.navigation.NavHostController
import androidx.navigation.NavGraph.Companion.findStartDestination
import com.example.chineselearningapp.R

internal val mainDestinations = listOf(Destination.Home, Destination.Learning, Destination.Review, Destination.Profile)

internal fun NavHostController.openMainDestination(destination: Destination) {
    if (currentDestination?.route == destination.name) return
    navigate(destination.name) {
        popUpTo(graph.findStartDestination().id) { saveState = true }
        launchSingleTop = true
        restoreState = true
    }
}

@Composable
internal fun MainBottomBar(selected: Destination?, open: (Destination) -> Unit) {
    com.example.chineselearningapp.core.designsystem.AppBottomNav(
        selected = selected,
        onSelect = open
    )
}
