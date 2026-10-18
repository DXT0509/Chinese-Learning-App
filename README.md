# Chinese Learning App

Android + FastAPI + PostgreSQL foundation for Vietnamese-speaking beginners.
Implemented: API connectivity, Room public catalog cache, DataStore preferences, Slice 1
local content authoring and immutable preview bundles, plus Slice 2 email/password login,
Keystore-encrypted Android sessions and protected version-pinned preview runs/checkpoints.
Google Sign-In is deferred until pre-release. Full learning execution, EXP, SRS and
synchronization remain future work. See [authentication](docs/authentication.md) and
[Slice 2 setup and verification](docs/slice2-verification.md).

For Windows with PostgreSQL installed directly and a USB-connected Android device, use
[the USB development guide](docs/android-usb-development.md). It covers ADB reverse,
`http://127.0.0.1:8000/`, backend reload, Android rebuild/install and password verification.
The app now opens session-aware Login/Registration or Home with a shared mint theme.

```text
ChineseLearningApp/
├── android/
│   ├── app/src/{main,debug,test,androidTest}/
│   │   └── main/java/com/example/chineselearningapp/
│   │       ├── core/{auth,database,datastore,designsystem,di,navigation,network,sync}/
│   │       ├── domain/{model,repository}/
│   │       ├── feature/{auth,roadmap,lesson,vocabulary,handwriting,quiz,review,profile}/
│   │       └── ui/theme/
│   ├── app/schemas/
│   ├── gradle/{libs.versions.toml,wrapper/}
│   └── gradlew[.bat], build.gradle.kts, settings.gradle.kts
├── backend/
│   ├── app/{api/v1/endpoints,core,dependencies,models,schemas,repositories,services}/
│   ├── alembic/versions/{0001_initial,0002_content_foundation,0003_sessions_and_runs}.py
│   ├── content/{vocabulary,lessons,templates}/
│   ├── scripts/{validate_content,import_content,publish_lesson,inspect_bundle}.py
│   ├── tests/
│   ├── pyproject.toml, requirements-dev.lock, alembic.ini, .env.example
├── docs/
├── docker-compose.yml, .env.example, .gitignore
└── AGENTS.md
```

Prerequisites: Android Studio with AGP 9 support, SDK 36 and Build Tools 36, JDK 21
for Gradle, Python 3.12+ (validated here with 3.14), PostgreSQL installed natively
or optionally through Docker Desktop with Linux containers,
and an emulator/device. Gradle Wrapper 9.2.1 is included. No Google account setup is
required for the demo. Android source and bytecode target Java 17.

From the repository root, start PostgreSQL:

```powershell
Copy-Item .env.example .env
docker compose up -d postgres
docker compose ps
```

This binds PostgreSQL to host loopback and preserves its data in a named volume. Defaults
are public local-development credentials. If changed, update `backend/.env` to match.
Do not run `docker compose down -v` unless intentionally deleting local data.

Set up Python (PowerShell):

```powershell
cd backend
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements-dev.lock
.venv\Scripts\python -m pip install --no-deps -e .
Copy-Item .env.example .env
.venv\Scripts\python -m alembic upgrade head
.venv\Scripts\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --no-access-log --loop app.core.event_loop:new_event_loop --log-config logging.json
```

For a fresh compatible resolution instead of the validated lock, use
`.venv\Scripts\python -m pip install -e ".[dev]"`. On macOS/Linux use `python3`,
`.venv/bin/python`, `cp`, and `./gradlew` in the equivalent commands.
The backend loads `.env` from `backend/` regardless of current working directory.
Use the supplied loop factory with Uvicorn: async psycopg needs a selector loop on Windows.
`python -m app` is a no-reload shortcut using the same compatible loop on port 8000.
Use secret-managed environment variables and HTTPS behind your chosen infrastructure later.

With FastAPI running, open `http://127.0.0.1:8000/docs` or run:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health
```

Health remains available without PostgreSQL because it checks API liveness only.
Database operations require migrations and a working database connection.

Authoring commands run from `backend/` after `alembic upgrade head`:

```powershell
.venv\Scripts\python -m scripts.validate_content --content-dir content
.venv\Scripts\python -m scripts.import_content --content-dir content
# Explicit publication is separate from draft import:
.venv\Scripts\python -m scripts.publish_lesson --lesson lesson-ni --version 1
.venv\Scripts\python -m scripts.inspect_bundle --lesson lesson-ni --version 1
```

The sample imports as DRAFT. Publication produces a CONTENT_PREVIEW, containing only
information and ordered character references. It cannot complete a learning lesson.
Audio, stroke media and reviewed component analysis are absent. See
[content authoring](docs/content-authoring.md) for contracts, migration compatibility,
storage, creating another lesson, correction versions and test setup.

Open **`android/`** in Android Studio, set Gradle JDK to 21, let Gradle sync, and
select an API 24+ emulator. Studio can create `android/local.properties` for your SDK.
Run the `app` configuration. Startup restores the session, then opens Home or Login;
registration is available from Login. Home links to preview runs, the roadmap/health
demo and clearly labelled future features. Debug defaults to `http://127.0.0.1:8000/`
with ADB reverse. For an emulator without reverse, build with
`-PDEV_API_BASE_URL=http://10.0.2.2:8000/`.
The repository root is a monorepo, not the Android Gradle import root.

Build and test from `android/`:

```powershell
.\gradlew.bat assembleDebug testDebugUnitTest lintDebug
# Requires a running emulator or attached Android device:
.\gradlew.bat connectedDebugAndroidTest '-Pandroid.testInstrumentationRunnerArguments.class=com.example.chineselearningapp.SessionNavigationTest'
```

Configure URLs with Gradle properties (trailing slash required):

```powershell
.\gradlew.bat assembleDebug -PDEV_API_BASE_URL=http://127.0.0.1:8000/
.\gradlew.bat assembleRelease -PRELEASE_API_BASE_URL=https://your-api.example.com/
```

Release defaults to reserved `https://api.example.invalid/`; replace it before distribution
and configure your own signing outside source control. Release URLs require HTTPS and the
release manifest disables cleartext. Only the debug source set allows local HTTP.

For a physical device over USB, run `adb reverse tcp:8000 tcp:8000`, then build with
`-PDEV_API_BASE_URL=http://127.0.0.1:8000/` (device loopback reaches the USB reverse tunnel).
Alternatively use the computer's LAN address, for example `http://192.168.1.50:8000/`,
on the same network; allow port 8000 through the firewall for your private network only.
Do not use `localhost` to reach the host from an emulator; use `10.0.2.2`.

Backend checks, from `backend/`:

```powershell
.venv\Scripts\python -m pytest -q
.venv\Scripts\python -m ruff check app tests alembic
.venv\Scripts\python -m alembic check
# Render SQL without applying it:
.venv\Scripts\python -m alembic upgrade head --sql
```

PostgreSQL integration tests require an **isolated**, already-migrated database and
`TEST_DATABASE_URL=postgresql+psycopg://...`. They insert test fixtures inside rolled-back
transactions. Never point tests at production. Without that variable the DB test is skipped.
See [development guide](docs/development-guide.md) for creating a test database.

Common problems:

- "Directory ... does not contain a Gradle build": the Gradle project is in `android/`.
  Close the current project, choose **File > Open**, and select `ChineseLearningApp/android`.
  If keeping the repository root open, link `android/settings.gradle.kts` from the Gradle
  tool window and unlink any Gradle project pointing at the repository root. Do not run
  `gradle init`; the Android build already exists. From a root terminal, run
  `.\android\gradlew.bat -p android assembleDebug`.
- Docker named-pipe errors: start Docker Desktop, select Linux containers, retry Compose.
- Port 5432 occupied: change `POSTGRES_PORT` in root `.env` and backend connection URL.
- Database password errors after editing `.env`: existing volumes keep their original
  credentials. Change the database role password deliberately rather than deleting data.
- Android unavailable status: check FastAPI, host firewall, URL, and emulator/device routing.
- Gradle/JDK errors: open `android/`, use JDK 21, install SDK 36, check network/proxy access
  to Google Maven, Maven Central and Gradle distribution services.
- Migrations fail: check database URL, run Compose health checks and inspect
  `docker compose logs postgres`. Never replace Alembic with application `create_all()`.

Design: [architecture](docs/architecture.md), [schema](docs/database-design.md),
[API conventions](docs/api-conventions.md), [Google setup](docs/authentication.md),
[offline plan](docs/offline-sync.md). Validation evidence is in [validation](docs/validation.md).
Next development slice: authenticated sessions with verified Google identity, tested
ownership enforcement and account-isolated local storage, before any user progress API.
