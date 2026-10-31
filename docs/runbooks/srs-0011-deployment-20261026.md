# SRS 0011 local deployment — 2026-10-26

**Applied successfully following explicit operator authorization.** Target:
`chinese_learning`, `127.0.0.1:5432`, role `postgres`. Revision advanced from
`0010_local_codex_review` to `0011_srs_foundation (head)`. No other migration,
review/session submission, account mutation or unrelated database write was performed.
Phase 4.1B was not started.

## Execution and backup

The API reload process tree was stopped before migration and restarted only after
preservation/schema verification passed. The pre-migration read-only checks reconfirmed
database identity, revision, all 34 table hashes against the approved baseline, backup
SHA-256, and absence of other active database clients. The only other connection was
an idle pgAdmin session. No database client was terminated or modified.

Executed from `backend/`:

```powershell
.\.venv\Scripts\python -m alembic upgrade 0011_srs_foundation
```

Exit status: zero. The verified backup remains at:

`C:\Users\ADMIN\AndroidStudioProjects\ChineseLearningApp\backend\.vocabulary-backups\srs-0011-20261026T160906Z\before-0011.dump`

Archive size: 2,871,784 bytes. SHA-256:
`fa4bed32d5058c3025f3eefaf194225b5a556cb9c4f17273b77d69c1c0a4123d`.
Prior archive/full-read and actual isolated restore checks passed; source and restored
data matched across all 34 original tables. See the
[preparation snapshot](srs-0011-readiness-20261026.md) for details.

## Post-migration results

Verification completed at `2026-10-26T16:56:15Z` (23:56:15 Asia/Bangkok), using
read-only transactions. Alembic `current` and `check` were also run with PostgreSQL
`default_transaction_read_only=on`.

| Check | Result |
| --- | --- |
| Alembic current | `0011_srs_foundation (head)` |
| Alembic check | No new upgrade operations detected |
| Original data preservation | All original columns in all 34 tables matched expected hashes; only revision and approved null due-time backfill changed |
| Tables | Original 34 plus `srs_review_attempts`; no unexpected tables |
| Catalog | All 2,810 entries and original contents preserved |
| Publication | 2,804 LOCAL_CODEX_REVIEWED and six NEEDS_REVIEW; 2,804 visible |
| Accounts / password credentials | Three / three, all original values preserved |
| Sessions / refresh credentials | 13 / 29, all original values preserved |
| Curated saved vocabulary | Same single saved UUID, owner, catalog link, mastery 0, save time, active flag and last-review time |
| Backfill | One row; LEARNING step 0; promotion/generation/counters zero; due time equals its original save time |
| Legacy snapshot | Original mastery and timestamps retained, including the original null due time |
| Preservation errors / null due times | Zero / zero |
| Duplicate progress / review attempts | Zero / zero |
| Legacy personal vocabulary and SRS | Original empty tables retained unchanged |
| Lesson runs / checkpoints | One / two, original values preserved |
| Dictionary service search/detail for `口` | Passed against migrated development, read-only |
| SRS dashboard, due queue, owned progress services | Passed against migrated development, read-only; grading unavailable |

Compared all public column definitions and indexes, constraint names/validation flags,
and exact SRS constraint definitions, history trigger and function with the verified
migrated restore. These matched. An initial broader textual comparison found seven
legacy CHECK expressions whose equivalent array casts were rendered differently by
dump/restore; these were inspected and left unchanged. The preexisting legacy
`ck_lessons_valid_type` NOT VALID flag also remains unchanged. No schema repair was
needed or attempted. Alembic reported no metadata drift.

The existing SQLAlchemy reflection warning occurred during `alembic check`; it did
not prevent schema validation. No production-like mutation was used to demonstrate
history/idempotency constraints. Their behavior was exercised in the previously
completed isolated regression suite: **245 passed, seven optional checks skipped**,
including nonempty SRS/legacy upgrades, rollback and independent-connection concurrency.
That suite was not rerun against development.

## API restored and checked

Restarted the same local Uvicorn app with reload, `127.0.0.1:8000`, and documented
`--no-access-log --log-config logging.json` settings. The process runs hidden; logs are
in the ignored private evidence directory. No credentials were printed or changed.

- GET `/api/v1/health`: 200.
- GET `/api/v1/me/srs/dashboard` and `/due` without credentials: 401.
- GET `/api/v1/dictionary/search?q=kou3` without credentials: 401.
- Live OpenAPI exposes dashboard, due queue, owned progress and session initialization.

No token was invented, no login/session was created, and no review was submitted.
Authenticated HTTP success cases remain covered by the isolated test clients; the
development service reads above verify runtime database compatibility without account
mutation. Grading remains disabled, as designed for Phase 4.1A.

## Evidence and remaining work

Private evidence is retained in the backup directory:
`development-postmigration.json`, `development-alembic-current.log`,
`development-alembic-check.log`, and `development-api-smoke.json`.
The operational verifier is `backend/.vocabulary-backups/srs_postdeploy_20261026.py`.
All verification database operations were read-only; only the authorized migration
changed development data/schema.

Deployment and documented post-migration verification are complete. There are no
remaining deployment blockers. The existing Phase 4.1B plan remains planning only;
no grader, stage lifecycle or Android UI implementation was added. No Android build,
emulator or physical-device validation is claimed.
