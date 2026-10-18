# Slice 1 content authoring

The approved eight-slice plan overrides the A/B/C labels in the target ERD. Slice 1
implements five new tables and adapts existing content tables only. The other schema
tables remain proposals. No learner execution, authentication, EXP or SRS is added.

## Reconciliation and bounded assumptions

- The 45-table design is a destination, not this migration. Components, radicals, POS
  joins, HSK, scene overrides, roadmap releases, runs and evaluation policies are deferred
  to their assigned slices. A nullable reviewed `part_of_speech` text attribute suffices
  now; it is not a permanent POS enum. HSK stays unclassified.
- The full seven-scene vocabulary flow remains the product requirement: introduction
  and speaking, information, character analysis, stroke demonstration, handwriting,
  conditional translation, optional transcription. Only information and ordered character
  reference contracts are authored in Slice 1. Their bundles have purpose
  `CONTENT_PREVIEW`, never permission to complete a learner lesson.
- The sample meaning is exactly bạn, citation Pinyin nǐ, Hán-Việt nhĩ and POS pronoun.
  Stroke count, dictionary radical, components, history and media are not supplied as
  reviewed content. NULL denotes unknown; visible placeholder notes explain omissions.
- JSON is the primary UTF-8 authoring format. Version 1 contracts reject unknown fields,
  executable configurations and unsupported scenes. References use namespace-qualified
  deterministic UUIDv5 aliases; existing UUIDs can be supplied explicitly for adoption.
- Draft templates and lesson versions are imported separately from publication. Publishing
  a preview publishes its exact template version too, in the same transaction. A later
  draft cannot modify either publication; corrections use a new version number.

## Safe expansion

`0001_initial.py` is immutable. Revision `0002_content_foundation` adds assets,
lesson_templates, lesson_template_versions, lesson_template_scenes and lesson_versions.
Existing audio_reference, stroke_order_asset, radical_info, title, lesson_order and all
personal data remain. New verified asset FKs start NULL; no arbitrary legacy key is mapped.
Unknown stroke_count may now be NULL; existing zero observations are retained unchanged.

lesson_vocabulary gains a generated UUID primary key, nullable lesson_version_id and role.
Its old columns remain, with partial uniqueness preserving the old unversioned membership
contract; versioned memberships have separate unique vocabulary/position constraints and
a composite FK ensuring version and lesson agree. Existing associations keep NULL version
and role. They do not become TEACHES evidence. No existing lesson is guessed into a template
or version, particularly multiword lessons. A reviewed adoption explicitly supplies existing
lesson/vocabulary UUIDs in authoring files and creates a new version; legacy links stay intact.
Progress continues to reference the original lesson UUID. Never infer eligible knowledge.

A NOT VALID lesson-type check preserves unknown legacy types while constraining new writes
to the five planned types. The authoring tool accepts only VOCABULARY. Audit old types before
separately validating the database constraint. PostgreSQL describes this staged constraint
behavior in [ALTER TABLE](https://www.postgresql.org/docs/17/sql-altertable.html).

Published versions, their memberships, template scenes and asset metadata are guarded by
database triggers as well as controlled services. Catalog projections are snapshotted into
bundles; changes to catalog prose affect only new publications. Published word identities
and character occurrence structure cannot be repurposed through the importer. No automatic
downgrade is provided: dropping this schema could destroy authored or published content.

## Commands

Commands below run from backend after applying migrations to an explicitly selected local
database. They do not expose unauthenticated authoring HTTP endpoints.

```powershell
.venv\Scripts\python -m scripts.validate_content --content-dir content
.venv\Scripts\python -m scripts.import_content --content-dir content
.venv\Scripts\python -m scripts.publish_lesson --lesson lesson-ni --version 1 --storage-dir .content-storage
.venv\Scripts\python -m scripts.inspect_bundle --lesson lesson-ni --version 1 --storage-dir .content-storage
```

Import leaves the sample DRAFT. Publication is an explicit separate command. Preview scenes
need no fabricated audio or animation; adding required media contracts later must verify
their actual files and hashes. Bundles are canonical UTF-8 JSON, SHA-256 addressed by
`sha256/<digest>.json`. Inspect verifies the bytes against the database hash before output.
Use local storage only for public catalog media; never put private voice or handwriting here.
If the database transaction fails after object creation, an unreferenced immutable file can
remain. It is safe to retry; no object is replaced. Do not remove objects without checking
database references and any future retention requirements. There is no automatic garbage
collector in this slice. CLI output is UTF-8, including redirected inspection output on Windows.

To add a word, copy content/vocabulary/ni.json, choose a new alias (or reviewed existing UUID),
add its character definitions and ordered occurrences with exact NFC spelling coverage.
To reuse the template, copy content/lessons/lesson-ni.json, give the lesson a new alias/title
and exactly one TEACHES vocabulary reference, pin the template alias and version explicitly.
Validate and import the whole directory. To correct a publication, increment lesson version;
increment template version only if scenes change. Never reuse a published version to edit it.
Media declarations belong in content/assets/*.json and reference existing stable local object
keys, MIME type, byte length and SHA-256; import verifies their bytes in --storage-dir.
For real reviewed media, calculate SHA-256 with `Get-FileHash`, copy the existing file into
`.content-storage/sha256/<lowercase-digest>.<extension>`, then declare that same key, digest
and byte length. Never insert a placeholder asset row for an object that does not exist.

Integration tests use TEST_DATABASE_URL for an already migrated dedicated test database.
Migration rehearsal uses MIGRATION_TEST_DATABASE_URL for a separate, newly created empty
database: tests refuse any existing table and never reset, drop or downgrade it. Each run
needs a fresh database name. See development-guide.md for setup and check commands.

## Changed source inventory

Created:

- backend/app/models/content.py
- backend/app/schemas/content.py
- backend/app/services/content_files.py
- backend/app/services/content_storage.py
- backend/app/services/content_authoring.py
- backend/app/services/lesson_publication.py
- backend/alembic/versions/0002_content_foundation.py
- backend/scripts/__init__.py and _content_cli.py
- backend/scripts/validate_content.py and import_content.py
- backend/scripts/publish_lesson.py and inspect_bundle.py
- backend/content/vocabulary/ni.json
- backend/content/templates/vocabulary-v1.json
- backend/content/lessons/lesson-ni.json
- backend/tests/test_content_files.py and test_content_cli.py
- backend/tests/test_content_postgres.py and test_content_migration.py
- docs/content-authoring.md

Modified:

- backend/app/models/learning.py and __init__.py
- .gitignore, AGENTS.md and README.md
- docs/database-design.md, learning-engine-design.md and lesson-examples.md
- docs/srs-design.md and mvp-implementation-plan.md
- docs/architecture.md, development-guide.md and validation.md

No Android files, dependencies, initial migration or personal learning tables changed.
vocabulary_characters already supported repeated ordered occurrences; its schema is reused
unchanged with strict authoring coverage validation. The five existing table responsibilities
are therefore adapted without adding a redundant character association table.
