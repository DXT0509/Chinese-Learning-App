package com.example.chineselearningapp.feature.roadmap

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.example.chineselearningapp.R

@Composable
fun RoadmapScreen(state: ConnectivityState, retry: () -> Unit) {
    Column(Modifier.padding(24.dp), verticalArrangement = Arrangement.spacedBy(20.dp)) {
        Text(stringResource(R.string.welcome), style = MaterialTheme.typography.headlineMedium)
        Text(stringResource(R.string.roadmap_placeholder))
        Card(Modifier.fillMaxWidth()) {
            Column(Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Text(stringResource(R.string.connection_title), style = MaterialTheme.typography.titleMedium)
                when (state) {
                    ConnectivityState.Loading -> {
                        CircularProgressIndicator()
                        Text(stringResource(R.string.connecting))
                    }
                    is ConnectivityState.Reachable -> {
                        Text(stringResource(R.string.backend_reachable))
                        Text("${state.health.service} · ${state.health.version}")
                    }
                    ConnectivityState.Unavailable -> Text(stringResource(R.string.backend_unavailable))
                }
                Button(onClick = retry, enabled = state != ConnectivityState.Loading) {
                    Text(stringResource(R.string.retry))
                }
            }
        }
    }
}
