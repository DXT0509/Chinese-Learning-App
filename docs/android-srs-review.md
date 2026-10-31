# Android SRS Review — Phase 4.2 stabilization

Phase 4.3 now adds handwriting, multi-character recognition, randomized bounded sessions,
summary and recovery refinements. See [current experience and device handoff](srs-phase-4.3-experience.md).
The Phase 4.2 details below remain historical verification and setup context.

The Review tab uses `ReviewViewModel` scoped to the authenticated navigation graph,
a framework-free `ReviewRepository`, `RemoteReviewRepository` and authenticated
Retrofit `ReviewApi`. Backend display/recovery contracts now close the three original
API gaps. Grading, scheduling, dependencies and database schema are unchanged.
No new migration is required; no development data or real learner attempt was changed.

## Improved contracts

- Dashboard adds `mastery_distribution`, six ordered `{mastery_level,count}` buckets
  covering levels 0–5. The existing aggregate SQL query calculates these alongside total
  and due counts, for the same owned active/available vocabulary. Zero buckets are
  explicit. Removed, suspended and foreign records are excluded. The due queue is
  limited to 100 for ordering; it is never used to infer the histogram.
- Creation accepts optional `request_id` UUID. The existing attempt primary key stores
  it; no new table/column is necessary. Ownership is checked first. Saved-row locking
  serializes identical retries, while `INSERT ... ON CONFLICT DO NOTHING` protects
  simultaneous cross-identity collisions. Such conflicts return generic 409 without
  disclosing another attempt. A replay returns the pinned original initialization,
  even after completion or expiry; GET question reports current status or 410.
- Finalization adds `previous_mastery_level` from immutable initialization `state_before`
  and `resulting_mastery_level` from finalized `state_after`. Replays never substitute
  newer shared progress. For stale/practice attempts, `scheduling_applied:false` means
  this attempt did not change schedules, even if another attempt changed progress since
  initialization. All grading/transition/interval rules are preserved.

Old clients can still omit `request_id`; their start behavior is unchanged. Existing
response fields and status codes remain. Updated Android always sends the key. Deploy
this backend source before the Android update: old backend builds reject the new body
with 422. Android does not silently fall back to unsafe unkeyed creation. An old dashboard
without histogram shows unavailable instead of invented counts. An old final response
without previous mastery shows unavailable rather than a separate progress read.

## Android reliability

The selected saved ID and creation key are written to identity-scoped SavedStateHandle
before the HTTP call. Network/5xx retry, foregrounding and normal process restoration
reuse exactly that body/key. A lost response after commit recovers the same attempt.
Cancellation is rethrown. Double taps are blocked synchronously. A legacy ambiguous
creation restored from an older app version has no recovery key and still requires
explicit abandonment. Ownership changes discard all saved review state.

Submissions retain their own exact body/key until GET question succeeds. Replays fetch
current state so an older submission response cannot rewind the exercise. 409 reconciles;
422 permits corrected input, while 410/429 offer deliberate replacement. Finalization
replays are atomic; the UI counts each completed attempt once and refreshes dashboard,
due queue and authorized targets. Previous mastery is displayed only from finalization.

A session freezes its selected target identities. Complete server Hanzi cues render
without truncation; Pinyin and single/multiple POS follow the returned question. POS
always submits an array. Feedback is shown before future-stage content; skipped POS
creates no answer. The installed Chinese keyboard supplies text through a callback
that can later accept recognition output. No local grader or scheduler exists.

## Executed verification — 2026-10-28

- Backend: **320 passed, 10 skipped**, with one existing Starlette/httpx deprecation
  warning. Optional migration/maintenance rehearsals without their dedicated URLs were
  skipped, not counted as validated. Existing scheduler and grading regressions passed.
- Independent-connection races passed for creation, submissions and finalization.
  Six simultaneous identical starts yield one attempt; cross-owner collisions yield
  one success and a generic conflict. Fault injection rolls back a creation before
  commit; post-commit replay, expiry and completion never allocate a replacement.
- Histogram tests cover every level, zero buckets, empty collections, due/later words,
  suspension/removal and owner isolation. Historical final mastery survives later progress
  changes. Authenticated HTTP tests cover ownership, strict input and legacy starts.
- `alembic check` on the isolated regular test database: no new upgrade operations.
- Android: **88 unit tests passed**, no failures/errors/skips. Includes connection loss
  before creation, lost creation response, same-key 5xx/auth retries, restoration,
  authoritative final mastery, server histogram, submissions and all stage error paths.
- Debug assembly, lint and instrumented-test Kotlin compilation passed. Lint: **0 errors,
  51 warnings**. Instrumented tests and physical-device tests have **not** been executed.
- Changed Python files pass Ruff lint/format checks. No dependency or lockfile changes.

The initial backend run encountered an inaccessible system pytest temporary directory.
A fresh workspace `--basetemp` and cache directory resolved it. The successful rerun used
fresh synthetic databases, existing Alembic history through 0012, and publication opt-ins
disabled. All fixtures/databases were retained; no resets, downgrades or drops occurred.
Database names (credentials were inherited in memory and never printed):

| Purpose | Database |
| --- | --- |
| Regular suite | `chinese_srs_stable_regular_f2c2e57cd8` |
| Scheduler race | `chinese_srs_stable_srs_race_8313d6f805` |
| Review race | `chinese_srs_stable_review_race_a3c589031c` |
| Creation race | `chinese_srs_stable_creation_race_02cd913806` |

For a rerun, use separate isolated migrated databases for `TEST_DATABASE_URL`,
`SRS_CONCURRENCY_TEST_DATABASE_URL`, `REVIEW_CONCURRENCY_TEST_DATABASE_URL` and
`SRS_CREATION_CONCURRENCY_TEST_DATABASE_URL`. Committed concurrency fixtures remain;
provision new empty databases for another full concurrency run. Never reset existing ones.
Set `DATABASE_URL` to the isolated regular database for `alembic check`. Disable all three
publication opt-ins globally; individual tests opt in as needed. From `backend/`:

```powershell
# Choose fresh paths; pytest manages only these test-owned directories.
.venv\Scripts\python -m pytest -q --tb=short --basetemp .phase4-postgres/tmp-new-run -o cache_dir=.phase4-postgres/cache-new-run
.venv\Scripts\python -m alembic check
```

From `android/`:

```powershell
.\gradlew.bat testDebugUnitTest assembleDebug lintDebug compileDebugAndroidTestKotlin
```

## Physical-device checklist (pending)

Use **only an isolated synthetic test database and test learner accounts** for every
graded manual test. Do not use the development backend on port 8000 or a real development
account. Prepare reviewed synthetic words for SINGLE_SELECT, MULTI_SELECT and skipped
POS, plus one word without a grading policy, using the existing authoring/policy workflow
before starting attempts. Do not alter a word/policy after it is pinned to an attempt.
The retained review-race database above contains a synthetic multi-POS 学 fixture;
the creation-race database has a synthetic skipped-POS fixture. They contain no real users.
Use separate test profiles/ports to verify each configuration if reusing those fixtures.

1. Start a separate API on **8001**, with `SRS_DEVICE_TEST_DATABASE_URL` locally set to
   the intended isolated migrated database URL. Confirm that database name before starting.
   Do not print its credentials or copy any development accounts/tokens. From `backend/`:

   ```powershell
   $env:DATABASE_URL = $env:SRS_DEVICE_TEST_DATABASE_URL
   $env:ALLOW_CONTENT_PREVIEW = 'false'
   $env:ALLOW_AI_APPROVED_VOCABULARY = 'false'
   $env:ALLOW_LOCAL_CODEX_REVIEWED_VOCABULARY = 'false'
   .venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --no-access-log --loop app.core.event_loop:new_event_loop --log-config logging.json
   ```

   No new migration is needed. Do not point this command at development. Check read-only
   `/openapi.json`: Dashboard must expose `mastery_distribution`, InitializeReview
   `request_id`, and FinalizedResponse both mastery fields. Health alone cannot establish
   contract or database readiness. Keep the existing development API untouched.
2. Connect a USB-debuggable phone, authorize the computer, then from repository root:

   ```powershell
   $srsAdb = "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe"
   & $srsAdb devices -l
   & $srsAdb -d reverse tcp:8001 tcp:8001
   cd android
   .\gradlew.bat installDebug '-PDEV_API_BASE_URL=http://127.0.0.1:8001/'
   ```

   Use a clean test app profile and register new synthetic learner accounts on this isolated
   API. Existing development tokens are not valid here; never import them. Verify release
   HTTPS enforcement remains intact.
3. Before saving words, verify zero due/later counts and all six zero mastery buckets.
   Save the prepared fixtures. Compare dashboard totals/distribution with authenticated
   server responses. Verify the word without a grading policy is explained and never graded.
4. Complete a three-stage PASS: confirm full Vietnamese meanings, Hán-Việt/count/sense cues,
   large Hanzi input via an installed Chinese keyboard, numbered-tone Pinyin guidance,
   future-answer concealment and server-defined POS controls. Verify single selection,
   multiple selection and explicit skipped POS separately. No POS submission for skipped POS.
5. Complete separate FAIL attempts with wrong Hanzi, Pinyin and POS. Continue through every
   applicable stage. Verify first-answer feedback persists, final before/after mastery and
   next time match finalization, and dashboard distribution refreshes after completion.
   Practice/stale finalization must explain `scheduling_applied:false` without claiming growth.
6. Test a connection failure before sending creation (remove the 8001 reverse rule), then
   restore forwarding and Retry. Use a controlled test proxy to drop a creation response
   after server commit as a separate case. Inspect request/attempt IDs via the debugger or
   read-only isolated DB query; never log tokens, answer bodies or hidden keys. Each retry
   must reuse the same creation UUID and leave exactly one attempt, with unchanged `started_at`.
7. Interrupt during Hanzi/Pinyin/POS submission and finalization. Restore forwarding, retry,
   and verify stable submission UUID/body, unchanged first correctness and one schedule update.
   Do not infer which side of commit a random USB disconnect reached; test both boundaries
   deliberately. Automated rollback/MockWebServer tests supplement these manual checks.
8. Switch tabs, press system Back/reenter, rotate, background/foreground and exercise normal
   OS process recreation. The attempt and pending body/key must resume; no new attempt on
   recomposition. Reopen a completed result and confirm stable historical mastery.
9. Let a keyed attempt reach 30-minute expiry. Replaying creation must recover the same
   expired attempt; only explicit replacement generates a fresh key. Check 409 content/key
   conflict, 422 validation, 429 event limit and 401 refresh/login handling in isolated fixtures.
10. Log out and sign in as a different synthetic learner. No previous attempt, text, request
    key or histogram may remain visible. Reusing a creation UUID against another learner's
    saved word must return generic conflict, not foreign attempt data.
11. Run the fake-only navigation/mastery instrumented tests on a dedicated device if desired:

    ```powershell
    .\gradlew.bat connectedDebugAndroidTest '-Pandroid.testInstrumentationRunnerArguments.class=com.example.chineselearningapp.ReviewNavigationTest'
    ```

    Record device model/API, keyboard, app/API revision, synthetic fixture identity,
    observed outcomes and request/attempt IDs without credentials. These tests are compiled
    but remain unexecuted in this handoff.

## Remaining limitations

SavedStateHandle supports normal OS restoration, not durable cross-device session discovery.
Force-stop, task removal or clearing app data can lose the creation key; abandoned attempts
expire without scheduling changes. Legacy keyless ambiguous starts still require abandonment.
Exclusion reports have IDs/codes rather than display names. Handwriting recognition in Review,
offline grading, and explicit hint/reveal controls remain outside this slice. No physical-device
validation is claimed. The default Android backend URL remains unchanged; the 8001 override
above is deliberately limited to isolated manual verification.
