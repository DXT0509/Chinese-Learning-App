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
    NavigationBar(
        modifier = Modifier.testTag("main_navigation").clip(RoundedCornerShape(topStart = 28.dp, topEnd = 28.dp)),
        containerColor = MaterialTheme.colorScheme.surface,
        tonalElevation = 2.dp
    ) {
        mainDestinations.forEach { destination ->
            val icon = when (destination) {
                Destination.Home -> R.drawable.ic_home
                Destination.Learning -> R.drawable.ic_book
                Destination.Review -> R.drawable.ic_review
                else -> R.drawable.ic_person
            }
            NavigationBarItem(
                selected = selected == destination,
                onClick = { open(destination) },
                modifier = Modifier.testTag("tab_${destination.name}"),
                icon = { Icon(painterResource(icon), contentDescription = null) },
                label = { Text(stringResource(if (destination == Destination.Home) R.string.nav_home else destination.title)) },
                colors = NavigationBarItemDefaults.colors(
                    selectedIconColor = MaterialTheme.colorScheme.primary,
                    selectedTextColor = MaterialTheme.colorScheme.primary,
                    indicatorColor = MaterialTheme.colorScheme.primaryContainer
                )
            )
        }
    }
}
