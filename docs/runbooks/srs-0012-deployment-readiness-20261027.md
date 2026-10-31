# Review engine deployment readiness — 2026-10-27

Status: **preflight complete; waiting for explicit migration authorization**.
No development migration or policy installation has been performed. This receipt
records the checks executed for the Phase 4.1B/C deployment request. Follow
[the primary runbook](srs-0012-deployment.md) for subsequent commands.

## Confirmed development target

- Database: `chinese_learning`.
- Endpoint: `127.0.0.1:5432`; connected server address reports `127.0.0.1/32`.
- PostgreSQL role: `postgres`; application environment: development.
- Current revision: `0011_srs_foundation`; repository head: `0012_srs_review_engine`.
- Existing local-review publication opt-in remains unchanged.
- No backend listener on port 8000 and no other clients connected to this database
  during the preflight. The backend remains stopped for maintenance.

All development queries ran in read-only transactions. Exact canonical row counts
and hashes were recorded for all 34 preexisting public data tables; no row contents,
passwords or session credentials are included in this receipt.

| Check | Observed |
| --- | ---: |
| Catalog / published | 2,810 / 2,804 |
| Local-reviewed / held | 2,804 / 6 |
| Users / password credential records | 3 / 3 |
| Curated saved vocabulary | 1 |
| Saved state | mastery 0; LEARNING step 0; progress, generation and all review counters 0 |
| Personal vocabulary / retired wordbook / legacy SRS rows | 0 / 0 / 0 |
| Review attempts / legacy curated review history | 0 / 0 |
| Lesson runs / scene checkpoints | 1 / 2 |
| Installed grading policies | 0; 0012 policy table does not exist |

## Verified backup and exact-data rehearsal

Fresh archive:

`backend/.vocabulary-backups/review-deploy-20261027T164815Z/before-0012.dump`

- Size: **2,877,420 bytes**.
- SHA-256: `0b6fad1e921e9f2b9d3904f4bfd0aaa2f272df6a0efcc0a4fb5ff028eb2659a0`.
- `pg_restore --list`: passed.
- Complete archive decode: passed.
- Actual restore into new isolated database
  `chinese_review_deploy_restore_d642f5ba15`: passed.
- Restored 0011 data matched all 34 development table fingerprints.
- Exact `0011 → 0012` upgrade on that isolated restore: passed.
- All original table fingerprints after isolated migration: unchanged.
- Isolated `alembic check`: no new upgrade operations detected.
- Existing policy-validation command on migrated isolated restore: 2,148 validated,
  zero inserted, zero conflicts. No policies installed in this rehearsal.
- Final read-only development comparison: all 34 fingerprints unchanged, still 0011.

Private evidence is in the same ignored directory: `preflight.json`,
`preservation-before-0012.json`, `policy-preview-audit.json`, `backup.json`,
`backup-toc.txt`, `artifacts.json` and `rehearsal.json`. Keep the backup outside
version control; isolated fixtures are retained and were not reset or dropped.

The existing Phase 4.1C verification additionally reports **318 passed, seven
optional checks skipped**, including nonempty review-history preservation and
independent-connection concurrency checks. That full suite was not rerun for this
preflight. Current Ruff lint and format checks passed again (137 Python files).

## Bundle integrity and proposed effects

Bundle: `docs/datasets/srs-catalog-policies-v1.json`.

SHA-256: `1eda6b46b0c568c9bfaa891f83cc05be14e21d77cffaa1df5c7d33e97fce77b2`.

All 2,148 strict policy records match the current published UUID, content version
and checksum and the newly computed preparation result. There are zero duplicate
policy identities, zero existing policies and zero unexpected conflicts. The
proposed later installation would insert 2,148 policies: 2,145 automatically cued
policies plus three preserved manually reviewed examples. It would leave 656
published records unresolved and all six held records excluded. This is a
pre-migration preview; a **new** migrated-database preview and separate explicit
operator authorization are required before policy installation.

## Migration authorization scope

Migration 0012 adds:

1. `srs_review_attempts.submissions JSONB NOT NULL DEFAULT '[]'`.
2. `srs_target_policies`, keyed by vocabulary UUID, content version and checksum.
3. The append-only submissions guard function and trigger.

It does not change SRS scheduling rules or rewrite vocabulary, user data, progress
or historical attempts. Existing attempt rows, if any appear before deployment,
would receive only the new empty journal; the preflight must be refreshed if data
changes. Migration file SHA-256:
`c5c1924bfe23bcd39b0792b74da7c024e02d59660f915ab30fcf6bc564b8648b`.

After explicit migration authorization, recheck target identity, stopped API,
artifact hashes and preservation fingerprints, then run from `backend/`:

```powershell
.venv\Scripts\python -m alembic upgrade 0012_srs_review_engine
if ($LASTEXITCODE -ne 0) { throw 'Migration failed; keep API stopped' }
```

Then execute the runbook's current/schema/preservation checks using this receipt's
fresh fingerprint path. Produce the new policy-installation preview and request
separate authorization. Migration approval does not authorize policy installation.
No real learner grading attempts are authorized as deployment checks.
