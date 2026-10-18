package com.example.chineselearningapp

import androidx.room.Room
import androidx.test.platform.app.InstrumentationRegistry
import com.example.chineselearningapp.core.database.CachedVocabulary
import com.example.chineselearningapp.core.database.LearningDatabase
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Test

class RoomCacheTest {
    @Test
    fun upsertPreservesUnicodeAndReplacesExistingEntry() = runBlocking {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val database = Room.inMemoryDatabaseBuilder(context, LearningDatabase::class.java).build()
        try {
            val dao = database.vocabularyDao()
            dao.upsertAll(listOf(CachedVocabulary("word-1", "你好", "nǐ hǎo", "xin chào")))
            dao.upsertAll(listOf(CachedVocabulary("word-1", "你好", "nǐ hǎo", "chào bạn")))
            val entries = dao.observeAll().first()
            assertEquals(1, entries.size)
            assertEquals("你好", entries.single().simplified)
            assertEquals("chào bạn", entries.single().vietnameseMeaning)
        } finally {
            database.close()
        }
    }
}
