# Phase 4 vocabulary reset plan

Status: implementation prepared; the development reset has NOT been executed. Revision
`0008_curated_vocabulary` follows `0007_personal_vocabulary`. All historical revisions,
including the existing uncommitted 0007 work, remain unchanged. The migration only adds
tables and a collection integrity trigger. It never clears data.

Read [schema/API](curated-vocabulary-schema.md) and [import workflow](curated-vocabulary-import.md).
Earlier dictionary/enrichment/wordbook guides describe historical behavior; this guide
supersedes their active API and import instructions.

## Verified local development inventory

A read-only connection and a real backup/dry-run verified database `chinese_learning`,
host `127.0.0.1`, port `5432`, environment `development`, revision
`0007_personal_vocabulary`. The October 23, 2026 local-time observation was:

| Clear, child first | Rows | Dependency / effect |
| --- | ---: | --- |
| personal_vocabulary_entries | 1 | users; dictionary_entries; saved snapshots removed |
| srs_states | 0 | user_vocabulary; old review schedules removed |
| user_vocabulary | 0 | users; legacy vocabulary/custom entries removed |
| lesson_vocabulary | 1 | lessons, lesson_versions, vocabulary; curriculum targets detached |
| vocabulary_characters | 1 | vocabulary, characters; character associations removed |
| vocabulary | 1 | assets; old authored lexical content removed |
| dictionary_character_enrichments | 659 | dictionary_enrichment_imports; Vietnamese character notes removed |
| dictionary_enrichment_imports | 1 | old enrichment source metadata removed |
| dictionary_entries | 125303 | dictionary_imports; CC-CEDICT entries removed |
| dictionary_imports | 1 | old dictionary provenance removed |

| Preserved table | Rows |
| --- | ---: |
| users | 3 |
| password_credentials | 3 |
| auth_sessions | 12 |
| refresh_credentials | 22 |
| lessons | 1 |
| lesson_versions | 1 |
| lesson_templates | 1 |
| lesson_template_versions | 1 |
| lesson_template_scenes | 2 |
| lesson_runs | 1 |
| lesson_scene_progress | 2 |
| user_lesson_progress | 0 |
| characters | 1 |
| assets | 1 |
| alembic_version | 1 |

No roles/permissions tables exist in the inspected schema. Any additional unrelated
public tables are preserved, with row counts and content fingerprints checked.
The curated catalog and its unified user state are also preserved if already present.

The actual report is `backend/.vocabulary-reset-before-migration.json`; full foreign-key
constraint names, columns, delete actions and trigger definitions appear there.
This report is intentionally ignored by Git. It is an observation, not permission to
execute a reset after the database changes.

Backup: `backend/.vocabulary-backups/vocabulary-before-reset-20261022T182248978401Z.dump`
(UTC filename), **8,476,376 bytes**, SHA-256
`109637c8a468681b7b69b6cd3716ad5958d9acc637aea273def7285ae5762a29`.
The command checked successful `pg_dump` exit, file existence, size and checksum.
Keep backups private: a full database backup contains password hashes and session digests.

## Exact lesson consequences to review before deletion

One link belongs to a PUBLISHED lesson version. Ordinary DELETE is blocked by the
`lesson_vocabulary_immutable` trigger introduced in 0002. Only the explicitly confirmed
maintenance transaction temporarily disables this named trigger, deletes obsolete
vocabulary links, and restores it before commit. An error rolls back data and trigger DDL.
This requires table-owner permission; failure stops the operation.

Published lesson/version rows, templates, bundle bytes and media assets are preserved.
The current bundle is a self-contained CONTENT_PREVIEW snapshot, so the player still
loads its pinned vocabulary content. Its old vocabulary UUID becomes historical and
returns 404 from the new dictionary API. A published version no longer has relational
vocabulary targets and cannot be treated as a new executable curated lesson. Existing
lesson runs/bookmarks and completion records stay unchanged; no completion/mastery is
inferred. Republish future curriculum through a separately designed curated lesson
contract; never reimport the old content library to repopulate the retired catalog.

The legacy `characters` table and stroke/media keys are retained as unrelated learning
infrastructure. Only old vocabulary-character mappings and dictionary enrichment are
removed. No asset files are deleted. There is no broad TRUNCATE or CASCADE reset.

## Operator procedure (PowerShell, from backend)

Stop the API to avoid normal account/session writes invalidating the report. Install the
updated lock into the development virtual environment, then apply the additive schema:

```powershell
.venv\Scripts\python -m pip install -r requirements-dev.lock
.venv\Scripts\python -m alembic upgrade head
.venv\Scripts\python -m alembic check
```

The existing pre-migration report becomes stale when the schema changes. Create a NEW
report and backup using the exact identity you have verified. Choose a new filename
for every dry run; report files are never overwritten:

```powershell
.venv\Scripts\python -m scripts.reset_vocabulary dry-run --database chinese_learning --host 127.0.0.1 --port 5432 --report .vocabulary-reset-after-0008.json --backup-dir .vocabulary-backups --pg-dump 'C:\Program Files\PostgreSQL\18\bin\pg_dump.exe'
Get-Content .vocabulary-reset-after-0008.json
```

Review ALL `clear`, `preserve`, `foreign_keys`, `triggers`, published-link consequences,
database identity and backup details. Verify the backup independently if desired:

```powershell
$resetReview = Get-Content .vocabulary-reset-after-0008.json -Raw | ConvertFrom-Json
Get-Item -LiteralPath $resetReview.backup.path | Select-Object FullName,Length
Get-FileHash -LiteralPath $resetReview.backup.path -Algorithm SHA256
& 'C:\Program Files\PostgreSQL\18\bin\pg_restore.exe' --list $resetReview.backup.path
```

Only the product owner should run this SECOND command after reviewing the report.
Replace the placeholder manually with that report's full `confirmation` value:

```powershell
.venv\Scripts\python -m scripts.reset_vocabulary apply --database chinese_learning --host 127.0.0.1 --port 5432 --report .vocabulary-reset-after-0008.json --confirm '<confirmation-from-reviewed-report>'
```

No apply command was run against development during this implementation. There is no
startup/test/import/migration hook invoking it. Remote hosts, production configuration,
mismatched identity, expired reports (>24 hours), changed inventories, unknown inbound
foreign keys and missing/modified backups stop it. All inspected public tables are
locked during each snapshot; apply checks preserved row contents as well as counts.
Database restart or ordinary writes require a fresh dry run. A stale report after a
successful reset is refused; a new empty dry run makes a subsequent apply a no-op.

## Restore and rollback

There is no destructive downgrade. A full pg_dump restore must target a NEW empty,
explicitly named database. Do not use `--clean` against development. Example, with
PGHOST/PGPORT/PGUSER set to your verified server and credentials supplied securely:

```powershell
& 'C:\Program Files\PostgreSQL\18\bin\createdb.exe' chinese_learning_restore_review
& 'C:\Program Files\PostgreSQL\18\bin\pg_restore.exe' --exit-on-error --dbname=chinese_learning_restore_review $resetReview.backup.path
```

Inspect restored accounts, credential/session counts, vocabulary, curriculum and app
connectivity before changing DATABASE_URL. Restore the matching application version;
a pre-0008 backup needs an additive upgrade before the new API can run. Content/media
storage is external to pg_dump: preserve its directory separately. Reconnecting to an
old backup intentionally rolls back database writes made since that backup.

## Isolated verification

Tests require explicit isolated URLs. Regular PostgreSQL tests use TEST_DATABASE_URL on
an already migrated database and roll back fixture writes. These dedicated rehearsals
require separate fresh EMPTY databases and refuse existing tables:

- CURATED_MIGRATION_TEST_DATABASE_URL: nonempty 0007 -> head, preserves every old value;
  leaves fixtures intact, with no reset or downgrade.
- VOCABULARY_RESET_TEST_DATABASE_URL: synthetic fixtures, real backup, confirmed deletion,
  trigger restoration and repeat-safety checks. This database is intentionally reset.
- VOCABULARY_RESTORE_TEST_DATABASE_URL: fresh empty destination for real pg_restore.
- TEST_PG_DUMP: absolute pg_dump path if it is not on PATH.

Historical MIGRATION_TEST_DATABASE_URL, DICTIONARY_MIGRATION_TEST_DATABASE_URL,
ENRICHMENT_MIGRATION_TEST_DATABASE_URL and WORDBOOK_MIGRATION_TEST_DATABASE_URL likewise
need their own fresh empty databases. Never point any of these variables at development.

Run `.venv\Scripts\python -m pytest -q`, `ruff check .`, `ruff format --check .`,
`pip check` and `alembic check` on the isolated database. Backend rehearsal artifacts are
ignored under `.vocabulary-backups`; no database files or backups belong in commits.

## Remaining migration risks

Legacy tables are deprecated and emptied, not dropped. Keeping their DDL preserves
historical Alembic reproducibility and published preview infrastructure. Legacy provider
services/tests remain for historical rehearsal; HTTP routes never call them. Provider
import CLIs permit validation only; confirmed revision repair is disabled. Removal of
legacy DDL and content-authoring vocabulary contracts needs a future reviewed migration.

The release must coordinate backend and Android updates: old clients expect removed
provider/traditional fields. Search is deliberately empty until human-approved curated
records exist. OpenCC catches known Traditional variants; it is not a substitute for
human linguistic review. Current linear search is suitable for the requested ~2,500
words; it is not intended as a replacement for a general-purpose dictionary.
