package com.example.chineselearningapp.core.datastore

import android.content.Context
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.floatPreferencesKey
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject
import javax.inject.Singleton
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

val Context.appPreferences by preferencesDataStore("app_preferences")

/** Non-sensitive preferences only; this is not session token storage. */
@Singleton
class AppPreferences @Inject constructor(@param:ApplicationContext private val context: Context) {
    private val languageKey = stringPreferencesKey("interface_language")
    val interfaceLanguage = context.appPreferences.data.map { it[languageKey] ?: "vi" }

    suspend fun setInterfaceLanguage(language: String) {
        require(language in setOf("vi", "en"))
        context.appPreferences.edit { it[languageKey] = language }
    }

    private val audioVolumeKey = floatPreferencesKey("audio_volume")
    val audioVolume: Flow<Float> = context.appPreferences.data.map { it[audioVolumeKey] ?: 1.0f }

    suspend fun setAudioVolume(volume: Float) {
        context.appPreferences.edit { it[audioVolumeKey] = volume.coerceIn(0f, 1f) }
    }
}
