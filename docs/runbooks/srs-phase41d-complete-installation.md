# Phase 4.1D complete candidate — operator procedure

Deployment status, 2026-10-29: this exact bundle has now been explicitly authorized,
installed and verified. See the [deployment receipt](srs-phase41d-deployment-20261029.md).
The original procedure and authorization requirements remain below for provenance
and any future separately scoped maintenance; do not infer approval for new writes.

Candidate: [srs-phase41d-complete-v2.json](../datasets/srs-phase41d-complete-v2.json).
SHA-256: `abae251396a78ffc12cfa535374751954f4cde060a330bbb8491e89e428e81e2`.
Verified read-only target: `chinese_learning`, `127.0.0.1:5432`, role `postgres`,
revision `0012_srs_review_engine`. Current effects: **656 INSERT, zero UPDATE,
2,148 unchanged**. Expected resulting coverage: **2,804 / 2,804**. No development
installation or authorization is recorded by this procedure.

Read the [completion report](../srs-phase41d-completion.md),
[242 linguistic findings](../srs-phase41d-linguistic-review-v2.json) and
[verification receipt](../srs-phase41d-complete-verification-v2.json).

## Reproduce and validate without writes

From `backend/`, use **new output paths**; existing files are refused:

```powershell
.venv\Scripts\python -m scripts.prepare_remaining_policies --checkpoint ..\docs\datasets\srs-phase41d-editorial-checkpoint.json --previous ..\docs\datasets\srs-phase41d-policies.json --remaining-output .vocabulary-backups\remaining-next.json --final-output .vocabulary-backups\complete-next.json --audit .vocabulary-backups\grammar-review-next.json
if ($LASTEXITCODE -ne 0) { throw 'Stop: recorded-review preparation failed' }
Get-FileHash .vocabulary-backups\complete-next.json -Algorithm SHA256
.venv\Scripts\python -m scripts.review_policies --file ..\docs\datasets\srs-phase41d-complete-v2.json
if ($LASTEXITCODE -ne 0) { throw 'Stop: current database validation failed' }
```

Preparation is offline and deterministic, serializing recorded individual
decisions rather than approving arbitrary input. Expected hash is above.
Validation enforces repeatable-read/read-only, checks live publication and
bindings, original POS/examples, generated policies and immutable existing payloads.
Expected: 2,804 validated, 2,148 unchanged, would_insert 656, would_update zero,
inserted zero. Any conflict or changed binding/count requires a renewed audit.

For a detailed live audit with the existing preparer:

```powershell
.venv\Scripts\python -m scripts.prepare_review_policies --complete-coverage --dry-run --preserve-file ..\docs\datasets\srs-phase41d-complete-v2.json --audit .vocabulary-backups\live-coverage-next.json
if ($LASTEXITCODE -ne 0) { throw 'Stop: live coverage audit failed' }
```

Inspect `database_target`, revision, full denominator and zero unresolved.
This preparer orders policies lexically; the final serializer orders by UUID.
Compare objects by identity, not array-order hashes. The approved installation
input remains the exact candidate file/hash.

## Release compatibility, backup and approval

1. Stop the API for maintenance and prevent concurrent content publication.
   Verify database identity directly, not from an environment filename.
2. Prepare the updated backend and Android together. The backend must understand
   contextual-grammar policy evidence; Android must label the new choices. Old
   policies keep their existing codes, but old clients do not label new choices.
   No schema migration is needed. Do not install against the old implementation.
3. Create a fresh custom-format `pg_dump` using existing secure credentials.
   Record size/hash, verify `pg_restore --list`, and restore fully to a newly named
   isolated database. Never restore over development. Rehearse installation and
   idempotent reimport there; run `alembic check` there.
4. The preparation backup remains privately at
   `backend/.vocabulary-backups/phase41d-final-0dfe58e5bd/source.dump`, 3,115,721 bytes,
   SHA-256 `0e969f05142ec8341a18c832c38aefec3013f70eac6e3c994bac1fd0ed41243b`.
   Listing, complete restore and every non-policy table fingerprint were verified.
   Refresh backup/evidence if development changes before execution; a past receipt
   does not prove the current state.
5. Fingerprint full UTC `to_jsonb(row)` canonical row counts/hashes for every
   non-policy table, including attempt submission journals. Preserve exact original
   policy JSON as well. Keep dump, row contents and credentials in ignored private
   evidence. No real graded review is part of testing.
6. Present the exact target, candidate hash, renewed read-only preview, effects,
   verified backup/restore and preservation plan. **Request explicit operator
   authorization before the development-writing command below.** Implementation,
   earlier migration approval and isolated tests are not installation approval.

The authorization request must name this exact bundle and target, 656 inserts,
zero updates, all 2,148 existing policies and personal/catalog data preserved,
the verified fresh backup hash and stopped-API maintenance plan. Silence or
elapsed time is not approval.

## Only after authorization

```powershell
.venv\Scripts\python -m scripts.review_policies --file ..\docs\datasets\srs-phase41d-complete-v2.json --install
if ($LASTEXITCODE -ne 0) { throw 'Stop: installation failed; inspect before retrying' }
```

The importer inserts missing policies in one transaction, locks catalog, meanings,
examples and publication evidence, serializes importers and rejects immutable-row
conflicts. Failures roll back the batch. No migration, vocabulary publication,
account, collection, mastery, schedule, attempt or review-result write is included.

## Post-deployment verification

1. Keep the API stopped until all non-policy fingerprints match. Verify all
   original policy payloads are identical, precisely 656 rows were added, no
   duplicates/stale bindings exist and the complete published denominator remains.
2. Validate again without `--install`: expect 2,804 unchanged and zero proposed
   inserts/updates. Compare fingerprints again.
3. Resolve every published identity read-only through `ReviewedTargets`. Expect
   2,804 gradable, every level at 100%, and all six unpublished holds preserved.
4. Restart the updated API. Check health, OpenAPI and unauthenticated 401s using
   GET only; use an existing authorized session for read-only dashboard/queue checks.
   Do not create real graded attempts as a deployment test.
5. Against isolated synthetic learners, verify stage secrecy, strict tones,
   ordinary POS single/multi-select, marked syntax, expression/morpheme alternatives,
   first-answer/assistance FAIL, replay, handwriting and unchanged SRS transitions.
   Device checks must be recorded separately from unit/build/lint checks.
6. Save a deployment receipt with actual target, hashes, effects and preservation
   fingerprints. Only then describe development as deployed.
