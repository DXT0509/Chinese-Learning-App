package com.example.chineselearningapp

import com.example.chineselearningapp.domain.model.AuthValidation
import org.junit.Assert.*
import org.junit.Test

class AuthValidationTest {
    @Test fun passwordBoundaries() {
        assertFalse(AuthValidation.validPassword("a".repeat(5)))
        assertTrue(AuthValidation.validPassword("a".repeat(6)))
        assertTrue(AuthValidation.validPassword("a".repeat(128)))
        assertFalse(AuthValidation.validPassword("a".repeat(129)))
    }
    @Test fun unicodeCharactersCountLikePydanticRatherThanUtf16Units() {
        assertFalse(AuthValidation.validPassword("😀".repeat(5)))
        assertTrue(AuthValidation.validPassword("😀".repeat(6)))
        assertTrue(AuthValidation.validPassword("😀".repeat(128)))
        assertFalse(AuthValidation.validPassword("😀".repeat(129)))
    }
    @Test fun emailValidationTrimsAndRejectsWhitespace() {
        assertTrue(AuthValidation.validEmail(" user@example.com "))
        assertFalse(AuthValidation.validEmail("user example.com"))
        assertFalse(AuthValidation.validEmail("user@example .com"))
    }
}
