# SRS intermittent connection failures and variable transitions ? 30 October 2026

## Evidence and fixes

Read-only `adb logcat -d -s ReviewTiming` from the connected phone showed attempt
creation taking 1,301?3,304 ms, with answer requests usually 43?136 ms. One tap while
prefetch was incomplete waited about 2,922 ms; a ready-prefetch tap took about 136 ms
including the frame scheduling proxy. These are existing device logs from 29?30 October,
not newly graded test reviews. Failure categories were absent from the old logs, so they
do not prove the exact cause of every original intermittent failure.

A development-catalog audit used **SET TRANSACTION READ ONLY**, then rolled back.
No attempts, mastery, saved words or schedules were written. The catalog had 2,810 rows.
The old runtime validator regenerated policies for all catalog words per transaction,
even when initializing one word. Full v1 preparation took 1,029?1,410 ms; v2 took
2,740?3,906 ms across the observed runs. CPU contention differed between runs.

Runtime validation now generates only the requested identity. **All catalog rows still
participate in cue, pronunciation, overlapping-meaning and publication checks**, including
unpublished collision peers. The installation/publishing generators keep their existing
full-catalog default. The target-report endpoint requests its whole page as one batch,
so it does not repeat the generator for every row. Generated results and catalog entries
remain transaction-scoped; no stale cross-request policy cache was introduced.

During a read-only run concurrent with Android build work, generation-only timing was:

| Generator | Full catalog | Requested identity mean / max | Equality checked |
| --- | --- | --- | --- |
| v1 | 1,409.71 ms | 26.13 / 60.91 ms | 10 sampled identities |
| v2 | 3,905.73 ms | 88.12 / 116.90 ms | 10 sampled identities |

Catalog loading in that run was 200.22 ms. Separate complete read-only resolver samples,
including database reads and catalog validation, were 650.20 / 177.87 / 161.66 ms for v1
and 238.68 / 242.41 / 229.62 ms for v2. All six remained gradeable. The first v1 sample
was cold. These are local resolver measurements, not an end-to-end phone benchmark;
there is no promise that every navigation will finish in those times.

The SRS-specific Retrofit factory had disabled `retryOnConnectionFailure`, unlike the
other APIs. A reused HTTP connection can disappear after idle or during a request;
this configuration forced the learner to retry manually. The review API now retains
normal OkHttp transport recovery. It does not add delays or blanket retries for HTTP
errors. Existing creation UUIDs, persisted submission keys and one-time finalization
make replay safe even if the server committed before the connection broke.

MockWebServer reproduced the lost-connection case on a previously used connection for
creation, submission and finalization. Recovery resent exactly the same path and body,
including the same identifiers. This validates that transport scenario; it does not
establish that all historical phone failures were caused by stale sockets.

## Clearer failure diagnosis

The old screen mapped HTTP 5xx, parsing errors, timeouts and IO errors to ?M?t k?t n?i?.
It now distinguishes:

- Transport: ?M?t k?t n?i. Th? l?i ?? ti?p t?c.?
- Timeout: ?Ph?n h?i qu? l?u. Th? l?i ?? ti?p t?c.?
- HTTP server error: ?M?y ch? ?ang g?p l?i. Th? l?i ?? ti?p t?c.?
- Unreadable response: ?Ch?a ??c ???c d? li?u. Th? l?i ?? ti?p t?c.?

Retry and all persisted idempotency keys remain. Expiry, invalid input and unavailable
content keep their existing specific handling. Cancellation is propagated.

Debug Android `ReviewTiming` now records fixed failure categories (`transport`, `timeout`,
`http_500`, etc.), never exception messages. Development backend logs record SRS route
**templates**, status and elapsed milliseconds. Unexpected failures additionally log a
fixed database connection/pool/operation/application category, never SQL, parameters,
driver exception text, tokens, actual attempt IDs, answers or request payloads.
The installed FastAPI exposes route templates without the outer `/api/v1` prefix;
logging accepts that form as well as fully prefixed templates. Production does not
emit the development request timings.

## Verification and deployment

- Android full unit suite: **122 passed**, zero failures/errors/skips. Debug build,
  lint and instrumentation compilation passed; lint has **0 errors, 74 warnings**.
- Full isolated backend regression: **386 passed, 10 skipped**; existing Starlette/httpx
  warning plus a pytest cache-permission warning. The final affected-test run disables
  pytest cache writes. Fresh separate concurrency databases covered scheduling,
  creation and stage/finalization races.
- Affected backend integration/unit suite after the final batching/logging changes:
  **87 passed, 1 skipped**, no warnings, **15.76 seconds**. The skipped independent
  connection race was already included in the full run with its dedicated database.
- `alembic check`: no new upgrade operations. No schema or dependency changes.
- Target-selection tests compare full versus selected output, including cue/form/gloss
  collisions, unpublished peers and transaction cache invalidation. Logging tests
  inject SQL/credential-like exception text and assert that neither it nor actual
  attempt IDs appear in diagnostic logs.

Database tests used port 55444 only, in the retained synthetic cluster
`backend/.test-postgres-slice2-phase44`: regular `chinese_phase44_regular` plus fresh
`chinese_reliability_review_race`, `chinese_reliability_schedule_race` and
`chinese_reliability_creation_race`. No development migration or learner write occurred.
The isolated cluster is stopped after testing; its data is retained.

The running development API uses `--reload`; source updates are reloaded automatically.
**The Android change requires installing the newly built debug APK over the current app.**
No phone APK installation, activity recreation, force-stop or real grading was performed
in this diagnostic pass. APK: `android/app/build/outputs/apk/debug/app-debug.apk`.

For the next physical check, use an isolated account/API. Leave each stage idle for
more than five seconds, then submit; test Continue both immediately and after prefetch.
Collect `adb logcat -s ReviewTiming` and the safe backend events if a failure recurs.
A connection failure should retain the same creation/submission ID. A 5xx should now
be identified as a server problem, so remaining failures can be investigated without
mistaking every cause for loss of network. Do not grade development learner data as a test.

## Changed files in this follow-up

- Android: `core/di/AppModule.kt`; review `ReviewViewModel.kt`, `ReviewScreen.kt`,
  `ReviewTiming.kt`, `RemoteReviewRepository.kt`; `res/values/review_strings.xml`;
  `ReviewRepositoryTest.kt`, `ReviewViewModelTest.kt`.
- Backend: `app/services/policy_preparation.py`, `policy_coverage.py`, `review_targets.py`,
  `review_engine.py`; `app/main.py`; new `tests/test_review_policy_selection.py` and
  `tests/test_review_failure_logging.py`.
- Documentation: this report and a follow-up link in the Phase 4.4 report.

Ignored evidence logs: `srs-reliability-android.log`, `srs-reliability-backend-full.log`,
`srs-reliability-backend-targeted.log`, `srs-reliability-catalog-timing.log`,
`srs-reliability-resolve-timing.log`, `srs-reliability-alembic.log`.
