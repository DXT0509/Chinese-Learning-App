# Submission recovery and Pinyin input — 30 October 2026

## Installed-version finding

Read-only package inspection on the connected phone showed `lastUpdateTime` of
**29 October 23:24:14**, while the previous connection-fix APK was built **30 October
00:28:11** (Bangkok time). Device logs still came from the earlier application process
and lacked the new failure categories. The earlier Android recovery changes therefore
had not reached the phone. Backend preparation was already fast, consistent with the
user's observation that loading the next word had improved.

The new debug APK was built and three synthetic local UI tests passed on the phone.
However, Gradle's connected-test cleanup unexpectedly uninstalled the target package
at the end. This removed the existing local installation despite the intended
in-place update. Package inspection confirmed it was absent, including from `pm list
packages -u`. The APK was immediately installed again with `adb install -r`; this
returned Success. Package metadata now records both firstInstallTime and lastUpdateTime
as **30 October 01:11:47** (Bangkok). Local sign-in/drafts can be lost; server progress
was not modified. The user was informed in commentary. No real review answer or
server progress write was used to validate the phone.

**Do not run `connectedDebugAndroidTest` on a phone holding user application data
under this setup.** Use an isolated emulator/test device. Ordinary APK updates should
use `adb install -r`, with no uninstall/clear step. Do not assume test-runner cleanup
retains application data.

## Submission recovery

The normal path still uses the submission response directly, without another GET.
The existing OkHttp stale-connection recovery remains enabled.

For an API transport IOException during stage submission:

1. GET the authoritative current attempt state.
2. If that stage already has first-answer feedback, show it, including an incorrect
   verdict. Do not POST the answer again and do not replace first correctness.
3. If the stage remains the current unanswered stage, replay once with the **same
   submission key and exact body**.
4. A second delivery failure or failed reconciliation propagates to the existing
   visible retry state. The ViewModel retains its pending key/body for manual retry
   and normal restoration. No delays or unbounded retry loop were added.

The recovery trigger marks failures specifically from the submission HTTP call.
Credential-vault IO errors and refresh-storage failures do not trigger it: retrying
those could replay a consumed refresh token. Malformed JSON, ordinary HTTP errors and
cancellation also do not trigger automatic submission replay. Cancellation propagates.
A server-completed attempt returned by recovery can proceed to idempotent finalization
instead of getting stuck on Continue. Scheduling/mastery and backend grading are unchanged.

Tests inject disconnects after the server receives a request, check sealed wrong
feedback without another POST, verify the same key/body for an unaccepted answer,
bound repeated failures, and ensure 422/500 and credential persistence failures do not
trigger replay. Existing first-answer, authentication, restoration and prefetch tests
remain in the Android suite.

## Pinyin input design

The Pinyin field uses an ASCII keyboard with autocorrect/capitalization disabled.
A compact accessory row supplies **ü · 1 · 2 · 3 · 4 · 5**. These are generic input
controls, never the target spelling or correct answer.

- Type `n`, tap `ü`, tap `3` to produce `nü3` without a specialized keyboard.
- Ordinary phone keys can enter `nv3` or `nu:3`; the backend already accepts both
  as explicit aliases of `nü3`, as well as tone-marked `nǚ`.
- Visible short help: “Gõ ü bằng v hoặc u:. Dùng số thanh 1–5.”
- Keys insert at the cursor or replace the selected text. A tone key replaces the
  immediately preceding tone number rather than creating invalid `34` suffixes.
- Text and cursor use saveable state; the ViewModel remains the draft owner across
  stage navigation. Controls disable during submission. Done dismisses the keyboard
  rather than grading automatically; the primary action remains explicit.
- `nu3` stays different from `nü3`; plain `u` is never silently changed to `ü`.
  Tone and syllable correctness remain server-authoritative.

Backend tests cover `nǚ`, `nü3`, `nv3`, `NV3`, `nu:3`, wrong tone and plain-u negatives,
plus multi-syllable ü/v/u: forms. No backend production change or migration was needed.

## Verification

- Android: **130 unit tests passed**, zero failures/errors/skips. Debug assembly,
  instrumentation compilation and lint passed. Lint: **0 errors, 74 warnings**.
- Backend targeted grading/privacy tests: **48 passed**. No database was required.
- Physical-device local UI tests: **3 passed, 0 skipped, 0 failed** on Samsung
  SM-A225F, Android 12 / API 31. These verified the umlaut/tone buttons, correcting an
  existing tone number, disabled submission controls and small-width stage draft
  navigation. Tests used a fake repository/local text editor and performed no network
  grading or writes to real learner data. Their uninstall side effect is documented
  above; local application data was not successfully preserved.
- Final installation verified with `pm path` and package update timestamps after the
  explicit successful `adb install -r`. The current APK is installed, not merely built.

Changed Android production files: review `RemoteReviewRepository.kt`, `ReviewViewModel.kt`,
`ReviewScreen.kt`, new `ReviewPinyinInput.kt`, and `res/values/review_strings.xml`.
Tests: `ReviewRepositoryTest.kt`, new `ReviewPinyinInputTest.kt`, new
`ReviewPinyinKeyboardUiTest.kt`, plus backend `tests/test_review_grading.py`.

Evidence: ignored logs `srs-submission-device.log`, `srs-pinyin-submission-android.log`,
`srs-pinyin-grading.log` and `srs-pinyin-device-tests.log`. APK remains at
`android/app/build/outputs/apk/debug/app-debug.apk`.

A real outage can still require manual retry. The historical phone error was not
classified by the old APK, so this report does not claim that every previous failure
was a particular backend or socket error. New failure-category logs remain available
for diagnosing any recurrence on the installed current build. Physical UI success is
not a claim that a real learner session was graded as an end-to-end network test.
