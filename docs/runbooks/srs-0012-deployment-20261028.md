# Review engine 0012 deployment — 2026-10-28

**Historical migration-only receipt.** Migration applied successfully after explicit
operator authorization. Policy installation was subsequently separately authorized
and completed; see the [final deployment receipt](srs-policy-deployment-20261028.md).
At the end of the migration-only step no policies had been installed. Deployment dates
use Asia/Bangkok; private evidence also records UTC timestamps.

Target: `chinese_learning`, `127.0.0.1:5432`, role `postgres`. The operator authorized
only migration 0012, schema/preservation verification and a fresh policy preview.
No other migration, policy write, real review attempt, account mutation or unrelated
database write occurred during this migration-only step. The backend was already
stopped and stayed stopped until the later policy deployment.

## Execution and preservation

Immediately before migration, read-only checks reconfirmed identity, revision 0011,
zero other database clients, migration/bundle hashes, the verified backup hash and
all 34 original table fingerprints. Executed from `backend/`, exit code zero:

```powershell
.venv\Scripts\python -m alembic upgrade 0012_srs_review_engine
```

Verified backup:
`backend/.vocabulary-backups/review-deploy-20261027T164815Z/before-0012.dump`.
Size: 2,877,420 bytes. SHA-256:
`0b6fad1e921e9f2b9d3904f4bfd0aaa2f272df6a0efcc0a4fb5ff028eb2659a0`.
The earlier full archive read, actual isolated restore and exact-data 0011→0012
rehearsal passed; see [readiness](srs-0012-deployment-readiness-20261027.md).
Matching pre-migration fingerprints confirmed that the backup still represents
all current original rows. No database was reset, downgraded, deleted or restored
over development.

Post-migration checks ran read-only:

| Check | Result |
| --- | --- |
| Alembic current | `0012_srs_review_engine (head)` |
| Alembic check | No new upgrade operations detected |
| Runbook preservation verifier and independent guard | All 34 original data table fingerprints match |
| New submissions column | JSONB, NOT NULL, default empty array |
| Submission guard | Function exists; trigger enabled |
| Installed policies / review attempts / review results | 0 / 0 / 0 |
| Catalog / published / held | 2,810 / 2,804 / 6 |
| Users / password credential records | 3 / 3, unchanged |
| Session / refresh credential records | 13 / 29, unchanged |
| Curated saved vocabulary | Same one row, identity, owner and content link |
| Saved SRS state | Mastery 0; LEARNING step 0; progress, generation and review counters 0 |
| Personal vocabulary / retired wordbook / legacy SRS | 0 / 0 / 0, unchanged |
| Lesson runs / scene checkpoints | 1 / 2, unchanged |

Alembic check emitted the previously documented SQLAlchemy reflection
`dialect_options` warning and completed successfully. The full backend suite was
not rerun against development; existing isolated verification remains 318 passed,
seven optional checks skipped. No learner actions were used as migration checks.

## Fresh policy-installation preview

The existing `review_policies --file` command ran **without `--install`**, with
PostgreSQL read-only transactions enforced: 2,148 validated, zero inserts, zero
existing rows and zero conflicts. Preparation was separately rerun against revision
0012 with the three prepared manual policies preserved. The new bundle is
byte-for-byte identical to `docs/datasets/srs-catalog-policies-v1.json`.

Bundle SHA-256:
`1eda6b46b0c568c9bfaa891f83cc05be14e21d77cffaa1df5c7d33e97fce77b2`.

| Proposed installation effect | Records |
| --- | ---: |
| Insert policies | 2,148 |
| Update / delete policies | 0 / 0 |
| Existing installed policies | 0 |
| Automatically prepared questions | 2,145 |
| Prepared manual policies preserved unchanged | 3 |
| Duplicate identities / stale bindings / unexpected conflicts | 0 / 0 / 0 |
| Published unresolved after proposed installation | 656 |
| Publication exclusions | 6 |

Every policy matches the current published vocabulary UUID, version and checksum.
Current installed grading coverage remains **zero**. Automatic questions require
the full Hán-Việt cue, character count and Vietnamese meanings. Unresolved categories
remain compound/unsupported POS, missing/shared Hán-Việt cues and unsuitable prompt
text; both alternate `谁` identities remain held. See [coverage](../srs-policy-preparation.md).

The [machine-readable preview](../srs-0012-policy-installation-preview-20261028.json)
records exact expected effects. Detailed private evidence is in
`backend/.vocabulary-backups/review-deploy-20261027T164815Z/`:

- `immediate-pre-migration-20261027T170055Z.json` and `post-migration-20261027T170113Z.json`.
- `post0012-policy-audit-20261028.json` and `post0012-policies-20261028.json`.
- The original backup, hashes, fingerprints and isolated rehearsal receipts.

## Separate installation authorization (subsequently completed)

After explicit policy-installation approval, recheck target, bundle hash, installed
policy state and unchanged fingerprints, then follow the primary runbook using:

```powershell
.venv\Scripts\python -m scripts.review_policies --file ..\docs\datasets\srs-catalog-policies-v1.json --install
```

The migration-only step stopped before that approval. Subsequent installation,
idempotency verification, backend restart and read-only API smoke checks are
recorded in the final deployment receipt.
No development API request was performed in this migration-only step. There are
no observed schema or preservation blockers. No real review attempt is authorized.

Android implementation remains Phase 4.2. The existing
[server contract](../srs-review-engine.md#actual-http-workflow-and-phase-42-android-contract)
covers initialization, stage submissions, feedback, finalization and resulting
schedule; dashboard/due/progress contracts are in `backend/app/schemas/srs.py`.
The UI must display every required prompt cue and use server grading/scheduling.
No Android files changed.
