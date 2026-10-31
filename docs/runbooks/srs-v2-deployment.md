# SRS v2 deployment approval gate

Historical preview, superseded by the user's explicit local deployment authorization
on 31 October 2026 and the [FSRS-only deployment report](srs-fsrs-only-deployment.md).
The authorized minimal backup and 0012→0014 migration are complete. The longer backup
restore rehearsal described below was not performed or required for this rollout.
The rollout flag has been removed; the old scheduling algorithm cannot be enabled.

Status: PREVIEW ONLY. No development migration, policy installation, learner
attempt, mastery update or schedule rewrite was authorized or performed.

## Read-only preflight

From backend, with the intended database supplied by the operator's protected
environment, run:

```powershell
.venv/Scripts/python -m scripts.srs_v2_preview --preflight ../docs/srs-v2-preflight.json
.venv/Scripts/python -m scripts.srs_v2_preview --policies ../docs/datasets/srs-v2-two-stage-policies.json
```

Both use REPEATABLE READ READ ONLY. The preflight is 0012-compatible, emits counts,
row fingerprints and pseudonymous per-word before/after projections; no credentials,
email addresses or answers from learner submissions are emitted. Projected Good/Again
dates are hypothetical next eligible completions, not proposed bulk UPDATEs.

Recorded baseline: revision 0012; 3 users; 27 curated saved words; 20 attempts;
2,804 installed policies. Refresh immediately before any authorized deployment.
The existing development API must not be restarted against this source before 0013.

## Required backup verification — separate approval still needed

Prepared command (not executed):

```powershell
.venv/Scripts/python -m scripts.srs_v2_backup_rehearsal
```

It exports a PostgreSQL snapshot under a read-only transaction, takes a custom-format
pg_dump into ignored `.vocabulary-backups/`, creates a fresh uniquely named isolated
restore database, restores with `--exit-on-error --no-owner --no-privileges`, and compares
every public table's canonical row count/hash against the same exported snapshot.
Credentials are passed through the child process environment, not command arguments.
PostgreSQL tools default to `C:/Program Files/PostgreSQL/18/bin`; override PG_BIN if needed.
It never restores over development, clears tables or drops a database. Keep the dump
private; it contains learner/application data. Back up immutable content storage and
retain the exact prior API/APK and environment configuration separately.

**Automatic approval review rejected executing this backup/restore rehearsal** because
the local export of development data and persistent restored copy require explicit
authorization. No verified backup report exists. The script is reviewable, but backup
restore verification remains a deployment blocker. Do not imply it passed.

## Exact 0013 changes and expected writes

* Add `curated_user_vocabulary.learning_activated`, non-null Boolean: existing rows
  logically receive true (27 at preflight); change the default for future inserts to false.
  PostgreSQL's constant default avoids a whole-table physical rewrite.
* Create empty `srs_memory`, `srs_daily_plans`, `srs_active_time`, their PK/FK/check
  constraints and owner/day index. No existing schedule/history/policy table is replaced.
* Advance the Alembic version row once. Expected existing due updates: 0; mastery
  updates: 0; attempts/submission changes: 0; policy inserts/updates: 0.
* No policy installation step: runtime projects the already validated immutable
  editorial policies and pins the resulting v2 policy into each new attempt.

DDL takes locks; schedule a maintenance interval after operator approval. First plan
creation writes one plan row only. Prefetch writes an attempt only. An eligible
completion updates one saved row, inserts/updates one memory row, finalizes one attempt
and records a unique completed identity in its plan; timing uses its separate receipts.

## Separate deployment checkpoint

Only after backup restoration is verified, all readiness checks pass, and the operator
explicitly approves the exact target database/revision and write counts:

1. Quiesce review traffic and stop API autoreload. Refresh the read-only preflight.
2. Capture and verify the final backup; compare the approved baseline and expected counts.
3. Operator-only command: `.venv/Scripts/python -m alembic upgrade 0013_srs_v2`.
4. Run `.venv/Scripts/python -m alembic check`, inspect old-column fingerprints,
   verify activation defaults and empty new tables. Any mismatch stops deployment.
5. Deploy matching backend dependencies, set `SRS_V2_ENABLED=true`, start the API,
   then distribute the matching APK. Keep old clients out of graded review: server
   ink validation intentionally rejects their text-only Hanzi requests.
6. Check liveness and read-only contracts. Any graded smoke test must use a separately
   authorized disposable synthetic account, never an existing learner account.
7. Verify real device ink, independent Pinyin, interruption/recovery, foreground timing
   and optional continuation before declaring rollout verified.

No command in this checkpoint has been run against development.

## Rollback

Before any v2 review: quiesce traffic and restore the previous API/APK/configuration;
retain 0013 tables and the pending-save distinction. Never downgrade or delete evidence.
After v2 reviews: stop writes first. Disable v2 as containment; the new code refuses
new v1 attempts on FSRS-adopted words. Existing pinned v2 finalization remains FSRS,
so stopping traffic is required for a complete freeze. Do not reset schedules to v1
or restore an old backup over newer learning history without a separately approved
data recovery plan. Prefer fixing forward. A restoration, if authorized, goes to a
fresh database first, verifies hashes, then uses an explicit controlled cutover.
