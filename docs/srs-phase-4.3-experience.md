# Phase 4.3 Android SRS experience — 2026-10-28

This phase extends the existing authenticated Review flow. Grading, PASS/FAIL,
mastery, due/practice eligibility and scheduling remain server authoritative.
No database migration, policy installation, development-data write, real learner
attempt or deployment was performed. Existing uncommitted Phase 4.1/4.2 work is retained.

## Handwriting and review UI

Stage 1 defaults to handwriting. `ReviewHandwritingViewModel` uses the existing
`HandwritingRecognizer` interface and production `MlKitHandwritingRecognizer`,
including the [`zh-Hani-CN` Chinese model](https://developers.google.com/ml-kit/vision/digital-ink-recognition/base-models)
and asynchronous native Tasks.
No dependency changes or fabricated recognizer results are introduced. The
[official Android integration](https://developers.google.com/ml-kit/vision/digital-ink-recognition/android)
documents model preparation/download and asynchronous recognition.

Hanzi questions add optional `character_count`, computed from the pinned word on
the server. The count never includes the answer or future Pinyin/POS solutions.
Existing complete Vietnamese prompts retain their meanings, Hán-Việt and reviewed
sense/context cues. Each character has its own strokes, ranked single-Han candidates
and explicit selected result. The learner can switch slots, undo or clear only the
active slot, recognize it again and correct its candidate without erasing other slots.
Recognition never submits, chooses the expected answer, advances the server stage,
or replaces an existing confirmed choice. Editing a slot invalidates that slot's choice.
Recognition grades neither stroke order nor calligraphy; only actual submitted text
is graded by the existing server API.

The shared canvas normalizes coordinates across size changes, consumes finger input,
renders rounded smoothed paths and confines per-move state to canvas drawing. Review
also retains an interrupted gesture as a partial stroke when the gesture is cancelled
by rotation/backgrounding. Completed strokes, candidates, selected characters, slot,
input mode and keyboard draft are saved in identity-scoped SavedStateHandle state.
No network or database access occurs in composables. Model and recognition loading,
empty and error states are visible; model download can be retried. Keyboard fallback
preserves both drafts and can submit even while model download is pending.

Dashboard uses the existing theme with a soft green gradient, rounded summary card,
six server mastery buckets, due/later counts, learning progress and a large primary
action. Session UI shows position, completion progress, stage, full cues and feedback
before the next question. Pinyin supports the existing numbered-tone instructions;
POS options and single/multiple selection come from the question. Result times use
device-local time, with authoritative before/after mastery and scheduling feedback.
The final summary counts PASS, FAIL, reviewed and explicitly skipped words and sums
only applied authoritative mastery changes. Replayed finalization never counts twice.

## Random session selection contract

`GET /api/v1/me/srs/session-targets?limit=20` requires existing Bearer auth and returns
`Cache-Control: no-store`. `limit` accepts 1–50; Android requests 20. Response shape:

```json
{"items":[{"saved_id":"<owned-saved-uuid>","due":true}],"excluded":[]}
```

The query includes **all** owned, active, available due records, ordered by PostgreSQL
`random()`, with no preselection LIMIT/OFFSET. The server streams batches of 100,
checks the existing reviewed-policy resolver and stops after the requested number
of gradeable rows. Filtering a uniformly random permutation gives uniform selection
over the eligible population, including records beyond the first old queue page.
The result is bounded and contains no answers or attempts. PostgreSQL performs the
random sort; its cost scales with the due population. Existing catalog-cued policy
verification retains its existing per-transaction cache and integrity checks.

Pressing “Ôn tập ngay” fetches a fresh sample. Android removes duplicate saved identities
and applies Kotlin's standard random shuffle to the whole selected session. The queue
is saved **before** creating the first keyed attempt and consumed by saved order, not
dashboard ordering or refreshed due timestamps. Recomposition, tab navigation, normal
rotation/process restoration and retries do not reselect or reshuffle it. Unavailable
or expired items can be explicitly skipped, with no fabricated failure or schedule write.
Dashboard target/exclusion display is bounded to 20/100 entries while paging correctly
through excluded pages. Dashboard counts always come from its aggregate endpoint.

Deploy/restart the source backend before this Android update. An old backend lacks
`session-targets`; Android reports the error rather than silently reviewing a biased
first page. A legacy question without `character_count` falls back to Chinese keyboard
instead of guessing a word length from prompt text or hidden answers.

## Recovery and practical limits

Creation UUIDs, attempt IDs and exact pending submission keys/bodies continue to use
the Phase 4.2 recovery mechanism. A lost response retries the same operation; question
reconciliation prevents replay responses from rewinding a stage. The protected graph
owns both ViewModels and discards them on identity changes. Native recognizer resources
are closed when its ViewModel is cleared. Cancellation is propagated, and stale
recognition from a different slot/attempt is ignored. Leaving the result for the
dashboard preserves the current session and offers Resume.

Saved state supports ordinary OS restoration, not cross-device recovery, force-stop,
task removal, app-data clearing or durable offline sessions. Unfinished server attempts
expire without penalty. Each slot uses at most 128 sampled points per completed stroke,
with a 6,000-point total saved-state budget. At capacity, feedback asks the learner to
undo/clear or use the keyboard. Counts above 64 use keyboard fallback. Recognition
quality, native model installation and touch feel require device testing. Initial
model download needs network/storage; grading always needs the backend. There is no
offline grader or recognition-based correctness heuristic.

## Automated verification

From `android/`:

```powershell
.\gradlew.bat testDebugUnitTest assembleDebug lintDebug compileDebugAndroidTestKotlin
```

Fake recognizer tests cover single/multiple slots, candidate selection and correction,
undo/clear, download and inference loading/failure, empty/non-Han results, fallback,
saved-state restoration/identity isolation, stale results and bounded saved ink.
MockWebServer checks actual Hanzi text, auth refresh and keyed retry, character-count
mapping, the new bounded endpoint, and pagination across an entirely excluded page.
Review tests cover server PASS/FAIL and Pinyin/POS progression, duplicate submission,
queue uniqueness/randomness/restoration, summary calculations, dashboard refresh,
explicit skipping and network/expiry/auth recovery. Instrumented UI tests use real
touch gestures with a fake recognizer; navigation tests keep existing auth behavior.
Instrumentation compilation is not execution on an emulator or phone.

Final Android run: **107 unit tests passed**, no failures/errors/skips. Debug assembly,
instrumentation Kotlin compilation and lint passed; lint reports **0 errors, 51 warnings**.

Backend full suite: **324 passed, 10 skipped**, one existing Starlette/httpx warning.
This includes independent-connection creation/submission/finalization races and all
existing scheduler/grading regressions. Additional character-count parameter cases
are verified in the focused rerun (**9 passed**). Optional migration/maintenance rehearsals without
their dedicated URLs were skipped. `alembic check`: **no new upgrade operations**;
an existing SQLAlchemy dialect-options warning was emitted. Changed Python files pass
Ruff format/lint. No new migration needs deployment or a migration rehearsal.

Fresh retained synthetic-only databases:

| Purpose | Database |
| --- | --- |
| Regular suite | `chinese_srs_phase43_regular_c83916dcae` |
| Scheduler race | `chinese_srs_phase43_srs_race_e592c4e5b0` |
| Review race | `chinese_srs_phase43_review_race_6bd8b71d2e` |
| Creation race | `chinese_srs_phase43_creation_race_f6a207587c` |

No reset, downgrade, volume deletion or development graded attempt was run. The first
Android run exposed a MockWebServer reconnect hostname issue from this machine's
wildcard reverse mapping; tests now explicitly use `127.0.0.1` for that server.

## First physical-device E2E procedure — pending

Use the isolated API/account setup, USB reverse commands and error-injection procedure
in [the Phase 4.2 checklist](android-srs-review.md#physical-device-checklist-pending).
Keep the development API on port 8000 untouched; run a separate backend on 8001 with
an explicitly selected isolated synthetic database. Check OpenAPI for the new
`/api/v1/me/srs/session-targets` route and `StageQuestion.character_count` before starting.
Register synthetic accounts and prepare reviewed synthetic single/multiple-POS,
skipped-POS and ungradable fixtures with existing local authoring tools. Do not reuse
development credentials or write graded attempts for real learners.

1. Build/install against the isolated API:
   `adb -d reverse tcp:8001 tcp:8001`, then from `android/`,
   `.\gradlew.bat installDebug '-PDEV_API_BASE_URL=http://127.0.0.1:8001/'`.
2. Verify empty/loading/error dashboards, all six mastery levels and due/later counts.
   With more than 100 synthetic due words, repeat bounded sessions and verify selection
   includes words outside the old first page, no duplicates and different possible orders.
3. On first handwriting use, observe model download, temporarily deny network to exercise
   retry/fallback, then restore network. Write 口, 学生, 你好, 图书馆 and 对不起 against
   corresponding reviewed fixtures. Select each candidate explicitly; switch slots,
   undo/clear, retry one character and correct a candidate. Verify no implicit submission.
4. Rotate mid-gesture and after candidate selection; background and return; navigate
   through Home/Review; exercise normal OS process recreation. Confirm the queue,
   completed progress, strokes and candidate choices remain. Verify fallback preserves
   separate handwriting/keyboard drafts and submits actual learner Chinese text.
5. Complete PASS and FAIL cases for each stage. Check that future-stage answers remain
   hidden until Continue, all meanings/context remain readable, single/multiple POS
   follow server options, and skipped POS never sends a fabricated answer. Compare
   resulting mastery and local displayed review time with authoritative finalization.
6. Drop creation/submission/finalization responses using a controlled test proxy as in
   Phase 4.2. Inspect keys/IDs in debugger or isolated read-only DB queries, without
   logging tokens or answer bodies. Verify one attempt, stable submission keys and one
   scheduling update. Check expired/unavailable words can be skipped without penalty.
7. Finish the session. Verify PASS/FAIL/skipped counts, mastery changes, progress and
   dashboard refresh. Log out/sign in as another synthetic learner and verify no old
   queue, handwriting, candidates or pending answer remains.
8. Run the compiled fake UI tests if desired:
   `.\gradlew.bat connectedDebugAndroidTest '-Pandroid.testInstrumentationRunnerArguments.class=com.example.chineselearningapp.ReviewHandwritingUiTest,com.example.chineselearningapp.ReviewNavigationTest'`.

Record device model/API, network/model-download state, app/API source versions,
synthetic fixtures and observed outcomes. **No physical-device or emulator execution
has been performed in this phase.**
