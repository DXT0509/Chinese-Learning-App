package com.example.chineselearningapp.core.di

import android.content.Context
import androidx.room.Room
import com.example.chineselearningapp.BuildConfig
import com.example.chineselearningapp.core.database.LearningDatabase
import com.example.chineselearningapp.core.database.VocabularyDao
import com.example.chineselearningapp.core.network.HealthApi
import com.example.chineselearningapp.core.network.RemoteHealthRepository
import com.example.chineselearningapp.domain.repository.HealthRepository
import com.example.chineselearningapp.domain.repository.VocabularyRepository
import com.example.chineselearningapp.feature.vocabulary.data.LocalVocabularyRepository
import dagger.Binds
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import java.util.concurrent.TimeUnit
import javax.inject.Singleton
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    @Provides @Singleton
    fun retrofit(client: OkHttpClient): Retrofit = Retrofit.Builder()
        .baseUrl(BuildConfig.API_BASE_URL).client(client)
        .addConverterFactory(GsonConverterFactory.create()).build()
    @Provides @Singleton
    fun sessionApi(retrofit: Retrofit): com.example.chineselearningapp.core.network.SessionApi =
        retrofit.create(com.example.chineselearningapp.core.network.SessionApi::class.java)
    @Provides @Singleton
    fun dictionaryApi(retrofit: Retrofit): com.example.chineselearningapp.core.network.DictionaryApi =
        retrofit.create(com.example.chineselearningapp.core.network.DictionaryApi::class.java)
    @Provides @Singleton
    fun personalVocabularyApi(retrofit: Retrofit): com.example.chineselearningapp.core.network.PersonalVocabularyApi =
        retrofit.create(com.example.chineselearningapp.core.network.PersonalVocabularyApi::class.java)

    @Provides @Singleton
    fun client(): OkHttpClient = OkHttpClient.Builder()
        .connectTimeout(10, TimeUnit.SECONDS).readTimeout(10, TimeUnit.SECONDS)
        .callTimeout(15, TimeUnit.SECONDS).build()

    @Provides @Singleton
    fun healthApi(retrofit: Retrofit): HealthApi = retrofit.create(HealthApi::class.java)

    @Provides @Singleton
    fun database(@ApplicationContext context: Context): LearningDatabase = Room.databaseBuilder(
        context, LearningDatabase::class.java, "chinese_learning.db"
    ).build()

    @Provides
    fun vocabularyDao(database: LearningDatabase): VocabularyDao = database.vocabularyDao()
}

@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {
    @Binds @Singleton
    abstract fun personalVocabulary(implementation: com.example.chineselearningapp.feature.vocabulary.data.RemotePersonalVocabularyRepository): com.example.chineselearningapp.domain.repository.PersonalVocabularyRepository

    @Binds @Singleton
    abstract fun dictionary(implementation: com.example.chineselearningapp.feature.dictionary.data.RemoteDictionaryRepository): com.example.chineselearningapp.domain.repository.DictionaryRepository

    @Binds @Singleton
    abstract fun tokenStore(implementation: com.example.chineselearningapp.core.network.SessionVault): com.example.chineselearningapp.core.network.SessionTokenStore
    @Binds @Singleton
    abstract fun session(implementation: com.example.chineselearningapp.feature.auth.data.RemoteSessionRepository): com.example.chineselearningapp.domain.repository.SessionRepository
    @Binds @Singleton
    abstract fun health(implementation: RemoteHealthRepository): HealthRepository

    @Binds @Singleton
    abstract fun vocabulary(implementation: LocalVocabularyRepository): VocabularyRepository
}
