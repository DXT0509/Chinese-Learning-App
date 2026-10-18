package com.example.chineselearningapp

import androidx.test.platform.app.InstrumentationRegistry
import com.example.chineselearningapp.core.network.SessionVault
import com.example.chineselearningapp.core.network.TokensDto
import java.io.File
import org.junit.Assert.*
import org.junit.Test

class SessionVaultTest {
    @Test fun encryptedPairSurvivesRecreationAndCanBeCleared() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val vault = SessionVault(context)
        vault.clear()
        try {
            vault.write(TokensDto("test-access-unique", "test-refresh-unique"))
            val bytes = File(context.noBackupFilesDir, "session.enc").readBytes()
            assertFalse(String(bytes, Charsets.ISO_8859_1).contains("test-refresh-unique"))
            assertEquals("test-refresh-unique", SessionVault(context).read()?.refresh)
            vault.clear()
            assertNull(SessionVault(context).read())
        } finally { vault.clear() }
    }
}
