# Development guide

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
