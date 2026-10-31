# 0012 review-engine deployment procedure

Prepared on 2026-10-27 (Asia/Bangkok). **Migration 0012 was applied on 2026-10-28
after explicit authorization; the 2,148-policy bundle was then installed after
separate explicit approval.** See the [final deployment receipt](srs-policy-deployment-20261028.md).
See also the [migration execution receipt](srs-0012-deployment-20261028.md) and
[fresh installation preview](../srs-0012-policy-installation-preview-20261028.json).
The original read-only [predeployment audit](../srs-review-data-audit.json) observed revision
0011, 2,810 words, 2,804 visible local reviews, six held entries, three users, one
curated saved word at mastery zero and one lesson run. No real learner attempts were
submitted. Recheck the target immediately before deployment; the audit is a snapshot.

Review [the engine and Android contract](../srs-review-engine.md), additive migration
`backend/alembic/versions/0012_srs_review_engine.py`, verification report and the
reviewed policy file before deployment. Obtain explicit authorization to apply 0012
to the development database. Implementation authorization did not authorize this
migration. Do not use a generic `upgrade head` against development.

All commands below run from `backend/`. Existing `.env` supplies credentials;
confirm any process `DATABASE_URL` override points to the approved database without
printing credentials. Stop the API before fingerprints and keep it stopped through
post-migration checks, so authentication/session writes cannot race preservation
comparison. Do not reset, downgrade or delete volumes.

After explicit deployment authorization, create a fresh backup:

```powershell
.venv\Scripts\python -m alembic current
if ($LASTEXITCODE -ne 0) { throw 'Revision check failed' }
# Require 0011_srs_foundation before proceeding.
New-Item -ItemType Directory -Force .vocabulary-backups | Out-Null
if (Test-Path -LiteralPath '.vocabulary-backups\srs-before-0012-20261027.dump') {
    throw 'Choose a fresh backup filename; never overwrite an existing backup'
}
& 'C:\Program Files\PostgreSQL\18\bin\pg_dump.exe' -h 127.0.0.1 -p 5432 -U postgres -W -d chinese_learning -Fc --file='.vocabulary-backups\srs-before-0012-20261027.dump'
if ($LASTEXITCODE -ne 0) { throw 'Backup failed' }
& 'C:\Program Files\PostgreSQL\18\bin\pg_restore.exe' --list '.vocabulary-backups\srs-before-0012-20261027.dump'
if ($LASTEXITCODE -ne 0) { throw 'Backup archive unreadable' }
.venv\Scripts\python -m scripts.review_preservation --snapshot .vocabulary-backups\srs-before-0012-20261027.json
if ($LASTEXITCODE -ne 0) { throw 'Preservation fingerprint failed' }
```

The fingerprint snapshots counts and SHA-256 hashes of canonical JSON rows from
every public base table except Alembic bookkeeping and the new policy table. It
normalizes database timestamp rendering to UTC, omits only the added `submissions`
field from attempts, and exposes no row payloads or session secrets. Snapshot files
refuse overwrite. The backup contains data and must remain outside version control.
Archive listing checks readability; a restore rehearsal into a separate empty
database is required under the operator's backup policy, never over development.

Apply exactly 0012 and verify before restarting:

```powershell
.venv\Scripts\python -m alembic upgrade 0012_srs_review_engine
if ($LASTEXITCODE -ne 0) { throw 'Migration failed; keep API stopped' }
.venv\Scripts\python -m alembic current
if ($LASTEXITCODE -ne 0) { throw 'Revision check failed' }
.venv\Scripts\python -m alembic check
if ($LASTEXITCODE -ne 0) { throw 'Schema drift; keep API stopped' }
.venv\Scripts\python -m scripts.review_preservation --verify .vocabulary-backups\srs-before-0012-20261027.json
if ($LASTEXITCODE -ne 0) { throw 'Preservation mismatch; keep API stopped' }
.venv\Scripts\python -m scripts.audit_srs --output .vocabulary-backups\srs-after-0012-20261027.json
if ($LASTEXITCODE -ne 0) { throw 'Audit failed; keep API stopped' }
.venv\Scripts\python -m scripts.review_policies > .vocabulary-backups\srs-policy-exclusions-20261027.json
if ($LASTEXITCODE -ne 0) { throw 'Exclusion report failed' }
```

Expected: revision 0012, no metadata drift, identical preexisting row fingerprints,
unchanged catalog/status/hold/user/progress counts and no new graded results. All
existing attempts have an empty journal. The new policy table starts empty; graded
targets remain unavailable until reviewed policies are installed.

Validate an actual reviewed policy array before installing it, with an operator-
selected path. Installation is a distinct explicit command and writes policies only:

```powershell
.venv\Scripts\python -m scripts.review_policies --file .vocabulary-backups\reviewed-srs-policies.json
if ($LASTEXITCODE -ne 0) { throw 'Policy validation failed' }
.venv\Scripts\python -m scripts.review_policies --file .vocabulary-backups\reviewed-srs-policies.json --install
if ($LASTEXITCODE -ne 0) { throw 'Policy installation failed' }
```

The prepared repository bundle is `..\docs\datasets\srs-review-policies-v1.json`.
After reviewing its prompts and reviewer attribution, substitute that exact path in
both policy commands to install the initial three catalog-bound questions. Its
checksums must still match at deployment; stale bundles are rejected. No policy
installation was performed during implementation.

Restart the existing API process only after verification. Smoke-test `/health`,
dictionary reads and authenticated dashboard/target/question reads using an
explicitly designated test account. Do not submit graded attempts for existing
learners. Foundation sessions started without a grading policy must be restarted
after policies are installed; their pinned targets are immutable. Android integration
is a future phase; existing Android UI remains unchanged.

## Phase 4.1C bulk policy installation

The [catalog preparation report](../srs-policy-preparation.md) and detailed
[audit](../srs-policy-coverage-audit.json) propose 2,145 automatically cued questions
plus the three preserved manual policies. Review and authorize this exact bundle
separately from the migration. Automatic policies require the full Hán-Việt cue
in their question; this is not approval of unrestricted translation grading.

Before stopping the API, prepare a fresh read-only candidate as documented in the
report and compare its coverage and SHA-256 with the approved artifact. If the
catalog, publication configuration or preserved policies changed, review a fresh
bundle; never patch a stale checksum. Keep the API and catalog authoring stopped
through migration and installation so the preservation comparison is meaningful.

Perform the backup, exact 0012 upgrade, `alembic check` and preservation verification
above first. For bulk installation, replace the three-policy example command with:

```powershell
# Validate only; this writes no policies.
.venv\Scripts\python -m scripts.review_policies --file ..\docs\datasets\srs-catalog-policies-v1.json
if ($LASTEXITCODE -ne 0) { throw 'Bulk validation failed; keep API stopped' }
# Execute only after explicit operator authorization of this bundle.
.venv\Scripts\python -m scripts.review_policies --file ..\docs\datasets\srs-catalog-policies-v1.json --install
if ($LASTEXITCODE -ne 0) { throw 'Bulk installation failed; keep API stopped' }
# A second validation must report unchanged rows (or preserved manual policies).
.venv\Scripts\python -m scripts.review_policies --file ..\docs\datasets\srs-catalog-policies-v1.json
if ($LASTEXITCODE -ne 0) { throw 'Post-install validation failed' }
.venv\Scripts\python -m scripts.review_preservation --verify .vocabulary-backups\srs-before-0012-20261027.json
if ($LASTEXITCODE -ne 0) { throw 'Learner/content preservation mismatch' }
.venv\Scripts\python -m scripts.prepare_review_policies --dry-run --audit .vocabulary-backups\catalog-policy-postinstall.json
if ($LASTEXITCODE -ne 0) { throw 'Post-install coverage audit failed' }
```

On an unchanged empty policy table, expect 2,148 inserted; a repeated authorized
installation inserts zero. Existing manual policies are preserved and can reduce
the insertion count. Verify the audit reports expected current coverage and six
publication exclusions. Fingerprints omit the policy table deliberately; all
preexisting content and learner rows must still match. Record the bundle hash,
validated/inserted/unchanged/preserved counts and audit with the operator receipt.
Then restart and run the read-only authenticated smoke checks above. No real
learner answers, mastery resets or review-history changes are deployment checks.

If anything fails, retain backup, fingerprints and fixtures, keep the API stopped,
and inspect the failure. Downgrade intentionally refuses history deletion. Any
restore or forward repair requires separate operator review and authorization.
