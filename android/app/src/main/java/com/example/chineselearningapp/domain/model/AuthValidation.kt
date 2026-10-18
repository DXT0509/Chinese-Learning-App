package com.example.chineselearningapp.domain.model

/** Matches the API's character count, including supplementary Unicode characters. */
object AuthValidation {
    const val MinPasswordLength = 6
    const val MaxPasswordLength = 128
    private val emailPattern = Regex("[^\\s@]+@[^\\s@]+\\.[^\\s@]+")

    fun validEmail(email: String): Boolean =
        email.trim().length <= 320 && email.trim().matches(emailPattern)

    fun validPassword(password: String): Boolean =
        password.codePointCount(0, password.length) in MinPasswordLength..MaxPasswordLength
}
