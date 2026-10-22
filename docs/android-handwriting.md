# Phase 3.3: dictionary handwriting

Learning → Tra từ điển now offers a pencil action beside the existing editable query.
The inline panel keeps that field visible, hides the keyboard on opening, and stays open
after a candidate is selected. Closing the panel preserves the query; the field can still
receive normal keyboard input. Back closes an open panel before leaving search.

## SDK and resources

The version catalog declares `com.google.mlkit:digital-ink-recognition:19.0.0`, as listed in
[Google's Android guide](https://developers.google.com/ml-kit/vision/digital-ink-recognition/android).
The model is `zh-Hani-CN`, confirmed in the official
[supported model list](https://developers.google.com/ml-kit/vision/digital-ink-recognition/base-models).
SDK 19 uses the
[`com.google.mlkit.vision.digitalink.recognition` package](https://developers.google.com/android/reference/com/google/mlkit/vision/digitalink/recognition/package-summary).

`MlKitHandwritingRecognizer` checks installed model availability before downloading,
reports a first-use download state, and reuses both an ongoing download Task and its loaded
client. Download failures remain retryable. Model preparation and inference use asynchronous
Tasks; Ink conversion runs on Dispatchers.Default. The Hilt-provided factory creates one
adapter for the dictionary back-stack ViewModel. The adapter closes when that ViewModel is
cleared, waiting for outstanding native inference to actually complete before closing its
client. Cancelling a coroutine stops waiting for a Task; ML Kit's underlying work may finish
later. No strokes or images are sent to the application backend.

## Canvas and state

The Compose Canvas collects finger/stylus down, historical/move samples and up events,
preserving point timestamps, stroke boundaries and input order. Coordinates use a fixed
1000 × 1000 writing space, scaled to the current canvas bounds. Ink is drawn continuously
with round line caps and joins; stationary taps render a dot. Crosshair guidelines do not
constrain or correct strokes. The active gesture stays local to the Canvas, avoiding
screen-wide state updates on every point. Completed strokes are immutable snapshots.
Touch cancellation, pointer disposal and lifecycle stop discard the unfinished gesture.

Undo removes the last completed stroke; Clear removes all completed strokes and candidates.
Recognition requires a completed valid stroke and is disabled during drawing or inference.
The state machine distinguishes closed, preparing, downloading, ready, recognizing,
candidates, empty results, model error and inference error. Cancellation plus generation
checks suppress late results after a new stroke, Undo, Clear, dismissal or supersession.
Recoverable failures show Vietnamese resource messages and Retry, without exception details.

The panel and completed strokes survive ordinary configuration changes through the
back-stack ViewModel; an interrupted active stroke is discarded. Backgrounding cancels an
active touch gesture while completed strokes and recognition state stay in memory. Leaving
search closes the panel and invalidates inference. Model files remain available for offline
recognition after the first successful download.

## Candidates and search

Ranked actual ML Kit strings are filtered to nonempty Han text, deduplicated in original
order and limited to ten. Supplementary Han code points are supported. Multi-character Han
candidates remain intact and are explicitly explained in the panel. No confidence
percentages or automatic selection are shown.

Selecting a candidate inserts its complete text at the saved caret or replaces the current
selection. Boundaries inside a surrogate pair are expanded safely; a split caret advances
past the whole code point. The caret moves after the inserted text and any IME composition
is committed. Only that deliberate selection calls the existing `edit(text, false)` query
callback. The existing 300 ms debounce, query validation, authenticated dictionary calls,
pagination and UUID detail navigation remain the only search implementation.

## Files changed for this phase

Created:

- `android/app/src/main/java/com/example/chineselearningapp/feature/dictionary/handwriting/Handwriting.kt`
- `android/app/src/main/java/com/example/chineselearningapp/feature/dictionary/handwriting/MlKitHandwritingRecognizer.kt`
- `android/app/src/main/java/com/example/chineselearningapp/feature/dictionary/handwriting/HandwritingViewModel.kt`
- `android/app/src/main/java/com/example/chineselearningapp/feature/dictionary/handwriting/HandwritingText.kt`
- `android/app/src/main/java/com/example/chineselearningapp/feature/dictionary/handwriting/HandwritingPanel.kt`
- `android/app/src/main/res/drawable/ic_handwriting.xml`
- `android/app/src/main/res/values/handwriting_strings.xml`
- `android/app/src/test/java/com/example/chineselearningapp/HandwritingTest.kt`
- `android/app/src/androidTest/java/com/example/chineselearningapp/HandwritingUiTest.kt`
- `docs/android-handwriting.md`

Modified:

- `android/gradle/libs.versions.toml`, `android/app/build.gradle.kts`: SDK dependency.
- `android/app/src/main/java/com/example/chineselearningapp/MainActivity.kt`: Hilt adapter provider.
- `android/app/src/main/java/com/example/chineselearningapp/core/navigation/SessionNavigation.kt`:
  pass the factory into the authenticated graph.
- `android/app/src/main/java/com/example/chineselearningapp/core/navigation/MainNavigation.kt`:
  back-stack handwriting ViewModel ownership.
- `android/app/src/main/java/com/example/chineselearningapp/feature/dictionary/DictionaryScreens.kt`:
  entry action, inline panel, focus behavior and selection-aware query insertion.
- `docs/architecture.md`, `docs/development-guide.md`: link this slice.

Existing unrelated working-tree edits were preserved. No backend, database, saved vocabulary,
SRS, EXP, lesson completion or new navigation destination changes belong to this phase.

## Validation

Executed from `android/` using Android Studio JBR:

```powershell
$env:JAVA_HOME = 'C:\Program Files\Android\Android Studio\jbr'
.\gradlew.bat testDebugUnitTest assembleDebug lintDebug assembleDebugAndroidTest
```

Result: **BUILD SUCCESSFUL**. All **58 unit tests passed**, including **11 new handwriting
tests**, with zero failures, errors or skips. Debug app assembly, lint and instrumentation
APK assembly passed. Lint reported **0 errors and 40 warnings** in existing dependency
catalog entries/resources. The build also reported existing deprecated ResponseBody test
usage and unstripped native libraries, including ML Kit's `libdigitalink.so`, packaged as
provided. `git diff --check` passed (Git printed line-ending normalization notices).

The initial sandboxed attempt could not download Gradle because network access was blocked;
the successful build used permitted network/cache access. An initial compilation error from
the SDK's renamed package was corrected to the current official SDK 19 API.

Unit tests cover actual collection/order/timestamps, interrupted/invalid strokes, Undo,
Clear, empty recognition prevention, download/retry states, model reuse, ranked candidates,
selection, surrogate-safe caret/selection replacement, composition commit, the existing
keyboard/debounce pipeline, inference errors, empty results, repeated taps, stale results
after all canvas invalidations and supersession, and ViewModel resource cleanup. The
existing dictionary tests continue to cover detail routes and search behavior.

Four new instrumentation tests cover actual canvas gestures, touch cancellation, candidate
selection and keyboard input, handwriting through the protected navigation graph into
dictionary search/detail and Back, and official model identifier/client initialization.
They were **compiled, not executed**. No device, emulator, live model download or physical
recognition validation is claimed.

## Physical-device checklist (not performed)

1. Start the existing backend with an imported dictionary and follow `android-usb-development.md`.
2. Install debug, sign in, open Learning → Tra từ điển.
3. Tap the pencil. Confirm the first-use download state with a working network.
4. Draw 你 naturally with a finger or stylus.
5. Tap Nhận diện and inspect the actual candidates.
6. Deliberately select 你; confirm query becomes 你 and the canvas clears.
7. Draw 好 and tap Nhận diện.
8. Select 好.
9. Confirm the editable query is 你好.
10. Confirm real dictionary suggestions arrive from the existing API.
11. Open a chosen word detail and verify the expected entry.
12. Back to search; confirm the query and results remain.
13. Open the panel, draw several strokes, test Undo and Clear, including during inference.
14. Close the panel; use the keyboard, composition, paste, cursor insertion and selection replacement.
15. Disconnect networking after the model download; verify recognition can reuse the model.
    Dictionary suggestions still require the existing backend connection.
16. Test offline first-use failure and Retry after reconnecting; inference with no matches;
    repeated taps; dismissal while preparing/recognizing; smaller phones and large text.
17. Rotate with completed strokes and during a stroke/inference; background/foreground the app;
    verify incomplete gestures are discarded and completed strokes remain usable.

Compile instrumentation coverage with `assembleDebugAndroidTest`. To run the new tests on
a connected device/emulator, use:

```powershell
.\gradlew.bat connectedDebugAndroidTest '-Pandroid.testInstrumentationRunnerArguments.class=com.example.chineselearningapp.HandwritingUiTest,com.example.chineselearningapp.DictionaryUiTest'
```

## Limitations

No device or emulator recognition validation has been performed. Recognition quality,
real Chinese glyph rendering, stylus latency, IME/focus interactions, rotation, downloads
and offline reuse still require the checklist above. The deterministic tests use fake
adapters; production candidates come exclusively from ML Kit. Instrumentation initialization
coverage creates the official client but does not download a model or assert recognition
accuracy. A killed process restores the existing saved query/field selection, but discards
the temporary panel, strokes and candidates. Non-Han recognition strings are excluded;
multi-character Han strings are offered intact. Handwriting is input, with no correctness
grading or stroke-order assessment.
