# Review-engine and policy deployment complete — 2026-10-28

**Local development is deployed:** migration `0012_srs_review_engine`, with exactly
**2,148 installed policies**. Migration and policy installation received separate
explicit operator authorizations. No real review attempt or Android change was
authorized or performed.

Target: `chinese_learning`, `127.0.0.1:5432`, role `postgres`.
The [migration receipt](srs-0012-deployment-20261028.md) records the preceding
migration/preservation checks. The
[machine-readable final verification](../srs-deployment-verification-20261028.json)
records policy integrity, runtime coverage, read-only API checks and test results.

## Approved installation

Before execution, the stopped-backend preflight reconfirmed target identity,
revision 0012, the empty policy table, approved migration/bundle hashes, backup hash
and all 34 original table fingerprints. The operator approved this exact bundle:

`docs/datasets/srs-catalog-policies-v1.json`

SHA-256: `1eda6b46b0c568c9bfaa891f83cc05be14e21d77cffaa1df5c7d33e97fce77b2`.

Executed exactly once from `backend/`, successfully:

```powershell
.venv\Scripts\python -m scripts.review_policies --file ..\docs\datasets\srs-catalog-policies-v1.json --install
```

Result: **2,148 validated, 2,148 inserted, zero unchanged**. This was the only
development policy-writing command. No catalog, account, collection, attempt,
mastery, schedule or historical row was modified. No new schema migration was run
during policy installation.

## Final integrity and preservation

| Check | Result |
| --- | --- |
| Installed policy rows | Exactly 2,148 |
| Stored policy payloads | Match all approved bundle payloads exactly |
| Runtime gradable catalog identities | 2,148 |
| Published unresolved / unpublished excluded | 656 / 6 |
| Duplicates / stale bindings / unexpected conflicts | 0 / 0 / 0 |
| Prepared manual policy payloads | All three preserved verbatim |
| Original data tables | All 34 row-count/SHA-256 fingerprints unchanged |
| Catalog / published | 2,810 / 2,804, unchanged |
| Users / password credentials / sessions / refresh credentials | 3 / 3 / 13 / 29, unchanged |
| Saved vocabulary | Same one row, owner and catalog identity |
| Mastery and SRS state | Mastery 0, LEARNING step 0; generation/progress/review counters unchanged at zero |
| Personal vocabulary / retired wordbook / legacy SRS rows | 0 / 0 / 0, unchanged |
| Review attempts / review results | 0 / 0 |
| Lesson runs / scene checkpoints | 1 / 2, unchanged |
| Alembic metadata | No new upgrade operations detected |

Every catalog record was checked using runtime policy resolution. The 656 published
unresolved records remain ungradable. Categories are compound/unsupported POS,
missing/shared Hán-Việt cues and unsuitable prompt text; the held alternate `谁`
pronunciations remain excluded. Counts and examples remain in the
[coverage report](../srs-policy-preparation.md).

Idempotency was checked **without a second installation**:

```powershell
.venv\Scripts\python -m scripts.review_policies --file ..\docs\datasets\srs-catalog-policies-v1.json
```

PostgreSQL read-only transactions were enforced. Result: **2,148 validated,
2,148 unchanged, zero inserted**. The final policy-table fingerprint also matched
after backend/API checks. Runtime and all original data were checked read-only.

## Backend restart and API verification

The backend is running hidden at `http://127.0.0.1:8000`, with access logging
disabled and the existing `logging.json` configuration. Startup command:

```powershell
.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log --log-config logging.json
```

The Windows launcher PID is 11136; the verified loopback listener PID is 8772.
Process IDs are snapshots; check the current listener before later maintenance.

Live HTTP checks used **GET only**:

- `/health` and `/api/v1/health`: 200.
- `/openapi.json`: 200; all eight SRS routes present with Bearer security.
- Dashboard, due queue, review targets, progress, question and dictionary reads
  without credentials: 401, with `Cache-Control: no-store`.

No real login, token refresh or authenticated learner action was performed.
Authenticated live HTTP success was not claimed because deployment had no supplied
raw session token. Read-only development service checks verified dictionary
search/detail and every owner's dashboard/due/targets/progress. The existing saved
word is now a due, gradable target; the other two accounts remain empty.

Authenticated HTTP grading and policy regressions ran against the existing isolated
test database `chinese_p41c_regular_65467151fc`: **38 passed, one independent-connection
test deliberately deselected**, 7.63 seconds. Synthetic fixtures were rolled back;
these were not real development review attempts. The earlier full suite remains
318 passed, seven optional checks skipped. It was not rerun against development.

## Backup, evidence and Phase 4.2

Verified pre-migration archive remains at:
`backend/.vocabulary-backups/review-deploy-20261027T164815Z/before-0012.dump`.
Size: 2,877,420 bytes. SHA-256:
`0b6fad1e921e9f2b9d3904f4bfd0aaa2f272df6a0efcc0a4fb5ff028eb2659a0`.
Its full-read/isolated restore/upgrade rehearsal and unchanged source fingerprints
are recorded in the [readiness receipt](srs-0012-deployment-readiness-20261027.md).
No database reset, downgrade, restore over development or volume deletion occurred.

Private ignored evidence in that directory includes the pre/post-migration receipts,
`policy-verification-before-api-restart.json`, `live-api-checks-20261028.json`,
`final-verification-20261028.json`, `backend.pid` and backend stdout/stderr logs.
No raw account credentials or tokens are included in public receipts.

There are **no observed deployment blockers**. Phase 4.2 can implement the existing
server protocol; the [Android handoff](../srs-phase-4.2-integration.md) provides exact
dashboard/queue/start/stage/feedback/finalization contracts. Android must display
the entire supplied prompt, including Hán-Việt, character count and Vietnamese
meanings, and use server grading and schedules. No Android build, emulator or device
validation is claimed during this deployment.
