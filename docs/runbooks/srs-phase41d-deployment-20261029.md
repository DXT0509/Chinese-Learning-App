# Phase 4.1D deployed and verified — 2026-10-29, Asia/Bangkok

**Local development is deployed: 2,804 / 2,804 published identities have valid
installed grading policies.** The operator explicitly authorized the exact bundle,
656 missing-policy inserts, verification, backend restart and isolated regression
tests. No real graded attempt was submitted and no Android code was modified.

See the [machine-readable deployment verification](../srs-phase41d-deployment-verification-20261029.json)
and preceding [readiness report](srs-phase41d-deployment-readiness-20261029.md).
The [complete-installation runbook](srs-phase41d-complete-installation.md) was
followed; this receipt supersedes its earlier undeployed status statements.

## Exact authorized installation

Target: `chinese_learning`, `127.0.0.1:5432`, role `postgres`.
Alembic remains `0012_srs_review_engine`; **no migration was applied**.

Bundle: `docs/datasets/srs-phase41d-complete-v2.json`.
SHA-256: `abae251396a78ffc12cfa535374751954f4cde060a330bbb8491e89e428e81e2`.

Immediately before writing, the bundle, verified backup and reviewed source hashes
matched; the exact database identity/revision and all 36 pre-installation table
fingerprints matched. The backend was stopped and no other client database
connections remained. Fresh read-only validation still proposed precisely 656
inserts and no updates. Explicit operator authorization was recorded privately.

Executed **once**, successfully, from `backend/`:

```powershell
.venv\Scripts\python -m scripts.review_policies --file ..\docs\datasets\srs-phase41d-complete-v2.json --install
```

Result: **2,804 validated, 656 inserted, 2,148 unchanged, zero updates,
deletions or conflicts**. The 656 comprise the earlier 414 prepared additions and
the remaining 242 individually reviewed policies. The importer committed one
policy-only transaction. No second development installation was run.

## Installed coverage and integrity

| Level | Published | Runtime-valid installed | Coverage |
| --- | ---: | ---: | ---: |
| 0 | 218 | 218 | 100% |
| 1 | 289 | 289 | 100% |
| 2 | 158 | 158 | 100% |
| 3 | 294 | 294 | 100% |
| 4 | 599 | 599 | 100% |
| 5 | 1,246 | 1,246 | 100% |
| Total | 2,804 | 2,804 | 100% |

Every published identity was checked through the runtime resolver. All installed
payloads match the exact authorized bundle. Duplicate policies: **zero**. Stale
version/checksum bindings: **zero**. Read-only revalidation reported **2,804
unchanged, zero proposed inserts/updates and zero actual inserts**.

The catalog remains 2,810 records. All six unpublished identities remain excluded
and ungradable: `不客气|bu4 ke4 qi5`, `什么|shen2 me5`, `厕所|ce4 suo3`,
`没关系|mei2 guan1 xi5`, `谁|shei2`, `谁|shui2`. No pronunciation identities were
merged and no published vocabulary was replaced.

## Preservation and recovery evidence

All **35 non-policy tables** matched their complete pre-installation row-count/
SHA-256 fingerprints. Comparison includes complete attempt submission journals,
catalog/revision/publication evidence, users and authentication records, saved
words, mastery, SRS schedules and review history. The **2,148 original policy rows**
also matched, including their row metadata. After restart, API/service reads and
regression tests, all 36 post-installation table fingerprints still matched.
Every fingerprint comparison used UTC without changing the database's timezone.

The preserved baseline includes three users, 2,810 vocabulary rows, **27 saved-word
rows**, **one existing SRS attempt**, and zero curated review-submission rows.
Existing attempts remain pinned and were not rewritten or finalized. No login,
token refresh, attempt initialization, graded submission or progress update was
performed against development.

Verified pre-installation backup:
`backend/.vocabulary-backups/phase41d-deploy-4ed7b8af8b1f/before-installation.dump`.
Size: 3,115,721 bytes. SHA-256:
`521f05da564830f6466a44c69119024c5bac49cbc5d0eff0255e22c21f91cf1b`.
Archive listing and a full isolated restore matched all 36 original source tables.
The isolated rehearsal also verified 656 inserts, idempotent reimport, full runtime
coverage, original policy preservation and unchanged non-policy data. No database
reset, downgrade, development restore or volume deletion occurred. Private snapshots,
authorization, installation output and logs remain beside that backup.

## Running backend and read-only checks

The updated backend runs hidden at **http://127.0.0.1:8000**, started with
`.venv/Scripts/python -m app` from `backend/`. It uses the psycopg-compatible loop
and existing safe JSON logging; access logging and reload are disabled. Launcher
PID: 22572; verified listening worker PID: 14272. PIDs are snapshots—check the
current listener before future maintenance.

GET-only live checks passed:

- `/health`, `/api/v1/health` and `/openapi.json`: 200.
- All nine SRS operations present in OpenAPI with Bearer security.
- Dashboard, due queue, review targets, randomized session targets, progress and
  question routes without credentials: 401 with `Cache-Control: no-store`.
- Question schema does not expose internal accepted-answer or policy-review fields.

Live owner service reads ran under database-enforced read-only transactions for
all three owners: dashboard, due, saved progress, review targets and bounded random
selection. **All 27 available saved words are eligible; no missing-policy or other
saved-word exclusions remain.** All 27 progress rows were inspected without writes.
Authenticated live HTTP success was not claimed without an existing raw token;
no real session was created to obtain one. Authenticated HTTP behavior was tested
using isolated synthetic accounts in the regression suite.

## Regression results and physical Android readiness

Full backend suite after installation: **365 passed, 13 optional checks skipped**,
77.34 seconds, with one existing Starlette/httpx deprecation warning. Both default
and test database URLs were explicitly set to isolated
`chinese_p41d_final_tests_0dfe58e5bd`; development was not a test target. The test
database had zero users/saved words before and after the suite. Optional dedicated
migration/race database URLs were not configured. Post-test isolated
`alembic check` passed. Tests cover strict Hanzi/Pinyin and contextual grading,
first-answer/assistance FAIL, ownership/replay, policy preservation and SRS behavior.

**Backend and the updated debug APK are ready for physical-device testing.** All
141 Android source files and the existing APK hash are unchanged by deployment.
The preceding implementation verification recorded 109 passing Android unit tests,
successful debug assembly and lint; these Android checks were not rerun for this
backend-only deployment. No emulator/device validation or APK installation was
performed.

APK: `android/app/build/outputs/apk/debug/app-debug.apk`.
SHA-256: `e2c0fb33b3803fa6c78702d2a5831a544d59baa4cbd9620f4def48e6f06cfbe3`.
Its debug API URL is `http://127.0.0.1:8000/`, and it includes the Vietnamese labels
for the new classification choices. Use this updated APK rather than an older
installed client. For USB connectivity, forward `tcp:8000` with `adb reverse` as in
[the USB guide](../android-usb-development.md).

Use a new synthetic review session when validating the new policies; historical
attempts intentionally keep their original pinned targets. For graded physical
E2E tests that must preserve development progress, follow the
[isolated port-8001 checklist](../srs-phase-4.3-experience.md#first-physical-device-e2e-procedure--pending)
and build the client with that isolated API URL. Device installation, model download,
handwriting/touch behavior and full physical E2E execution remain to be recorded.
