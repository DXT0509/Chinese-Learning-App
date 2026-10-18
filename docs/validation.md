# Slice 1 validation — 2026-10-18

Executed on Windows using backend/.venv (Python 3.14, locked dependencies unchanged).
Docker client was present but its engine was unavailable. A fresh PostgreSQL **18.3**
cluster was initialized in ignored backend/.test-postgres-slice1, bound only to
127.0.0.1:55439, with separate newly created databases. The existing server on 5432 was
not used. No database was reset, downgraded or dropped, and no application volume changed.
The configured Docker PostgreSQL **17.9** runtime remains unverified for this slice.

| Check | Result |
| --- | --- |
| Backend suite with both explicit DB URLs | **56 passed, 1 warning in 16.56s** |
| Ruff | `ruff check .` and `ruff format --check .` passed, 40 Python files formatted |
| Imports/bytecode | `compileall -q app scripts alembic tests` passed |
| Dependencies | `pip check`: no broken requirements; no constraints or lock changes |
| New migration on empty DB | `alembic upgrade head` passed |
| Nonempty legacy upgrade | Passed on fresh slice1_upgrade_verified: all original columns, UUIDs, relationships, repeated occurrences, legacy keys, multiword memberships, completion times and SRS state preserved |
| Legacy compatibility | Existing unknown lesson type retained under NOT VALID check; memberships retained with NULL version/role; no inferred TEACHES or fabricated provenance |
| Metadata drift | `alembic check`: No new upgrade operations detected, on empty-upgrade and legacy-upgrade databases |
| Revision | `0002_content_foundation (head)` |
| Initial migration integrity | SHA-256 unchanged: c94de95eb3c4640861c8f983c5497e9ef23464930a420040e8d860d9b488b6b6 |
| Sample files | `scripts.validate_content --content-dir content` passed |
| Repeated CLI import | Ran twice in isolated slice1_authoring: one DRAFT version and one TEACHES target |
| CLI publication/inspection | Passed separately in slice1_cli_preview; CONTENT_PREVIEW bundle hash verified; repeated publication rejected |
| Publication behavior | Tests cover published lesson/template/scene/membership/asset immutability, invalid targets/contracts, missing media, new drafts and retaining old bundle bytes |
| Windows Unicode | CLI inspection emits Hanzi/Vietnamese successfully; regression test forces cp1252 redirected output |
| Existing liveness | `/health` and `/api/v1/health` both HTTP 200 with expected contract through ASGI transport tests; no live server/device test in this slice |
| Android | Untouched; Gradle/emulator/device checks not rerun |

The installed SQLAlchemy/Alembic toolchain emits `SAWarning: Can't validate argument
'dialect_options'; can't locate any SQLAlchemy dialect named 'dialect'` during reflection
of the staged NOT VALID check. Normal drift checks complete successfully; a strict
warnings-as-errors drift check fails on this warning. It was not suppressed and no
dependency update was made. Alembic does not compare trigger bodies; focused PostgreSQL
immutability tests exercise those rules explicitly.

The sample in slice1_authoring remains **DRAFT**, with no fabricated media. A separate
publication demonstration produced the ignored local object
`sha256/67696692356f6c4aa5313dfe859cb596d0b02a3345cc731acf43d1fbdea1e040.json`.
It contains two reference scenes, not the complete seven-scene learning lesson. Reviewed
audio, stroke assets/components and all learner capabilities remain future delivery work.

The temporary test cluster was stopped after validation; its data files were retained for
inspection. The complete source inventory and reproducible commands are in
[content authoring](content-authoring.md) and [development guide](development-guide.md).
Before rollout, repeat the checks on the configured PostgreSQL 17.9 image and an approved
restored copy of any real legacy database; fixture preservation is not an audit of live data.

# Earlier foundation validation — 2026-10-17

Validation ran on Windows in the provided workspace. Source structure, package/import
consistency and exported Room schema were inspected after moving the Android starter.
The original Android application ID and package are preserved.

| Check | Result |
| --- | --- |
| Python environment | Python 3.14.0; dependencies installed in `backend/.venv` |
| Dependency consistency | `python -m pip check`: no broken requirements |
| Python lint/format | Ruff check passed; all 23 Python files formatted |
| Backend tests | `pytest -q`: **8 passed in 2.12s**, including PostgreSQL constraints |
| Alembic upgrade | `alembic upgrade head` applied `0001_initial` successfully |
| Migration drift | `alembic check`: **No new upgrade operations detected** |
| Alembic revision | `alembic current`: **0001_initial (head)** |
| Offline migration SQL | `alembic upgrade head --sql` rendered successfully |
| Live API | `/health` and `/api/v1/health` returned expected HTTP 200 JSON, including with the final JSON logging/server launcher |
| Docker Compose configuration | `docker compose config --quiet`: passed |
| Android debug APK | `assembleDebug`: passed |
| Android release APK | `assembleRelease`: passed; unsigned, reserved API URL |
| Android unit tests | `testDebugUnitTest`: **2 tests, 0 failures, 0 errors** |
| Android lint | `lintDebug`: **0 errors, 23 warnings** |
| Android instrumentation APK | `assembleDebugAndroidTest`: passed |
| Android device execution | Not run: `adb devices` found no emulator/device |
| Release transport configuration | Merged release manifest has `usesCleartextTraffic=false`, backup disabled and explicit extraction exclusions |
| Credential hygiene | Common private-key/API-token pattern scan found no matches in source/docs/config examples; local SDK paths, environments, build outputs and credentials are ignored |

Final Android command:

```powershell
.\gradlew.bat assembleDebug assembleRelease testDebugUnitTest lintDebug assembleDebugAndroidTest --console=plain
```

Result: **BUILD SUCCESSFUL in 1m 2s**, 144 actionable tasks (79 executed, 65 up-to-date).
Unit tests cover the versioned health HTTP contract, invalid payload rejection, unavailable
state and retry recovery. The instrumentation suite includes a Room Unicode/upsert test;
its APK compiled, but it has not been executed on a device. Android-to-FastAPI connectivity
has therefore been validated through compilation, repository HTTP tests and live backend
requests, not through an emulator end-to-end run.

Lint warnings comprise newer dependency versions and unused starter color resources.
Builds also reported inability to strip two dependency native libraries; both APK variants
packaged successfully. Versions are intentionally pinned as a compatible set rather than
automatically upgrading every dependency. The release URL is a reserved placeholder;
real HTTPS API configuration and release signing remain manual setup.

## PostgreSQL execution detail

Docker Desktop was initially stopped and was started for validation. Pulling the configured
`postgres:17.9` image failed with registry/CloudFront EOF errors on repeated attempts,
including an alternate public mirror. **The configured Compose database image was not
started successfully**, so its startup/health check remains unverified in this environment.

To validate actual database behavior, an already-cached PostgreSQL 17.6 image
(`public.ecr.aws/supabase/postgres:17.6.1.156`) was used in a separate temporary container,
`chineselearning-validation`, on host loopback port 55432 with a fresh isolated database.
The image's initialization scripts were bypassed; plain `initdb`/`postgres` were used.
No existing Supabase database or user data was accessed. The initial migration, drift check,
timezone handling, repeated-character association, custom-entry validation and uniqueness
constraints passed on that database. Test fixture writes were rolled back.

Database checks exposed Windows' default Proactor loop incompatibility with psycopg.
Alembic, pytest and the documented API launcher now use a compatible selector loop.
The temporary PostgreSQL process and API validation server were stopped after checks;
Docker Desktop remains running. The stopped validation container is separate from Compose
and can be removed when no longer needed. No application database volume was reset.

Remaining manual validation: retry `docker compose up -d postgres` after registry access
recovers, apply migrations to that instance, run on an emulator/device, execute
`connectedDebugAndroidTest`, and visually verify loading, reachability, unavailable and retry.
