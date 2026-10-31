# FSRS-only local deployment — 31 October 2026

**Successfully deployed to local development.** Backend is running at
`http://127.0.0.1:8000`. Production was not a target. The user's explicit authorization
covered replacement, the minimal local backup, migration and backend restart.
No further backup/restore rehearsal was performed.

Machine-readable evidence: [deployment and consistency report](../srs-fsrs-only-deployment.json).

## Active behavior

* **Only scheduler:** upstream `fsrs==6.3.2`, scheduler identifier
  `fsrs-6.3.2/binary-v2`, desired retention 0.90. The fixed-interval transition
  function, its interval table and `SRS_V2_ENABLED` runtime switch are deleted.
  All new scheduling-applied finalizations use `fsrs_scheduler.review`.
* **Grading:** exactly handwritten Hanzi plus tone-correct Pinyin; PASS requires
  both correct and unaided. Either incorrect stage means FAIL. First valid
  answers remain sealed. Ink evidence is mandatory; grading cannot use a keyboard
  fallback. Feedback withholds solutions until both stages are submitted.
* **Planning:** default 1,200 seconds, risk-prioritized selection, persisted random
  presentation order, bounded pending intake, actual active-time receipts,
  session recovery and explicit continuation beyond the target. Planning and
  prefetch never move a vocabulary due date.
* **Progress:** mastery 0–5 is retained as a separate indicator. It cannot calculate
  intervals or override FSRS due dates. Dictionary POS metadata and historical
  POS submissions/policies remain, with no active POS review controls/questions.
* The retired `GET /api/v1/me/srs/session-targets` path is removed from router,
  ReviewEngine and Android Retrofit. New sessions use authenticated
  `POST /api/v1/me/srs/daily-plans`. Existing diagnostic due/progress/policy-report
  reads remain useful and do not schedule words.

## Migration and preserved data

Local database `chinese_learning`: **0012_srs_review_engine → 0014_fsrs_only**.
Existing historical migrations 0001–0013 were left intact. Revision 0013 adds
memory/planner/timing storage and an activation flag. New revision 0014 converts
every existing saved identity to an FSRS card using the pinned upstream library.

**All 35 original data tables matched their before/after row fingerprints.**
The comparison includes every original saved-word column, complete attempt JSON,
all installed policy payloads and authentication/session records. The new activation
column is intentionally excluded from the old-column comparison.

| Records | Preserved |
| --- | ---: |
| Learner accounts / password credentials | 3 / 3 |
| Saved curated vocabulary | 27 |
| Historical review attempts | 20 |
| Installed grading policies | 2,804 |
| Curated catalog entries, including existing holds | 2,810 |
| Existing authentication sessions / refresh credentials | 14 / 40 |

**27 FSRS memory rows were added:** 14 replay actual completed scheduling-applied
outcomes; 13 have no recorded scheduling history and remain unreviewed cards.
No mastery-derived ratings or missing review timestamps were fabricated. Every
memory `last_review` exactly matches its latest recorded scheduling-applied
completion, or remains null when none exists. Card due timestamps match the
unchanged saved-word schedules. Migration performed **zero due-date, mastery,
historical attempt or installed policy updates**. No reset, deletion, downgrade
or volume removal occurred.

The active format projects all **2,804 / 2,804** installed editorial policies into
`handwriting-pinyin-v2`. Source policy versions and snapshot hashes remain pinned
in new attempts. Existing policy rows are preserved byte-for-byte. There is no
new policy installation or three-stage scheduling path. Unfinished historical
attempts are read-only and can be restarted; completed attempts retain their
original results and audit journal.

## Minimal backup

Private ignored artifact:
`backend/.vocabulary-backups/fsrs-only-20261030174649/before-migration.dump`.
Size **3,270,859 bytes**. SHA-256:
`4deab1bd49a28b259128fa7b8063d95588ff43c44043d641102cc05bc3125892`.

Created with pg_dump custom format from an exported read-only PostgreSQL snapshot.
The archive is nonempty and `pg_restore --list` succeeded before migration.
The private `before.json` records the full pre-migration table fingerprints.
No restore was performed or claimed. The dump contains learner/application data
and remains in the ignored local backup directory.

Executed deployment command, from backend:

```powershell
.venv/Scripts/python -m scripts.deploy_fsrs_only --database chinese_learning
```

The script refuses non-development, non-localhost or differently named databases.
Migration and post-upgrade `alembic check` succeeded before starting the backend.
If recovery is needed, stop review writes, retain all FSRS evidence and prefer a
forward fix. Restoring over newer learner history requires a separately reviewed
recovery decision. An old scheduling algorithm is no longer a runtime option.

## Backend restart and live checks

Started hidden with `.venv/Scripts/python -m app`, the existing psycopg-compatible
event loop and safe JSON logging. Access logging and reload remain disabled.
Launcher PID **21736**, verified listening worker PID **14112**, bound to
`127.0.0.1:8000` (PIDs are a verification snapshot).

| Live HTTP check | Result |
| --- | --- |
| `/health`, `/api/v1/health`, `/openapi.json` | 200 |
| Dashboard without credentials | 401 |
| Daily-plan POST without credentials | 401; no plan created |
| Retired random-session route | 404 and absent from OpenAPI |
| Dashboard scheduler version in live contract | `fsrs-6.3.2/binary-v2` |

Post-restart database-enforced READ ONLY service checks covered **all 3 accounts**.
Their daily targets are 1,200 seconds; the two accounts with vocabulary have 1 and
25 due words respectively; the empty account has none. The cold-start estimate
is 45 seconds/word because legacy attempts lack measured active durations.
Estimated backlogs are 45 and 1,125 seconds. These are workload estimates, not a
promise of complete coverage within 20 minutes. No new real learner attempt,
authentication session or daily plan was created for verification.

## Tests and Android readiness

Full isolated backend suite: **400 passed, 10 optional checks skipped**, 90.87
seconds. Separate databases exercised real concurrent submissions/finalizations.
Skipped tests require separately gated older migration/operator/reset database
URLs; none is treated as a successful test. A further strengthened nonempty
0012→0014 rehearsal **passed** with both recorded PASS/FAIL history and an
unreviewed identity, checking exact upstream replay, all original columns and
retention of future due dates. Isolated and development `alembic check` passed.
Changed Python files passed Ruff; `pip check` passed.

```powershell
# backend — fresh isolated databases, fixtures retained
.venv/Scripts/python -m scripts.srs_v2_isolated_checks
# android
.\gradlew.bat testDebugUnitTest assembleDebug lintDebug compileDebugAndroidTestKotlin --console=plain
```

Android: **132 unit tests passed**, debug assembly passed, lint **0 errors / 78
warnings**, instrumentation compilation passed. Request-count/prefetch, recovery,
binary grading, ink transport, timing and optional-continuation regressions pass.
The lower backend count than the earlier preview reflects removal/replacement of
obsolete fixed-interval and randomized-session tests; two-stage and FSRS coverage
remain, with an explicit no-v1-fallback architecture check.

APK: `android/app/build/outputs/apk/debug/app-debug.apk`. SHA-256:
`7486e0f625a289579f3a636904ab2783f3a9c4dce1749885839d0743a585f9c1`.
**Ready for physical-device testing; not installed by this deployment.** Device
ML Kit download/native recognition, touch/stylus behavior and frame pacing still
need physical validation. Instrumentation compilation is not device execution.
Use the USB workflow and this matching APK. Any graded validation that should not
alter real learner progress belongs in an isolated synthetic environment.

Known limits remain documented in [SRS v2](../srs-v2.md): client ink is structurally
validated but does not attest physical origin against a modified client; active
time uses five-second sampling. Historical v1 workload figures in the earlier
simulation JSON are frozen comparison evidence, not a maintained runtime algorithm.
