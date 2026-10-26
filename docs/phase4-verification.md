# Phase 4 implementation and verification report

Prepared October 23, 2026 (Asia/Bangkok). The real development database was inspected
read-only and backed up. It was NOT migrated or reset. The product owner must perform
the separate reviewed reset described in [the operator plan](vocabulary-reset-plan.md).

## Implementation files

New backend implementation:

- alembic/versions/0008_curated_vocabulary.py
- app/core/pinyin.py
- app/models/curated_vocabulary.py
- app/schemas/curated_api.py and app/schemas/curated_vocabulary.py
- app/services/curated_catalog.py, app/services/curated_import.py,
  app/services/vocabulary_reset.py
- scripts/curated_vocabulary.py and scripts/reset_vocabulary.py
- tests/test_curated_vocabulary.py, tests/test_vocabulary_reset.py,
  tests/test_vocabulary_reset_safety.py and tests/fixtures/curated/synthetic.jsonl

Backend integration changes:

- app/models/__init__.py registers the additive models.
- app/api/v1/endpoints/dictionary.py and the preexisting personal_vocabulary.py now
  use CuratedCatalog and the curated wire contracts.
- pyproject.toml and requirements-dev.lock add the pinned OpenCC validation dependency.
- scripts/import_dictionary.py and import_dictionary_enrichment.py retire database
  imports while preserving offline historical validation. repair_dictionary_revision.py
  refuses confirmed changes to the retired provider.
- Historical dictionary/enrichment HTTP tests now assert legacy rows are excluded from
  curated responses; direct legacy-service and migration tests remain. The preexisting
  personal-vocabulary tests retain the legacy concurrency test, with new API behavior
  covered in test_curated_vocabulary.py.

Android changes under app/src/main/java/com/example/chineselearningapp:

- core/network/DictionaryApi.kt and PersonalVocabularyApi.kt consume curated responses.
- domain/model/Dictionary.kt and domain/repository/PersonalVocabularyRepository.kt remove
  Traditional Chinese and provider-only state.
- feature/dictionary/data/RemoteDictionaryRepository.kt,
  feature/vocabulary/data/RemotePersonalVocabularyRepository.kt map the new contracts.
- feature/dictionary/DictionaryScreens.kt and feature/vocabulary/MyVocabularyScreen.kt
  remove retired script/enrichment/source sections; curated_strings.xml adds Vietnamese text.
- DictionaryRepositoryTest, DictionaryViewModelTest and the preexisting personal-vocabulary
  tests use the updated models. DictionaryUiTest, HandwritingUiTest and the preexisting
  PersonalVocabularyUiTest compile with curated models.

Documentation: vocabulary-reset-plan.md, curated-vocabulary-schema.md,
curated-vocabulary-import.md, this report and the Phase 4 pointer in development-guide.md.
.gitignore excludes backup/report/test-cluster artifacts. Existing unrelated navigation,
authentication, app wiring and documentation edits in the workspace were retained.
No credentials, generated builds or database files are included in source changes.

## Schema, reset and API result

Migration head: **0008_curated_vocabulary**, parent **0007_personal_vocabulary**. No
historical migration changed. Seven tables are added: batches, catalog, meanings,
examples, revisions, unified collection and reserved review submissions. The
[schema/API guide](curated-vocabulary-schema.md) contains their keys, constraints,
ownership rules and complete endpoint contracts.

Ten old tables are deprecated/cleared by the dedicated reset, with no table drops.
The [reset plan](vocabulary-reset-plan.md) records the real per-table dry-run counts,
published-link consequences, preserved authentication/infrastructure, full backup path,
checksum, explicit second-step command and restore procedure. The development report is
ignored at backend/.vocabulary-reset-before-migration.json. Generate a NEW report after
0008; applying that structural migration invalidates the pre-migration approval artifact.

The importer supports strict UTF-8/NFC JSONL, pronunciation-specific UUID identities,
versioned revisions, source batches, content checksums and idempotency. Import cannot
approve AI content. Explicit checksum-bound human approval is separate. Search/detail/save
require approved Vietnamese content. Collection saves/reactivations preserve mastery;
new associations require mastery zero at the database boundary. Old provider IDs return
404 rather than mapping to new words. Review evaluation/due-review APIs remain deferred.

## Executed checks

All database tests used a newly initialized private PostgreSQL 18 cluster bound to
127.0.0.1:55440. Test databases were distinct from development at 127.0.0.1:5432.
Migration rehearsals refused nonempty destinations and retained their fixtures. No
development database was used for destructive tests.

| Check | Result |
| --- | --- |
| Complete backend pytest suite, all isolated database URL variables supplied | 181 passed; no skips |
| Final reset/restore and safety regression after adding all-table content fingerprints | 8 passed |
| Historical nonempty 0001/0004/0005/0006 upgrade rehearsals and new nonempty 0007 -> 0008 | Passed; every preexisting column/reference checked |
| Actual isolated pg_dump -> confirmed reset -> pg_restore | Passed; preserved table fingerprints and restored legacy row counts matched |
| Invalid identity/token/expired report/missing or changed backup/database drift | Refused before deletion |
| Catalog quality, homographs, duplicate saves, owner isolation, mastery, FKs and initial-state guards | Passed |
| Alembic check on isolated head schema | No new upgrade operations |
| Ruff check and format check | Passed |
| pip check | No broken requirements |
| Actual curated CLI validation, first import, repeated import and synthetic-only explicit approval | Passed on isolated phase4_cli; repeated batch reported unchanged |
| Android testDebugUnitTest | 67 passed, no skips/failures/errors |
| Android assembleDebug | Passed |
| Android lintDebug | Passed, 0 errors / 50 warnings |
| Android compileDebugAndroidTestKotlin | Passed; instrumentation compiled only |
| Physical device / emulator execution | Not performed |

Backend warnings: existing FastAPI/Starlette test-client deprecation and SQLAlchemy
reflection warning about dialect_options. Android reported an existing deprecated
ResponseBody factory in tests. These did not fail the checks.

## Remaining limits and operator actions

The catalog intentionally stays empty/unpublished until separately authored records are
imported and a human approves them. No live vocabulary dataset was generated or imported.
The real backup is 8,476,376 bytes; backup existence/size/SHA-256 were verified. A real
development restore was not attempted; restore was proven only on synthetic isolated data.

The confirmed reset removes one published relational vocabulary target while preserving
its self-contained preview bundle, lesson/run/bookmarks and all accounts/sessions. That
bundle's old vocabulary UUID will not resolve through the new dictionary API. New curated
curriculum authoring and executable lessons require a later contract. Legacy table DDL and
historical provider/content services remain to preserve reproducible migrations and old
preview infrastructure; only curated tables serve active dictionary and collection APIs.

Coordinate backend/Android rollout, follow the physical verification checklist in the
schema guide, and use the exact new-report confirmation workflow in the reset plan.
OpenCC validation and Pinyin consistency checks require human linguistic review; they do
not establish HSK membership or factual correctness. The future SRS evaluator must use
the same collection, Vietnamese prompts, Simplified handwriting and idempotent submissions.
