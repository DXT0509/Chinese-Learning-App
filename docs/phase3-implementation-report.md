# Phase 3 implementation report

The Android vocabulary preview is now interactive: authenticated users can opt into the
sample, start/resume its pinned run, navigate five scene types, draw and return to the
server-saved position. Apply migration 0004 and publish the new version 2 before using it.
The personal development database and physical device were not changed during this work.

## Android implementation

- `LessonPlayerViewModel`: loading/content/error state, start/resume, serialized checkpoint
  actions, session expiry, identity isolation, temporary normalized handwriting strokes and media.
- `LessonBundleMapper` and framework-free domain models: only known contracts become typed
  scene content; unsupported types/config versions stay visibly unsupported.
- `LessonPlayerScreen`, `SceneBody`, `Field`, `HandwritingCanvas`, `AssetMedia`, `AudioButton`:
  focused mint/white Material 3 layout, progress, character/component subpages, previous/next,
  save/exit, placeholders, drawing/reset, optional audio and image/GIF rendering.
- `PreviewLessonsScreen`: existing consent/catalog and saved-run entry point; obsolete
  bookmark-counter UI removed. Protected Navigation Compose graph adds the player route.
- Existing session repository/Retrofit authorization and refresh remain the transport boundary.
  Login/logout and protected account transitions keep their existing contracts.

Supported: VOCABULARY_INTRODUCTION, VOCABULARY_INFORMATION, CHARACTER_ANALYSIS,
STROKE_ANIMATION and HANDWRITING_PRACTICE. Listening/transcription and translation execution
remain unsupported. Missing reviewed sample analysis/media have explicit placeholders.

## Backend and checkpoint changes

Existing catalog/bundle endpoints remain. Run POST now reuses an existing run for the exact
owner/version, with PostgreSQL locking to serialize concurrent starts. Run GET/list and
checkpoint PUT add `current_scene_key`. Checkpoint PUT validates membership and saves both
the cursor and scene subpage in one transaction. A new authenticated
`GET /api/v1/lesson-versions/{version_id}/assets/{asset_id}` serves only verified objects
listed in that pinned bundle. Preview gates remain in effect.

Revision `0004_vocabulary_player` preserves every existing row, adds the cursor and extends
the finite scene-type constraint. New template and lesson version 2 add the first full MVP
flow; published version 1 stays untouched. No dependencies or legacy learning/SRS data change.

Opening, moving, backgrounding and exiting save scene/subpage position. Navigation/exit
wait for successful writes; failure keeps the screen visible and permits retry. Server
bookmarks survive process death. Ink/media survive rotation but remain temporary and are
cleared for a new run, logout or process loss. A restored route without memory returns to
the catalog, from which the saved run resumes. There is no completion status or reward.

## Verification

Backend final suite: **77 passed, 1 skipped**. The skipped nonempty migration rehearsal was
executed separately against a fresh empty PostgreSQL database and **passed**; its fixtures
remain intact. `alembic upgrade head` and `alembic check` passed on the isolated regular test
database; Alembic reports no new upgrade operations. Ruff check and format check passed.
The existing Starlette deprecation and SQLAlchemy reflection warnings remain.

The isolated regular database is `phase3_test_20261018`, and the successful retained upgrade
rehearsal database is `phase3_upgrade_20261018_02`, on the local test cluster at port 55432.
No shared database was reset, downgraded or cleared.

Android final command: `gradlew.bat testDebugUnitTest assembleDebug lintDebug compileDebugAndroidTestKotlin`.
Result: **BUILD SUCCESSFUL**, **33 unit tests passed**, no skipped/failed tests. Debug APK
assembled; navigation/auth instrumentation sources compiled. Lint: **0 errors, 40 warnings**
(dependency update notices and unused resources). Final `git diff --check` passed.

Backend commands used `.venv/Scripts/python -m pytest -q --tb=short` with a unique local
`--basetemp=.pytest-phase3-04 -p no:cacheprovider` to avoid Windows temp/cache permission
conflicts. `TEST_DATABASE_URL` selected only the fresh isolated test database. The separate
migration run used a fresh `MIGRATION_TEST_DATABASE_URL`; subsequent suite runs omitted it
to preserve the rehearsal fixtures rather than attempting to reuse a nonempty database.

Physical device/emulator execution was **not performed**. Existing navigation instrumentation
sources were compiled; compilation does not establish runtime UI/device behavior. Auth unit
and API regression tests are included in the executed suites.

## Running and remaining work

[Full exact Windows/physical-device commands and manual acceptance checklist](vocabulary-player.md#native-windows-postgresql-and-physical-android-over-usb)
cover native PostgreSQL, migration, content import/publication, FastAPI, ADB reverse,
`installDebug` and launching the app at `http://127.0.0.1:8000/`. Docker is not required.

The sample has no reviewed audio/stroke/component assets. Detailed component authoring,
completion, EXP, SRS, grading, recognition, speech evaluation, review and offline sync stay
deferred. GIFs animate on Android 9+; earlier devices use a static first frame. Legacy
runs without a cursor start at their first scene because chronology cannot be recovered.

Recommended next phase: review and author real teaching/media content, complete physical
USB-device acceptance, then define the explicit completion/evaluation contract.

## Files changed

- `.gitignore`
- `android/app/src/main/java/com/example/chineselearningapp/MainActivity.kt`
- `android/app/src/main/java/com/example/chineselearningapp/core/navigation/SessionNavigation.kt`
- `android/app/src/main/java/com/example/chineselearningapp/core/network/SessionApi.kt`
- `android/app/src/main/java/com/example/chineselearningapp/domain/model/LessonPlayer.kt`
- `android/app/src/main/java/com/example/chineselearningapp/domain/repository/SessionRepository.kt`
- `android/app/src/main/java/com/example/chineselearningapp/feature/auth/data/RemoteSessionRepository.kt`
- `android/app/src/main/java/com/example/chineselearningapp/feature/lesson/LessonPlayerScreen.kt`
- `android/app/src/main/java/com/example/chineselearningapp/feature/lesson/LessonPlayerViewModel.kt`
- `android/app/src/main/java/com/example/chineselearningapp/feature/lesson/PreviewLessonsScreen.kt`
- `android/app/src/main/java/com/example/chineselearningapp/feature/lesson/README.md`
- `android/app/src/main/java/com/example/chineselearningapp/feature/lesson/data/LessonBundleMapper.kt`
- `android/app/src/main/res/values/lesson_strings.xml`
- `android/app/src/test/java/com/example/chineselearningapp/LessonBundleMapperTest.kt`
- `android/app/src/test/java/com/example/chineselearningapp/LessonPlayerViewModelTest.kt`
- `android/app/src/test/java/com/example/chineselearningapp/SessionRepositoryTest.kt`
- `backend/alembic/versions/0004_vocabulary_player.py`
- `backend/app/api/v1/endpoints/learning.py`
- `backend/app/models/content.py`
- `backend/app/models/session.py`
- `backend/app/schemas/content.py`
- `backend/app/schemas/session.py`
- `backend/app/services/learning_access.py`
- `backend/content/lessons/lesson-ni.v2.json`
- `backend/content/templates/vocabulary-v2.json`
- `backend/tests/test_content_files.py`
- `backend/tests/test_content_postgres.py`
- `backend/tests/test_sessions.py`
- `docs/android-usb-development.md`
- `docs/architecture.md`
- `docs/authentication.md`
- `docs/development-guide.md`
- `docs/vocabulary-player.md`
- `docs/phase3-implementation-report.md` (this report)
