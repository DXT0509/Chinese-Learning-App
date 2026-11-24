# Phase 6.1 operator deployment and verification

Local development migration 0015 was explicitly authorized, applied and verified on
1 November 2026. See the [actual deployment report](roadmap-0015-deployment-20261101.md).
Roadmap content publication remains pending authorization. No real account, mastery,
schedule, review history or progress was modified by the deployment. The procedure below
records the preflight/deployment sequence; do not rerun its 0014 preflight on the upgraded DB.

## Preflight and authorized deployment

1. Obtain operator authorization specifically for `0015_roadmap_engine`. Stop learner,
   content-authoring and background writes for the preflight/verification window. Confirm
   that backend `.env` identifies the intended development database; do not print credentials.
2. From `backend/`, run the read-only preflight. It requires revision 0014, fingerprints
   every original column/row in all public tables, and refuses to replace an existing audit.
   Store the output outside Git. MD5 here is a data-drift fingerprint, not a security token.

   ```powershell
   .venv/Scripts/python -m alembic current
   .venv/Scripts/python -m scripts.roadmap_preflight --output .roadmap-preflight-0015.json
   ```

3. Take a PostgreSQL custom-format backup to an operator-controlled location outside the
   repository. Use existing PGHOST, PGPORT, PGUSER, PGDATABASE and a secured PGPASSFILE;
   do not put passwords in commands or source. Confirm those select the same target.

   ```powershell
   pg_dump --format=custom --file "$env:TEMP/chinese-before-roadmap-0015.dump"
   pg_restore --list "$env:TEMP/chinese-before-roadmap-0015.dump"
   ```

   Confirm exit codes, available disk space and a previously tested restore procedure.
   Never restore over development as part of a rehearsal.
4. Review `backend/alembic/versions/0015_roadmap_engine.py`: one nullable JSONB column,
   nine new tables/indexes/FKs and publication/audit guards. No DROP, learner UPDATE,
   backfill or catalog deletion. DDL takes normal PostgreSQL relation locks; keep writes
   quiesced and choose an appropriate maintenance window.
5. Only after authorization, apply the exact revision and verify before reopening writes:

   ```powershell
   .venv/Scripts/python -m alembic upgrade 0015_roadmap_engine
   .venv/Scripts/python -m alembic current
   .venv/Scripts/python -m alembic check
   .venv/Scripts/python -m scripts.roadmap_preflight --verify .roadmap-preflight-0015.json
   ```

   Verification uses the original column list, so the new nullable column does not cause
   a false difference. Any mismatch keeps writes closed for investigation. Restart the
   API only after successful verification; authenticated `/api/v1/roadmaps` should be empty
   before content publication. Existing health/auth/dictionary/SRS routes must still work.
6. Obtain separate content-publication authorization. Validate/import/preview drafts and
   inspect educational content/assets before explicit `publish --reviewed-by`. Publication
   atomically activates the release; never fabricate an external review attestation.

If deployment fails, investigate the transactional migration rather than resetting or
downgrading. Published versions and learner history have no automatic downgrade. An
application rollback can hide the new routes while leaving additive tables intact.
Content rollback uses explicit `activate` to an earlier published version; `depublish`
withdraws discovery. Neither action rewrites old runs, progress, rewards or FSRS state.

## Isolated verification

Run the existing venv from `backend/`:

```powershell
.venv/Scripts/python -m ruff check app scripts tests alembic
.venv/Scripts/python -m ruff format --check app scripts tests alembic
.venv/Scripts/python -m scripts.roadmap validate content/roadmaps/hsk-0.example.json
.venv/Scripts/python -m scripts.roadmap_isolated_checks
```

The isolated runner reads connection credentials without printing them, creates fresh
timestamped databases, and overrides child process DATABASE_URL. Only those newly created
databases receive migrations. It runs the full backend suite, existing FSRS regression
and concurrency tests, original nonempty 0001 upgrade, nonempty 0012 FSRS upgrade and
nonempty 0014 roadmap upgrade. Rehearsals refuse existing tables. Synthetic fixtures and
databases are retained; there is no reset, downgrade, volume deletion or automatic cleanup.

Final full isolated run on 1 November 2026: **419 passed, 9 skipped** in 96.65 seconds;
isolated Alembic check exited 0. Database suffix: `20261101062633`. This includes six
simultaneous completion requests, existing FSRS concurrency/regressions, authenticated
HTTP execution, repeated replay, raw evidence idempotency and catalog/memory preservation.
The 0014 upgrade rehearsal also exercised the read-only preflight and verified every
original table/column fingerprint afterward, including synthetic saved vocabulary and
an existing FSRS memory card. Original 0001 and FSRS 0012 nonempty rehearsals also passed.

After the final query projection/authoring bounds refinements, the selected roadmap
contracts, PostgreSQL progression/publication tests and authenticated API flow passed:
**15 passed, 1 concurrent test deselected** in 6.26 seconds. Concurrency was already
covered by the full run above. Source-scoped Ruff checks/formatting, compilation and
draft JSON validation passed. No Android build/device checks were run because Android
source was unchanged.

Fresh databases from verification are intentionally retained for inspection. In the
final run they are `chinese_roadmap_{kind}_20261101062633`, where kind is test, upgrade,
concurrent, creation, srs, v2, roadmap_upgrade or legacy_upgrade. Earlier isolated runs
used suffixes `20261101061909` and `20261101062256`; none targeted development.
The skipped tests require separate dedicated historical migration URLs; skips do not count
as verification of those older independent rehearsals. The original, FSRS and roadmap
rehearsals listed above ran explicitly. Known warnings are existing Starlette/httpx
deprecation and SQLAlchemy reflection warnings.

Repository-wide Ruff discovery encounters the pre-existing inaccessible deleted
`backend/.test-new-saves-full` directory. Checks explicitly scoped to source/test/migration
directories avoid that unrelated filesystem problem. No dependency versions were changed.
