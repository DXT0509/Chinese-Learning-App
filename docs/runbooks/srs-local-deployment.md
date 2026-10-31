# Local SRS 0011 deployment (operator action only)

Development was explicitly authorized and upgraded to `0011_srs_foundation`.
See the [2026-10-26 deployment results](srs-0011-deployment-20261026.md) for the backup,
preservation/schema verification and API restart. The
[readiness report](srs-0011-readiness-20261026.md) and instructions below record the
original pre-deployment proposal; do not treat their 0010 baseline as current state.

The following commands were originally prepared for operator review. Deployment was
subsequently executed with explicit authorization as recorded above. Any future
database change still requires its applicable authorization and a fresh baseline.

## Reviewable deployment target

| Item | Observed / proposed |
| --- | --- |
| Database | `chinese_learning`, `127.0.0.1:5432`, role `postgres` |
| Current revision | `0010_local_codex_review` |
| New revision | `0011_srs_foundation` |
| Catalog | 2,810 entries; 2,804 LOCAL_CODEX_REVIEWED; six NEEDS_REVIEW holds |
| Backfill | One curated saved row, mastery 0, null due → existing save time |
| Preservation | Three users, one lesson run, same saved UUID/mastery/save/last-review times; all catalog and legacy tables retained |
| Schema | Extend curated saved progress with phase/step/promotion/generation/counters/legacy snapshot, require due time; one attempt table, checks/index/history trigger |

The complete state machine, API contracts and unresolved sense/POS policies are in
[the foundation document](../srs-foundation.md). Test evidence is in
[verification](../srs-verification.md). The table above is an audit snapshot: re-audit
immediately before authorization if the database has changed.

## Before requesting operator authorization

Review the additive migration and the audit. From the repository's `backend/`
directory, use the existing local `.env` and do not print its credentials:

```powershell
.venv\Scripts\python -m alembic current
.venv\Scripts\python -m alembic heads
.venv\Scripts\python -m scripts.audit_srs --output ..\docs\srs-data-audit.json
git diff -- alembic/versions
git status --short
```

0011 is a new untracked file until committed; review its complete contents as well
as the diff. No 0001–0010 migration may change. If the identity, current revision,
counts or holds differ, update this deployment proposal before seeking authorization.

The exact backup command below uses the inspected native PostgreSQL 18 installation.
It prompts for the password rather than placing it on the command line. The backup
directory is already ignored by Git. Use a fresh backup name on subsequent dates.

```powershell
New-Item -ItemType Directory -Force .vocabulary-backups | Out-Null
if (Test-Path -LiteralPath '.vocabulary-backups\srs-before-0011-20261026.dump') {
    throw 'Choose a fresh backup filename; do not overwrite an existing backup.'
}
& 'C:\Program Files\PostgreSQL\18\bin\pg_dump.exe' -h 127.0.0.1 -p 5432 -U postgres -W -d chinese_learning -Fc --file='.vocabulary-backups\srs-before-0011-20261026.dump'
if ($LASTEXITCODE -ne 0) { throw 'Backup failed' }
& 'C:\Program Files\PostgreSQL\18\bin\pg_restore.exe' --list '.vocabulary-backups\srs-before-0011-20261026.dump'
if ($LASTEXITCODE -ne 0) { throw 'Backup archive is unreadable' }
```

Archive listing checks readability; it is not a restore rehearsal. Follow local
backup policy to restore into a separately provisioned empty database and verify it
before deployment. Never restore over development as a test.

## After explicit operator authorization

Stop the API to prevent saves/reviews during the snapshot/backfill. Confirm that
`DATABASE_URL`, if set, identifies the approved database; otherwise Alembic reads
the existing `.env`. The exact migration command, from `backend/`, is:

```powershell
.venv\Scripts\python -m alembic upgrade 0011_srs_foundation
if ($LASTEXITCODE -ne 0) { throw 'Migration failed; keep API stopped and inspect safely' }
.venv\Scripts\python -m alembic current
.venv\Scripts\python -m alembic check
.venv\Scripts\python -m scripts.audit_srs --output .vocabulary-backups\srs-after-0011.json
```

Expected: revision 0011, no metadata drift, identical catalog/status/hold/user/run
counts, one curated saved row still at mastery 0, zero null due timestamps. Its
legacy JSON snapshot must contain the original null due time. Every preexisting
non-null due/last-review timestamp must match its snapshot as an instant in UTC.
An operator can verify the backfill with this read-only query (run before API restart):

```sql
SELECT count(*) AS backfilled,
       count(*) FILTER (WHERE
           mastery_level <> (legacy_srs_snapshot->>'mastery_level')::integer OR
           last_reviewed_at IS DISTINCT FROM
               (legacy_srs_snapshot->>'last_reviewed_at')::timestamptz OR
           next_review_at IS DISTINCT FROM COALESCE(
               (legacy_srs_snapshot->>'next_review_at')::timestamptz, saved_at)
       ) AS preservation_errors
FROM curated_user_vocabulary
WHERE legacy_srs_snapshot IS NOT NULL;
```

Expected for the audited database: `backfilled=1`, `preservation_errors=0`.
Restart the API only after all checks pass. Authenticate through the existing
email/password flow and inspect `/api/v1/me/srs/dashboard`, `/due`, owned progress
and `/sessions`. Grading must remain unavailable. The new contract intentionally
does not enable the Android Review screen or award mastery from a client result.

There is no downgrade/reset recovery command. A failed PostgreSQL migration should
roll back transactionally; inspect revision and schema before retrying. Any recovery
that replaces data requires a separate operator-reviewed plan and verified backup.

## Reproducing isolated verification

Provision fresh databases with operator-selected credentials; never point these
variables at `chinese_learning`. The regular and concurrency databases must be
migrated. The SRS/legacy rehearsal databases must be empty and are populated by the
tests themselves. Each nonempty rehearsal refuses existing tables and retains its
fixtures; choose new database names for every repeat.

```powershell
foreach ($variableName in @('TEST_DATABASE_URL', 'SRS_CONCURRENCY_TEST_DATABASE_URL',
                           'SRS_MIGRATION_TEST_DATABASE_URL', 'MIGRATION_TEST_DATABASE_URL')) {
    if ([string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable($variableName))) {
        throw "Set $variableName to an explicitly provisioned isolated database first."
    }
}
$env:DATABASE_URL = $env:TEST_DATABASE_URL
# TEST_DATABASE_URL: isolated regular test DB; set explicitly before this command.
.venv\Scripts\python -m alembic upgrade 0011_srs_foundation
$env:DATABASE_URL = $env:SRS_CONCURRENCY_TEST_DATABASE_URL
.venv\Scripts\python -m alembic upgrade 0011_srs_foundation
$env:DATABASE_URL = $env:TEST_DATABASE_URL
$env:ALLOW_AI_APPROVED_VOCABULARY = 'false'
$env:ALLOW_LOCAL_CODEX_REVIEWED_VOCABULARY = 'false'
# SRS_MIGRATION_TEST_DATABASE_URL: fresh empty database for 0010 -> 0011.
# MIGRATION_TEST_DATABASE_URL: another fresh empty database for legacy -> head.
.venv\Scripts\python -m ruff check .
.venv\Scripts\python -m ruff format --check .
.venv\Scripts\python -m pytest -q
.venv\Scripts\python -m alembic check
```

Restore/remove these process environment overrides afterward. Test fixtures explicitly
enable publication options when testing their corresponding local/AI policies.
