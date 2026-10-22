package com.example.chineselearningapp.core.designsystem

import androidx.annotation.DrawableRes
import androidx.annotation.StringRes
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.example.chineselearningapp.R

@Composable
fun FeatureEmptyState(@StringRes title: Int, @StringRes description: Int, @DrawableRes icon: Int) {
    Text(stringResource(title), style = MaterialTheme.typography.headlineMedium)
    OutlinedCard(colors = CardDefaults.outlinedCardColors(containerColor = MaterialTheme.colorScheme.surface.copy(alpha = .85f))) {
        Column(Modifier.fillMaxWidth().padding(28.dp), horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(20.dp)) {
            Surface(shape = CircleShape, color = MaterialTheme.colorScheme.primaryContainer) {
                Box(Modifier.size(112.dp), contentAlignment = Alignment.Center) {
                    Icon(painterResource(icon), null, Modifier.size(52.dp), tint = MaterialTheme.colorScheme.primary)
                }
            }
            Text(stringResource(R.string.coming_soon), style = MaterialTheme.typography.titleLarge,
                color = MaterialTheme.colorScheme.primary)
            Text(stringResource(description), color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
}
