# Chinese Learning App

Android app for Vietnamese-speaking Chinese beginners, with a FastAPI/PostgreSQL backend.
This repository contains infrastructure, a health connectivity demo, Slice 1 local
content authoring and Slice 2 email/password sessions and preview runs. Published
CONTENT_PREVIEW bundles do not implement executable lessons.

## Boundaries and directories

- `android/`: one Gradle app module, Kotlin, Compose, Material 3, Hilt, Room, Retrofit.
- `android/app/src/main/java/com/example/chineselearningapp/core/`: platform infrastructure.
- `domain/`: framework-free models and repository contracts. Add use cases only for real logic.
- `feature/`: screens, ViewModels, feature data implementations as needed.
- `backend/app/api/`: HTTP routing; `schemas/`: wire contracts; `models/`: SQLAlchemy persistence.
- `backend/app/dependencies/`: request-scoped resources. Add `repositories/` for concrete queries,
  `services/` for business operations when a feature needs them; do not add empty base classes.
- `backend/alembic/`: reviewed, immutable migration history. `docs/`: design and setup decisions.

## Coding and dependencies

- Use descriptive names, small functions, constructor injection and existing conventions.
- Keep Android versions in `android/gradle/libs.versions.toml`. AGP 9 supplies Kotlin;
  do not add the legacy Kotlin Android plugin. Match the Compose compiler plugin to Kotlin.
- Keep Python dependency constraints in `pyproject.toml`; refresh `requirements-dev.lock`
  and verify dependencies when changing them. The lock captures the tested dev environment.
- No feature Gradle modules, generic repositories, speculative use cases or sync frameworks.
- Preserve unrelated user edits. Never commit credentials, environments or generated builds.

## Android rules

- Composables render state and forward events; never access Retrofit or Room directly.
- ViewModels expose immutable StateFlow and preserve coroutine cancellation.
- Repositories map transport/database types into domain models. Domain code imports no Android APIs.
- Use lifecycle-aware collection and resources for UI text; Vietnamese is the default.
- Export Room schemas; add explicit migrations. Never enable destructive migration fallback.
- Debug can use HTTP for local development. Release must require HTTPS and block cleartext.
- DataStore holds non-sensitive preferences. Never place session credentials in plain preferences.
- User-specific Room tables must be scoped by identity; public catalog cache is separate.

## Backend and database rules

- Use async SQLAlchemy sessions with psycopg consistently. No blocking DB calls in async routes.
- Services own transactions; repositories do not silently commit. Always close sessions.
- All API features live under `/api/v1`; `/health` is a liveness alias only.
- Validate input with Pydantic. Return generic errors; do not log payloads, tokens, SQL or secrets.
- Email/password is the MVP identity method. Never add fake login or unauthenticated progress APIs.
- Google linking is deferred until pre-release; use official verification and stable `sub`
  when implemented, and never automatically merge accounts by matching unverified email.
- Alembic is the only schema deployment mechanism. Never call `create_all()` at application startup.
- Add new revisions for schema changes; inspect generated migrations for data loss.
- Author public drafts through the strict JSON contracts and local scripts documented in
  `docs/content-authoring.md`. Never edit published versions; corrections use new versions.
- Preserve unversioned legacy lesson links and media keys. Never infer TEACHES provenance.
- Never reset a database, downgrade shared environments, or remove Docker volumes casually.
- Use timezone-aware UTC timestamps; enforce important integrity rules in PostgreSQL.

## Adding and verifying features

1. Define a small user-visible slice and contract; update design docs when behavior changes.
2. Add domain models/contracts only as needed, then data implementation, ViewModel and UI.
3. Add authenticated API, services/queries and migration only if required by that slice.
4. Test meaningful behavior and error paths. Backend: `.venv/Scripts/python -m pytest`.
   Android: `gradlew.bat testDebugUnitTest assembleDebug lintDebug` from `android/`.
5. Test migration upgrades and `alembic check` against an isolated PostgreSQL database.
6. Report executed checks honestly. Do not claim emulator or device validation from unit tests.

The nonempty migration rehearsal requires a fresh empty `MIGRATION_TEST_DATABASE_URL`;
it refuses existing tables, leaves its fixtures intact and never resets or downgrades.

Read `docs/architecture.md`, `docs/development-guide.md`, and `docs/authentication.md`
before expanding architecture, synchronization or identity handling.
