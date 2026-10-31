# Development guide

Phase 5.0 [FSRS-only replacement](runbooks/srs-fsrs-only-deployment.md) is deployed
in local development at 0014. No scheduler rollout flag or fixed-interval fallback
exists. Run `python -m scripts.srs_v2_isolated_checks` from the backend venv for
fresh dedicated databases and preservation/concurrency tests; fixtures remain.
Future database changes still require explicit authorization. Historical deployment
notes below describe earlier revisions rather than the current database state.

Device-test note (30 October): this AGP setup's `connectedDebugAndroidTest` cleanup
uninstalls the target application. Run it only on an isolated emulator/test phone,
not a device holding user sign-in or drafts. Use `adb install -r` for ordinary APK
updates. See [the observed cleanup and recovery](srs-submission-pinyin-20261030.md).

Phase 4.4 [review UX and performance](srs-phase-4.4-ux-performance.md) adds persistent
stage selectors, freely collected drafts with canonical server submissions, safe next-word
prefetch and concise feedback. API additions are backward-compatible; no migration or
scheduling change. Reload the API before installing Android.

For current policy preparation, see [Phase 4.1D completion](srs-phase41d-completion.md)
and the [installation runbook](runbooks/srs-phase41d-installation.md). The final
2,804-policy candidate preserves the previous 2,562 and adds 242 reviewed policies.
It is **installed and verified** in development following explicit authorization:
656 inserts, zero updates, all existing learner data preserved. See the
[deployment report](runbooks/srs-phase41d-deployment-20261029.md). The updated backend
is running and the existing updated Android APK is ready for physical testing.

For current randomized SRS sessions, handwriting, verification and first-device testing,
follow [Phase 4.3](srs-phase-4.3-experience.md). Reload its backend source for the new
read-only session-targets and character-count contracts before installing Android.

For the current [Android SRS stabilization and physical-device checklist](android-srs-review.md),
use an isolated synthetic backend on port 8001 for every graded test. Updated Android
requires the source API contract with optional `request_id`, mastery distribution and
final mastery fields. No new migration is required; do not reset development vocabulary
or progress. Physical-device execution remains pending.

Phase 4.1A adds the [SRS backend foundation](srs-foundation.md),
[verification results](srs-verification.md) and an explicit
[0011 operator deployment runbook](runbooks/srs-local-deployment.md).
Local development is now at 0011 following explicit authorization; see the
[deployment verification](runbooks/srs-0011-deployment-20261026.md).
Do not migrate the development database without operator authorization.

Phase 4.1B's [review engine and Android contract](srs-review-engine.md) requires
additive migration 0012 and explicitly installed reviewed sense policies. Development
remains at 0011; follow the [0012 operator procedure](runbooks/srs-0012-deployment.md)
only after authorization. See [executed verification](srs-review-verification.md)
for isolated migration/concurrency database variables and test results. Android UI
integration remains Phase 4.2 work.

For direct Codex session review, use the versioned development-only
[local Codex runbook](runbooks/local-codex-vocabulary.md) and
[current review coverage](phase4.0.3-codex-review.md). Additive migration 0010
and a separate opt-in are required; no paid review provider is needed.

Phase 4.0.2: [bulk vocabulary pipeline](bulk-vocabulary-pipeline.md) adds global integrity
auditing, configured external review, versioned correction attempts, explicit database
reconciliation/confirmation and resumable import/submission. Read the blocked-status
snapshot before attempting development writes.

Phase 4.0.1: follow [AI-assisted vocabulary publication](ai-vocabulary-publication.md)
for additive migration 0009, offline review exchange, explicit publication opt-in and
coverage reporting. This workflow preserves all existing catalog and user data.

Phase 4 supersedes the historical dictionary/wordbook API and import instructions below.
Follow [the vocabulary reset plan](vocabulary-reset-plan.md),
[curated schema/API](curated-vocabulary-schema.md), and
[JSONL import guide](curated-vocabulary-import.md). Apply additive 0008 explicitly;
legacy deletion requires the separate backup/dry-run/confirmed maintenance workflow.

## Personal vocabulary (Phase 3.4)

Apply additive revision `0007_personal_vocabulary` explicitly before using the new wordbook.
Do not reimport dictionary data or reset the native database. See
[personal vocabulary](personal-vocabulary-design.md) for migration commands, isolated test
URLs, authenticated endpoints, Android checks and the unperformed physical-device checklist.
The fresh-database rehearsal uses `WORDBOOK_MIGRATION_TEST_DATABASE_URL` and retains fixtures.


For Phase 3.3 model downloads, handwriting state, Android checks and physical-device
verification, follow [dictionary handwriting](android-handwriting.md).

For Phase 3.1.1, follow [dictionary revision repair and Vietnamese character enrichment](dictionary-vietnamese-enrichment.md).
New CC-CEDICT imports derive revisions from header/checksum when `--revision` is omitted.
Repair of an existing placeholder defaults to dry-run and requires explicit `--confirm`;
apply additive revision `0006_dictionary_enrichment` before confirmed repair/enrichment.
No development database repair or enrichment has been automatically applied. The additional
`ENRICHMENT_MIGRATION_TEST_DATABASE_URL` must select a fresh empty isolated PostgreSQL DB.

Phase 3.1 dictionary lookup uses additive revision `0005_dictionary_foundation` and an
explicit local CC-CEDICT v1 import, never a startup download. Follow
[dictionary foundation](dictionary-foundation.md) for source/license review, checksums,
import commands, Swagger, PostgreSQL tests and synthetic performance measurements.
`DICTIONARY_MIGRATION_TEST_DATABASE_URL` selects an additional fresh-empty rehearsal from
0004; like the legacy rehearsal, it refuses existing tables and retains its fixtures.

For the playable vocabulary sample, apply revision `0004_vocabulary_player` and publish
lesson-ni version 2. Follow [the Phase 3 player guide](vocabulary-player.md) for current
native PostgreSQL/USB commands, scene support and checkpoint semantics.

Follow the root README for setup and `AGENTS.md` for coding boundaries. Run Python commands
from `backend/`, Gradle from `android/`, and Docker Compose from the repository root.
Android Studio should open `android/`. Existing root `.idea` and `.gradle` folders are
local starter metadata, ignored by Git; Studio may recreate its settings under `android/`.

For the current Windows workflow (native PostgreSQL, physical Android over USB,
ADB reverse and debug localhost URL), follow [USB development](android-usb-development.md).
Docker below is an optional alternative, not a prerequisite. That guide also explains
backend reload versus Android rebuild/install and migration requirements.

Keep backend development dependencies reproducible by reviewing `pyproject.toml` changes,
installing into a clean virtual environment, running tests and regenerating the lock:

```powershell
.venv\Scripts\python -m pip freeze --exclude-editable | Out-File -Encoding ascii requirements-dev.lock
```

The lock records an exact tested toolchain, not deployment configuration. Before production,
review dependency updates, choose your supported Python version and packaging strategy,
configure TLS, signing, monitoring, backups and secret-managed database credentials.

For schema changes, edit SQLAlchemy models and run:

```powershell
.venv\Scripts\python -m alembic revision --autogenerate -m "describe change"
# Review the generated revision before applying it.
.venv\Scripts\python -m alembic upgrade head
.venv\Scripts\python -m alembic check
```

No migration runs automatically at API startup. Migrations use async psycopg through
Alembic's async engine bridge. Review constraints, indexes, foreign keys and data migration
requirements; metadata autogeneration cannot infer every safe data transformation.
Alembic and pytest use an explicit event loop factory because async psycopg does not support
Windows' default Proactor loop. Uvicorn commands must include
`--loop app.core.event_loop:new_event_loop`, or use `python -m app`.
See [psycopg's async platform requirements](https://www.psycopg.org/psycopg3/docs/advanced/async.html).

Create a separate integration database from the root:

```powershell
docker compose exec postgres createdb -U chinese chinese_learning_test
cd backend
$env:DATABASE_URL = 'postgresql+psycopg://chinese:local-dev-only@127.0.0.1:5432/chinese_learning_test'
.venv\Scripts\python -m alembic upgrade head
$env:TEST_DATABASE_URL = $env:DATABASE_URL
.venv\Scripts\python -m pytest -q
Remove-Item Env:DATABASE_URL, Env:TEST_DATABASE_URL
```

Adapt credentials if overridden. Do not recreate an existing test database; apply new
migrations. API tests do not need PostgreSQL. DB tests roll back their fixture writes.
Use explicit transaction ownership when implementing services. Add focused Android tests
for repository contracts and ViewModel state transitions, plus device tests for Room and UI.
Commit exported Room JSON schemas and provide migration tests for later schema changes.

Email/password authentication is implemented in Slice 2; Google linking and sync remain
future work. Read [authentication](authentication.md) and [Slice 2 verification](slice2-verification.md).
Avoid
building multiple unfinished features at once. A feature should have a testable vertical
slice, explicit error behavior and reviewed security boundaries before the next begins.

## Slice 1 authoring and migration rehearsal

Read [content authoring](content-authoring.md) for the compatibility schema, scene contracts,
sample limitations and creating another lesson using the same template. No dependencies
were added; the existing lock remains the tested environment. From backend, against an
explicitly selected development database:

```powershell
.venv\Scripts\python -m alembic upgrade head
.venv\Scripts\python -m scripts.validate_content --content-dir content
.venv\Scripts\python -m scripts.import_content --content-dir content
# Repeating import is safe. Publication is a separate, explicit operation:
.venv\Scripts\python -m scripts.publish_lesson --lesson lesson-ni --version 1 --storage-dir .content-storage
.venv\Scripts\python -m scripts.inspect_bundle --lesson lesson-ni --version 1 --storage-dir .content-storage
```

Published bundles are CONTENT_PREVIEW only. Publication checks every referenced local object;
missing objects or incompatible contracts leave the version DRAFT. Both the exact template
and lesson version become immutable. Repeating publication rejects the already published
version; repeating the same import is a no-op for definitions. A new lesson version can
reuse the published template; changing a template requires a new template version. Scene
removal requires a new template version even for an imported draft. Draft edits can update
existing scene configurations and add new keys; ordering must stay unique at every DB write.
For complex reorderings use a new version rather than relying on transient duplicate positions.

For PostgreSQL tests use TWO separate databases. The regular tests roll back fixture writes
on an already migrated database. The upgrade test starts at 0001 with representative legacy
rows, upgrades to head and checks all original values and metadata drift. It refuses any
existing table and intentionally retains fixtures for inspection. Pick a new name each run:

```powershell
# From the repository root, using the configured Compose credentials:
docker compose exec postgres createdb -U chinese chinese_learning_test
docker compose exec postgres createdb -U chinese chinese_slice1_upgrade_test_01
cd backend
$env:DATABASE_URL = 'postgresql+psycopg://chinese:local-dev-only@127.0.0.1:5432/chinese_learning_test'
.venv\Scripts\python -m alembic upgrade head
$env:TEST_DATABASE_URL = $env:DATABASE_URL
$env:MIGRATION_TEST_DATABASE_URL = 'postgresql+psycopg://chinese:local-dev-only@127.0.0.1:5432/chinese_slice1_upgrade_test_01'
.venv\Scripts\python -m ruff check .
.venv\Scripts\python -m ruff format --check .
.venv\Scripts\python -m pytest -q
.venv\Scripts\python -m alembic check
Remove-Item Env:DATABASE_URL, Env:TEST_DATABASE_URL, Env:MIGRATION_TEST_DATABASE_URL
```

Skip createdb for a regular test database that already exists; never recreate/reset it.
The migration test always needs a fresh empty database, not the regular test database.
Without database URLs the PostgreSQL tests are skipped; that is not migration validation.
The Slice 1 revision refuses downgrade because deleting published content requires a
separately reviewed retention strategy. Alembic autogeneration does not inspect trigger
bodies; review the revision and run the immutability tests when changing publication rules.
