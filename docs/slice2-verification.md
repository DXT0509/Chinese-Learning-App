# Slice 2 setup and verification

Run commands from the repository root unless a block changes directory. Never point
test URLs at a shared or production database. Migration rehearsal refuses existing
tables and leaves its legacy fixtures intact; choose a new database name each run.

Install the tested dependency set and migrate an explicitly selected local database:

```powershell
cd backend
.venv\Scripts\python -m pip install -r requirements-dev.lock
.venv\Scripts\python -m pip install --no-deps -e .
Copy-Item .env.example .env # only when .env does not already exist
# Edit backend/.env to select your local database, then:
.venv\Scripts\python -m alembic upgrade head
.venv\Scripts\python -m scripts.validate_content --content-dir content
.venv\Scripts\python -m scripts.import_content --content-dir content
# Publish once; an already published version must not be republished:
.venv\Scripts\python -m scripts.publish_lesson --lesson lesson-ni --version 1
$env:ALLOW_CONTENT_PREVIEW = 'true'
.venv\Scripts\python -m app
```

The sample has no audio/stroke media, executable Scene Engine, completion, EXP or SRS.
Only PUBLISHED versions are retrievable. CONTENT_PREVIEW requires the server flag and
`allow_preview=true` on bundle GET or start POST. Drafts remain unavailable.

| Method | Learning route under `/api/v1` | Behavior |
| --- | --- | --- |
| GET | `/lessons` | Available published version metadata, explicitly preview-only |
| GET | `/lesson-versions/{version_id}/bundle?allow_preview=true` | Immutable SHA-256/length-verified bundle |
| POST | `/learning-runs` | `{lesson_version_id,request_id,allow_preview:true}`; UUID request deduplicates per owner |
| GET | `/learning-runs` | Current user's most recent 100 runs |
| GET | `/learning-runs/{run_id}` | Resume pinned version and checkpoints |
| PUT | `/learning-runs/{run_id}/scenes/{scene_key}` | `{page:0..10000}` bookmark; repeated identical writes are idempotent |

All routes require `Authorization: Bearer <access_token>`. `/auth/me` supplies current user
information. Reusing a start request UUID with another version returns 409. Foreign runs
and unknown scenes return 404. Checkpoints validate membership in the pinned immutable
bundle and cannot claim PASS/completion. The page value is a bounded preview bookmark,
not engine-validated learning evidence. New publications never move existing runs.
There is no write to legacy `user_lesson_progress`, `user_vocabulary` or SRS tables.

Android: open `android/`, run the debug app, and choose Tạo tài khoản from Login.
Use a syntactically valid test email and a 6–128 character test password. On login the
app opens lessons. Consent to preview access, start a run, save a scene bookmark, reload
or restart the app and resume the run. Log out and use a second account to check isolation.
Debug defaults to `http://127.0.0.1:8000/` through ADB reverse for USB devices.
For an emulator without reverse use `-PDEV_API_BASE_URL=http://10.0.2.2:8000/`.
See [native PostgreSQL/USB setup](android-usb-development.md). Release uses HTTPS and
blocks cleartext. Do not send real passwords over debug HTTP.

Create two isolated databases with your configured Compose credentials (skip createdb
for an existing regular test database, but always use a fresh migration rehearsal database):

```powershell
docker compose exec postgres createdb -U chinese chinese_slice2_test
docker compose exec postgres createdb -U chinese chinese_slice2_upgrade_01
cd backend
$env:DATABASE_URL = 'postgresql+psycopg://chinese:local-dev-only@127.0.0.1:5432/chinese_slice2_test'
.venv\Scripts\python -m alembic upgrade head
$env:TEST_DATABASE_URL = $env:DATABASE_URL
$env:MIGRATION_TEST_DATABASE_URL = 'postgresql+psycopg://chinese:local-dev-only@127.0.0.1:5432/chinese_slice2_upgrade_01'
.venv\Scripts\python -m pip check
.venv\Scripts\python -m ruff check .
.venv\Scripts\python -m ruff format --check .
.venv\Scripts\python -m pytest -q
.venv\Scripts\python -m alembic check
Remove-Item Env:DATABASE_URL, Env:TEST_DATABASE_URL, Env:MIGRATION_TEST_DATABASE_URL
cd ../android
.\gradlew.bat testDebugUnitTest assembleDebug lintDebug
# Requires a connected emulator/device; separate from unit/build/lint checks:
.\gradlew.bat connectedDebugAndroidTest
```

No URL means PostgreSQL tests skip; skips do not validate security persistence or migrations.
The test suite includes registration, normalization, duplicate registration, dummy/wrong
password login, Argon2id, expiry, rotation, hashed token storage, logout, replay revocation,
unauthorized and foreign-resource access, idempotent runs/checkpoints and publication pinning.
The existing nonempty migration test upgrades from 0001 through head, preserving original
values and relationships and checking metadata drift. Slice 1 regression tests remain.

Android repository tests cover refresh, rotated credential persistence, rejected sessions,
transient failure and logout. ViewModel tests cover validation, loading/login, retry request
identity, checkpoints and clearing account data. A device test checks Keystore encryption,
storage recreation and deletion; it requires an emulator and is not a JVM security proof.

## Completion report — 2026-10-18

Executed against a newly initialized, ignored local PostgreSQL 18 cluster on loopback
port 55432 because Docker was unavailable. No existing database was reset or modified.
The test cluster data and migration fixtures remain in
`backend/.test-postgres-slice2-20261018/` for inspection; the server was stopped after checks.
The final migration rehearsal database is `slice2_upgrade_final`; regular tests used
`slice2_test`. Earlier rehearsal fixtures also remain in `slice2_upgrade`.

| Executed check | Result |
| --- | --- |
| `python -m pip check` | Passed |
| Ruff check and format check | Passed, 49 Python files formatted |
| Full pytest with both isolated database URLs | **67 passed, no skips** |
| Alembic upgrade head | Passed on empty isolated DB |
| Nonempty migration rehearsal 0001 → head | Passed; original values/relationships preserved |
| `alembic check` | No new upgrade operations detected |
| Slice 1 content validation | Passed; CONTENT_PREVIEW only |
| Android `testDebugUnitTest` | **7 tests passed** |
| Android `assembleDebug lintDebug` | Passed; 23 lint warnings, no errors |
| Android `assembleDebugAndroidTest` | Passed; device tests compiled |
| Emulator/device tests and manual UI/network validation | Not run: `adb devices` showed no connected device |

Pytest emits a Starlette/httpx deprecation warning and the existing SQLAlchemy dialect_options
reflection warning during migration rehearsal. Lint warnings remain recorded in
`android/app/build/reports/lint-results-debug.html`; no dependency upgrades unrelated to this
slice were attempted. Build artifacts and local test databases are ignored.

Revision `0003_sessions_and_runs` adds exactly five tables: `password_credentials`,
`auth_sessions`, `refresh_credentials`, `lesson_runs` and `lesson_scene_progress`.
It alters no legacy table or published version and refuses destructive downgrade.
The preceding migrations remain unchanged. There is no claim of emulator/device validation,
production security review or public-release readiness.

Created files:

- `backend/.env.example`
- `backend/alembic/versions/0003_sessions_and_runs.py`
- `backend/app/models/session.py`
- `backend/app/schemas/session.py`
- `backend/app/services/authentication.py`
- `backend/app/services/learning_access.py`
- `backend/app/dependencies/authentication.py`
- `backend/app/api/v1/endpoints/authentication.py`
- `backend/app/api/v1/endpoints/learning.py`
- `backend/tests/test_sessions.py`
- `android/app/src/main/java/com/example/chineselearningapp/domain/repository/SessionRepository.kt`
- `android/app/src/main/java/com/example/chineselearningapp/core/network/SessionApi.kt`
- `android/app/src/main/java/com/example/chineselearningapp/core/network/SessionVault.kt`
- `android/app/src/main/java/com/example/chineselearningapp/feature/auth/data/RemoteSessionRepository.kt`
- `android/app/src/main/java/com/example/chineselearningapp/feature/auth/SessionViewModel.kt`
- `android/app/src/main/java/com/example/chineselearningapp/feature/auth/SessionScreen.kt`
- `android/app/src/main/res/values/session_strings.xml`
- `android/app/src/test/java/com/example/chineselearningapp/SessionRepositoryTest.kt`
- `android/app/src/test/java/com/example/chineselearningapp/SessionViewModelTest.kt`
- `android/app/src/androidTest/java/com/example/chineselearningapp/SessionVaultTest.kt`
- `docs/slice2-verification.md`

Modified files:

- `.gitignore`, `AGENTS.md`, `README.md`
- `backend/pyproject.toml`, `backend/requirements-dev.lock`
- `backend/app/main.py`, `backend/app/core/config.py`, `backend/app/core/security.py`
- `backend/app/models/__init__.py`
- `android/app/proguard-rules.pro`
- `android/app/src/main/java/com/example/chineselearningapp/MainActivity.kt`
- `android/app/src/main/java/com/example/chineselearningapp/core/di/AppModule.kt`
- `android/app/src/main/java/com/example/chineselearningapp/core/navigation/AppNavigation.kt`
- `android/app/src/main/java/com/example/chineselearningapp/core/auth/README.md`
- `android/app/src/main/java/com/example/chineselearningapp/feature/auth/README.md`
- `docs/authentication.md`, `docs/architecture.md`, `docs/development-guide.md`
- `docs/mvp-implementation-plan.md`, `docs/api-conventions.md`, `docs/database-design.md`

The working directory has no Git metadata, so a Git diff/commit status was unavailable.
No commit was created. Changes were made directly in the supplied workspace.

Remaining limitations: unverified email and no recovery service; local single-process rate
limiting; no shared session cleanup job or completed production security review; rotation
response loss can require login again; the run list returns the latest 100 without a cursor.
Preview bookmarks do not implement scene execution, completion, EXP, SRS, speech,
handwriting or synchronization. Google linking remains deferred until pre-release.
