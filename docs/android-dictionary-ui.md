# Phase 3.2: Android dictionary search and detail

The Learning tab now opens **Tra từ điển**, then a detail route for a selected dictionary
UUID. This client uses the existing authenticated dictionary API. Backend files, schemas,
imports, database contents and dependency versions were not changed by this phase.

## Files

Created under `android/app/src/main/`:

- `java/com/example/chineselearningapp/domain/model/Dictionary.kt`: framework-free suggestions,
  pages, senses, sources, entries and character annotations.
- `java/com/example/chineselearningapp/domain/repository/DictionaryRepository.kt`: search/detail contract.
- `java/com/example/chineselearningapp/core/network/DictionaryApi.kt`: Retrofit endpoints and wire DTOs.
- `java/com/example/chineselearningapp/feature/dictionary/data/RemoteDictionaryRepository.kt`: authenticated calls and mapping.
- `java/com/example/chineselearningapp/feature/dictionary/DictionaryViewModels.kt`: saved query, request cancellation,
  debounce, paging, detail loading, error states and UUID routes.
- `java/com/example/chineselearningapp/feature/dictionary/DictionaryScreens.kt`: Compose search,
  suggestions, detail, character cards and expandable attribution.
- `res/values/dictionary_strings.xml`: Vietnamese UI resources.

Modified existing Android files:

- `MainActivity.kt`: inject and pass the dictionary repository.
- `core/di/AppModule.kt`: register the API and repository with the existing client configuration.
- `core/navigation/SessionNavigation.kt`: pass the repository into the identity-scoped protected graph.
- `core/navigation/MainNavigation.kt`: own dictionary destinations and back-stack-scoped ViewModels.
- `feature/learning/LearningScreen.kt`: prominent dictionary entry card.
- `feature/auth/data/RemoteSessionRepository.kt`: expose its existing authorized-request helper
  internally so dictionary calls share token storage, serialized refresh and retry behavior.

Added tests:

- `android/app/src/test/java/com/example/chineselearningapp/DictionaryViewModelTest.kt`
- `android/app/src/test/java/com/example/chineselearningapp/DictionaryRepositoryTest.kt`
- `android/app/src/androidTest/java/com/example/chineselearningapp/DictionaryUiTest.kt`

This document is the implementation and verification report. Pre-existing working-tree edits
remain in place, including the main navigation and backend dictionary work.

## Navigation and UI

The existing four bottom tabs remain. Logout remains in Profile. Dictionary search and detail
hide the bottom bar and provide toolbar Back. Search navigates to `dictionary/{entryId}` using
the selected UUID, with single-top navigation. Popping detail preserves the search ViewModel,
query, results, text selection and lazy-list position. Popping search returns to Learning.
Protected state belongs to the existing identity-scoped graph and is removed on sign-out.

The UI uses the existing aurora background, Material theme, mint accents, rounded bordered
surfaces and lightweight navigation transitions. Results use a LazyColumn keyed by entry UUID.
Identical Hanzi with different identities remain separate and retain backend ordering.
Traditional text appears when different, alongside tone-marked Pinyin.

The editable TextFieldValue preserves cursor editing, selection, paste, deletion and IME
composition. Searching waits for composition to finish, then debounces for 300 ms. A changed
query cancels both delayed and in-flight requests immediately; cancellation checks and a
generation guard prevent late responses from replacing the current results. Cursor-only edits
and equivalent surrounding whitespace do not repeat requests. Manual retry bypasses debounce.

Empty/whitespace input makes no request. Raw queries longer than 64 Unicode code points, or
containing Unicode control/format/surrogate/private/unassigned characters, show validation.
The field retains the entered text, including on failure. Search pages request 20 entries;
an explicit load-more action follows the server offset through its maximum of 1000. Page
failures retain already loaded results and retry the same offset. Overlapping page UUIDs are
filtered without merging entries that merely share Hanzi.

States include empty, typing/composing, loading, results, no results, invalid input, request
failure, expired authentication and missing detail. IOException/timeouts/server errors use
a generic retry state; 422 shows invalid input; detail 404 shows unavailable. Authentication
uses the existing refresh-once/retry-once path. Rejected refresh clears the existing session;
the route calls the existing session reload action to restore the login flow. Transient
refresh failures preserve credentials and allow retry.

## API and content mapping

`GET /api/v1/dictionary/search?q=…&limit=20&offset=…` maps `items` and `next_offset`.
Suggestions map `entry_id`, `simplified`, `traditional`, `primary_pinyin`,
`short_vi_meaning`, `available_languages` and `source`. The current response has no English
definition snippets, so no snippets or English definition labels are manufactured. A future
nonblank `short_vi_meaning` will render as supplied. No per-result detail requests occur.

`GET /api/v1/dictionary/entries/{entry_id}` runs only when opening detail. It maps citation
Pinyin, language-grouped numbered meanings, optional lexical Sino-Vietnamese data, character
annotations and source attribution. Available Vietnamese meanings sort before English.
English meanings are labeled **Nghĩa tiếng Anh**. Cross-references remain literal selectable
text, with no inferred examples, links or extra senses.

Character annotations have their own **Khám phá từng chữ Hán** section and explanation that
they are not verified word translations/readings. Cards show form, Pinyin, supplied
Sino-Vietnamese reading and Vietnamese gloss. A false pronunciation match displays a warning;
an unknown match is explicitly unverified. Positions and traditional positions remain mapped
in the domain model. Missing annotations omit the section. Individual character glosses are
never combined into a compound-word translation.

The expandable source section includes word and character sources, attribution, changes,
source links and license links. Checksums and revisions stay out of the learning UI.
Only HTTP(S) source links are opened; malformed/unavailable links fail gracefully.
Absent audio, examples or parts of speech produce no empty cards or inert controls.
No audio playback, TTS, saving, SRS or handwriting recognition was added.

## Verification

Executed from `android/`, using Android Studio's JBR:

```powershell
$env:JAVA_HOME = 'C:\Program Files\Android\Android Studio\jbr'
.\gradlew.bat testDebugUnitTest assembleDebug lintDebug assembleDebugAndroidTest
```

Final result: **BUILD SUCCESSFUL**. All **47 unit tests passed** (13 dictionary tests), with
zero failures, errors or skips. `assembleDebug`, `lintDebug` and `assembleDebugAndroidTest`
passed. Lint reported **0 errors and 40 warnings**, all located in existing dependency
catalog entries and other resource files; none are in the dictionary implementation.
`git diff --check` passed. The initial sandboxed attempt could not download Gradle;
the checks above completed with the permitted cache/network access and Android Studio JBR.
Unit coverage includes
debounce, composition, cancellation of non-cooperative stale requests, blank/oversized/control
input, supplementary Hanzi, manual retry, empty results, saved query, pagination retry,
duplicate Hanzi identities, stable UUID routes, wire mapping, literal glosses, character/word
separation, token refresh/rejection, HTTP validation/not-found/server errors and detail retry.

The two Compose instrumentation tests cover actual graph selection of the second duplicate
Hanzi entry, Back to preserved search and Learning, English labels, character notes,
pronunciation mismatch warnings and attribution expansion. They were compiled into the test
APK, not executed. No emulator or physical-device validation was performed for this phase.
The repository tests use MockWebServer; they do not prove connectivity to a live imported DB.

## Physical Android verification steps (not performed)

1. Follow `android-usb-development.md` to run the existing backend and configure USB/ADB reverse.
   Use a database with the existing dictionary migrations and reviewed imports already applied.
2. From `android/`, run `gradlew.bat installDebug`, open the app and log in with a real account.
3. Open Learning → Tra từ điển. Type/paste 学生; test Chinese keyboard composition, cursor
   selection/replacement, deletion and clear. Confirm no requests for blank input.
4. Search 家 and inspect entries with different traditional forms/readings. Open a chosen
   entry and confirm its UUID in the API response matches that selection. Check English labels,
   separate Vietnamese character notes, mismatch/unknown-reading notices and license links.
5. Back to search: verify query, results and scroll position. Back again: verify Learning.
   Rotate on search/detail; background/recreate the process and verify query restoration.
6. Disconnect the API, search and retry after reconnecting; retain the query. Test expired
   access with successful refresh and rejected refresh returning to login. Test an unavailable
   UUID, no-result input, a 65-character paste and load-more/retry behavior.
7. Run `gradlew.bat connectedDebugAndroidTest -Pandroid.testInstrumentationRunnerArguments.class=com.example.chineselearningapp.DictionaryUiTest`
   on a connected device/emulator to execute the two UI tests.

## Limitations and Phase 3.3 preparation

Search is the backend's Hanzi exact/prefix search; Pinyin search is not advertised. Results and
details require connectivity and are not cached in Room. Query restoration after process death
refetches results; results are retained in memory on ordinary Back/configuration changes.
Chinese glyph appearance and real IME behavior still require device verification.

The field already supports cursor/selection operations through TextFieldValue. Phase 3.3 can
insert recognized text at that selection and feed the resulting text through the same
`edit(text, isComposing)` pipeline. Recognition is not implemented. Detail header, definitions,
character cards and attribution are separate renderers to accommodate a future real Save action.
