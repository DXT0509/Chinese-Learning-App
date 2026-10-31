# Phase 4.4 — review UX and transition performance

Follow-up: [30 October connection reliability and real-catalog timing](srs-connection-reliability-20261030.md).

Implemented 29 October 2026. No development learner data was used or modified.
No schema, scheduling interval, mastery rule, grading policy or dependency changed.
Existing uncommitted Phase 4.1–4.3 work was preserved.

## Learner experience

The dashboard shows due count, six compact mastery counts, and “Ôn tập ngay”.
Removed the motivational paragraph, raw saved IDs, technical availability details,
large nested cards, repeated instructions, gradient, expiry timestamp and scheduling
explanations. Errors and explicit recovery actions remain visible. Session results
show a brief outcome and mastery change; the summary shows reviewed, pass/fail,
mastery change and any skipped words.

Three rounded selectors stay above the scrolling answer area, including on narrow
screens: “1. Chữ Hán”, “2. Pinyin”, “3. Từ loại”. Selection uses a border and accessible
selected semantics; text/icons distinguish unanswered, saved, correct, incorrect and
not applicable. The answer area scrolls independently and retains keyboard padding.
There are no heavy animations. Drawing remains isolated in the handwriting state
flow; the review flow does not observe every stroke point. A prepared recognizer is
reused across words instead of checking/preparing its model for every new word.

| Before | After |
| --- | --- |
| Viết từ đã học có âm Hán-Việt «mã» (1 chữ Hán). Nghĩa trong danh mục: con ngựa; ngựa. | **con ngựa**, with smaller “Hán-Việt: mã · 1 chữ” |
| Bước 1 · Chữ Hán giản thể | 1. Chữ Hán |
| Đúng ở lần trả lời đầu tiên | ✓ Chính xác! |
| Chưa đúng ở lần đầu hoặc đã dùng trợ giúp | ✕ Chưa đúng, followed by that stage’s answer |
| Hết hạn lượt ôn: … | Removed from ordinary UI; TTL enforcement and recovery remain |
| Repeated handwriting/Pinyin explanations | Short “Trợ giúp” toggle |

Only known generated prompt templates are shortened. Required Hán-Việt, length and
sense-specific Vietnamese context remain as secondary cues because installed policies
explicitly depend on them. Duplicate glosses and the narrow “con ngựa; ngựa” pattern
are collapsed; unrelated senses such as “nước; đất nước” are retained. Unknown manual
editorial prompts remain intact to avoid changing the correct-answer contract.
No example containing the hidden target is added to Hanzi. Pinyin help uses a format
instruction without an example that might coincide with the current answer.

## Navigation and authoritative submission contract

**Navigation is free; server submissions remain canonical: HANZI → PINYIN → POS.**
This release does not enable out-of-order HTTP submissions.

Each stage retains its text/selection draft in identity-scoped SavedStateHandle.
Handwriting keeps its existing separate saved strokes, slots, candidates, confirmed
choices and keyboard draft. Switching stages neither submits nor changes correctness.
“Lưu câu trả lời” on a future stage explicitly queues its draft; “Đã lưu · chờ bước
trước” distinguishes it from a graded answer. Editing an unsent draft unqueues it.
After an earlier stage is accepted, queued answers flush in canonical order. An
unanswered stage stops the flush; no empty answer is invented. All applicable answers
must be sealed before the server permits finalization.

Submitted stages display read-only server feedback. A wrong first answer cannot be
replaced for a new PASS. Each request retains its submission key until its response
is reconciled. An interruption during a multi-stage flush preserves both the pending
key and later drafts. Rejected 422 input unqueues only that answer so it can be edited.
409 reconciles current server state. Finalization and scheduling remain authoritative
and idempotent; cached completed results avoid unnecessary finalization calls on resume.

## Backward-compatible API additions

`StageResponse.draft_questions` maps applicable stages to safe question metadata.
The existing `stage`, `question`, ordered submission validation and endpoints remain.
Before Hanzi submission, Pinyin has only the Vietnamese prompt and POS has its target
Chinese occurrences replaced with □, including repetitions. Neither view includes the
hidden simplified form or accepted Pinyin. Full POS options are choices, not an
accepted-answer set. Once Hanzi is sealed, its Chinese form may be displayed; Pinyin
solutions still appear only in feedback after Pinyin submission. Non-applicable stages
have no draft question. Reviewed grammatical context remains pinned to the attempt.
Legacy Android clients ignore the additive fields. New Android falls back to the
canonical question on an old server; full free draft navigation requires updated API
source. Reload the API before installing the new APK. No migration is needed.

`StageFeedback.tone_mismatches` and `syllable_mismatches` are optional additive,
one-based positions. The server diagnoses only unambiguously segmented numbered
Pinyin with the same syllable count as the sole accepted spelling. It does not guess
for unsegmented tone-mark input, malformed input or different syllable counts. Those
cases still receive the authoritative correct answer. Android translates positions
into “Sai thanh ở âm tiết …” or “Sai âm tiết …”.

## Investigated latency and failure causes

Source inspection found these concrete costs and failure paths:

- `ReviewViewModel.finish` previously awaited dashboard → due → all target-report
  pages after successful finalization, before returning control. `targets_report`
  performs per-word eligibility queries and policy resolution; some generated policy
  versions also prepare catalog-wide collision/coverage evidence per transaction.
  A large saved catalog therefore increased work after every word.
- A failure in any of those unrelated refresh calls was caught as a review load error,
  even though finalization had already succeeded. The result was needlessly disabled.
- `send` previously discarded the submission response and made another GET. A lost
  GET could report a connection failure after a successfully accepted answer.
- Next-word initialization then required POST start + GET question only after the
  learner tapped Continue. There was no prepared next question.
- Lifecycle resume fetched the active question repeatedly, even with healthy local
  state. The existing authentication mutex serializes authorized operations, including
  refresh; extra requests add to that serialized work. Refresh logic is unchanged.
- Each new handwriting word called model preparation again. Recognition already runs
  off the main thread and stroke collection already has bounded saved-state size;
  neither required a new drawing architecture.

Finalization now returns its result without catalog/due refresh. Accepted submission
responses supply the next question directly, retaining replay keys and conflict
reconciliation. Dashboard refresh occurs when the dashboard is entered/refreshed.
Healthy active resume reuses state; errors, pending operations and expiry reconcile.
No artificial delays, optimistic grading or broad authentication changes were added.

These are verified source/reproduction paths, not a claim that every original phone
failure had the same cause. There was no captured device HTTP trace in this session.
Real transport outages, expired attempts and unavailable content still show recovery.

## Prefetch, caching and lifetime

The randomized, unique session queue is selected/shuffled once and saved. Finalization
removes only its current saved ID and starts preparation of exactly the next queued
word while the result is displayed. Start uses a persisted UUID as the attempt primary
key; POST replay returns the same attempt. Prefetch never submits or finalizes answers,
never refreshes/reorders the due queue and never changes scheduling.

Only one safe next-question response and its identifiers are cached. Continue consumes
it without another request. If preparation is still running, Continue awaits that same
job and shows “Đang chuẩn bị…” in the answer area; submission is unavailable until a
valid attempt is installed. Failed preparation preserves its key, and the foreground
path retries with that key. A saved completed result and prepared question restore
through normal saved-state recreation without recounting or reshuffling. Owner change
clears private saved state. ViewModel cancellation propagates.

Prepared attempts have the server’s 30-minute TTL. A long pause may expire one; expired
cache is not treated as fresh. The server rejects it and the existing explicit skip/new
attempt recovery remains available. This is not force-stop/cleared-data persistence,
offline review, or a guarantee against external progress changes by another client.

## Measurements and verification

Measurements are samples, not invented speedup ratios or device benchmarks:

| Scope | Measured duration | Method |
| --- | --- | --- |
| Finalize service | 18.78 ms | perf_counter around real SQLAlchemy/PostgreSQL service call |
| Next attempt creation | 14.24 ms | same isolated synthetic two-word fixture |
| Next question retrieval | 5.59 ms | real PostgreSQL, safe draft views included |
| Total next preparation | 19.83 ms | sum of creation + question above |
| Ready-prefetch Continue to ViewModel state | 2.35 ms | JVM wall clock around next() + coroutine scheduler drain; zero API calls |

The database sample is from `test_review_transition_latency.py`, local PostgreSQL 18.3
on loopback, a reviewed synthetic policy and fixture transaction/savepoints. It excludes
Retrofit, TLS, Android rendering and large production-policy catalog preparation. The
JVM sample includes coroutine/test overhead and does not measure a frame or touch.
There is no measured physical-device before/after baseline.

Debug-only `ReviewTiming` emits durations and fixed event names, never tokens,
identities, prompts or answers: `create_request`, `question_request`, `submit_request`,
`finalize`, `next_preparation`, `tap_to_state`, `state_to_frame`, `tap_to_interactive`.
Request times include any authorization mutex wait/refresh. The last two are Compose
next-frame scheduling proxies, not GPU render-completion measurements. Collect them
with `adb logcat -s ReviewTiming` during the isolated device retest. Release does not
log these events. Finalization happens on the result action before the next-word tap;
its timing must be reported separately from the prefetched tap path.

Executed checks:

- Android `testDebugUnitTest assembleDebug lintDebug compileDebugAndroidTestKotlin`:
  **119 unit tests passed**, zero failures/errors/skips; build and instrumentation
  compilation passed. Lint: **0 errors, 74 warnings**, including unused resources
  retained for compatibility with earlier review copy. No lint baseline or suppression
  was added to bypass errors. API 24 expiry parsing uses SimpleDateFormat.
- Backend full suite: **376 passed, 10 skipped**, one existing Starlette/httpx
  deprecation warning, **75.82 seconds**. Fresh concurrency databases covered creation,
  submission/finalization and scheduling races. Skipped tests require additional
  dedicated opt-in migration/maintenance configuration.
- Focused privacy/context/timing suite: **20 passed**. Updated the previous contextual
  test to permit a full list of draft options while explicitly asserting that accepted
  sets, source review evidence, Chinese target and Pinyin key remain hidden.
- Ruff check and format check: all six changed Python files passed.
- `alembic check` on the isolated regular database: **No new upgrade operations**;
  an existing SQLAlchemy dialect-options warning was emitted. No new migration.
- The fake Compose tests for fixed selectors, small-width drafts and handwriting were
  compiled. **No instrumentation, emulator or physical-device execution was performed.**

Temporary-directory permissions initially blocked many Python fixtures; the final run
used a new workspace-local `--basetemp` and cache. A preliminary lint compiler crash
cleared on a stable-source rerun; the subsequent real API-26 lint error was fixed using
API-24-compatible parsing. These failures were resolved, not suppressed.

All database runs used a new loopback-only PostgreSQL cluster on port **55444**,
`backend/.test-postgres-slice2-phase44`, with these retained synthetic databases:
`chinese_phase44_regular`, `chinese_phase44_review_race_final`,
`chinese_phase44_schedule_race_final`, `chinese_phase44_creation_race_final`.
Earlier retained race rehearsal databases have the same prefixes without `_final`
and with `_v2`. Only these new test databases received schema upgrades. No development
migration, reset, downgrade, real learner grading or Docker volume action occurred.
The test cluster was stopped after verification; its fixtures remain on disk.

Local ignored logs: `phase44-android-checks.log`, `phase44-backend-isolated.log`,
`phase44-backend-timing.log`, `phase44-alembic-check.log`. Android XML reports and
lint HTML are under the ignored `android/app/build/` directory.

## Modified files

Android production (`android/app/src/main/`):

- `java/com/example/chineselearningapp/feature/review/ReviewScreen.kt`
- `java/com/example/chineselearningapp/feature/review/ReviewViewModel.kt`
- `java/com/example/chineselearningapp/feature/review/RemoteReviewRepository.kt`
- `java/com/example/chineselearningapp/feature/review/ReviewHandwritingInput.kt`
- `java/com/example/chineselearningapp/feature/review/ReviewHandwritingViewModel.kt`
- `java/com/example/chineselearningapp/feature/review/ReviewPrompt.kt`
- `java/com/example/chineselearningapp/feature/review/ReviewTiming.kt`
- `java/com/example/chineselearningapp/core/network/ReviewApi.kt`
- `java/com/example/chineselearningapp/domain/repository/ReviewRepository.kt`
- `res/values/review_strings.xml`

Android verification (`android/app/src/`):

- `test/java/com/example/chineselearningapp/ReviewFlowOptimizationTest.kt`
- `test/java/com/example/chineselearningapp/ReviewPromptTest.kt`
- `test/java/com/example/chineselearningapp/ReviewViewModelTest.kt`
- `test/java/com/example/chineselearningapp/ReviewRepositoryTest.kt`
- `test/java/com/example/chineselearningapp/ReviewHandwritingTest.kt`
- `androidTest/java/com/example/chineselearningapp/ReviewStageDraftUiTest.kt`
- `androidTest/java/com/example/chineselearningapp/ReviewNavigationTest.kt`
- `androidTest/java/com/example/chineselearningapp/ReviewHandwritingUiTest.kt`

Backend:

- `app/services/review_engine.py`, `app/services/review_grading.py`
- `app/schemas/review_engine.py`
- `tests/test_review_draft_views.py`, `tests/test_review_transition_latency.py`
- `tests/test_contextual_grammar.py` (allows full draft choices, asserts hidden accepted keys)

Documentation: this report, `architecture.md`, `development-guide.md`.

## Physical-device retest checklist — pending

Use a separate synthetic API/account on port 8001, following
[the existing isolated-device setup](android-srs-review.md#physical-device-checklist-pending).
Do not grade real development vocabulary as a test.

1. Reload the isolated API and verify `draft_questions` in OpenAPI; build/install
   with `-PDEV_API_BASE_URL=http://127.0.0.1:8001/` and USB reverse 8001.
2. At 320dp width, larger font scale, landscape and keyboard open, check all three
   fixed selectors, readable prompts, accessible selected/status semantics and scroll.
3. Write/select candidates, switch to Pinyin, type, select POS, return to each stage.
   Include mid-stroke switching/rotation/backgrounding. Verify every draft survives.
4. Save POS/Pinyin first, submit wrong Hanzi, and verify canonical flush and immutable
   first failure. Try each single/multiple/contextual/not-applicable POS fixture.
   Inspect that target Chinese/Pinyin never appears before its permitted boundary.
5. Test wrong Hanzi, numbered tones/syllables and POS; verify compact stage-specific
   feedback. Marked/malformed Pinyin must not get a guessed mismatch diagnosis.
6. Drop responses before/after each stage submission, finalization, prefetch creation
   and between words. Retry, rotate and resume. Verify stable keys, queue and counts,
   one created attempt per queued word and one scheduling effect per completed attempt.
7. Tap Continue both before and after preparation finishes. Capture ReviewTiming,
   report warm/cold/model-download states, device/API/network/catalog size and samples.
   Compare frame proxy with visual readiness; profile frame time during long strokes.
8. Pause longer than TTL, verify explicit expiry recovery, complete the session, return
   to updated dashboard, and log out/change identity. Confirm no private draft persists
   into another account. Force-stop and cleared-data recovery remain unclaimed.
