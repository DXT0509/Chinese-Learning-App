# Phase 3: Vocabulary Lesson Player MVP

Home → **Bắt đầu học** → opt in to preview content → choose **你 — bạn**, version 2 →
start/resume → player. Existing runs can also be opened from the saved runs list.
The server resumes the newest existing run for the same identity and exact lesson version.
Starting twice, including with different request UUIDs, does not create another run.
Legacy duplicate runs remain accessible rather than being deleted. Requests are serialized
with a PostgreSQL user-row lock; checkpoint writes lock their run row.

The bundle remains `CONTENT_PREVIEW`: Phase 3 adds Android scene interaction, without
introducing evidence of completion. `learning_completion_supported` stays false. Version 1
files and published objects remain unchanged. The new lesson version uses template version 2.
Both versions can coexist; an older run continues using its original bundle.

## Supported content

| Scene | Android behavior |
| --- | --- |
| `VOCABULARY_INTRODUCTION` | Hanzi, pinyin, Hán Việt, meaning when `show_meaning` permits it, optional audio |
| `VOCABULARY_INFORMATION` | Only configured fields: pinyin, Hán Việt, meaning, part of speech, notes |
| `CHARACTER_ANALYSIS` | Ordered character pages, or one reviewed component per page when configured; explicit unreviewed placeholder otherwise |
| `STROKE_ANIMATION` | Ordered character pages; referenced image/GIF when available, explicit placeholder otherwise |
| `HANDWRITING_PRACTICE` | Finger drawing canvas with clear/reset; normalized strokes survive scene changes and activity recreation |

The sample has **no reviewed component breakdown, audio, stroke count or stroke-order asset**.
No instructional media or decomposition is invented. A supplied stroke-order asset reference
must be reviewed during local content authoring. GIF animation uses the platform decoder on
Android 9+; older Android versions display the first frame. Audio uses MediaPlayer with
asynchronous preparation. Invalid/unavailable assets display a Vietnamese fallback.
Assets are fetched by ID through an authenticated, bundle-scoped route, never by executing
a storage key or a bundle-provided URL. The server verifies their SHA-256 and byte length.

`LISTENING_TRANSCRIPTION`, `SENTENCE_TRANSLATION`, unknown scene types and future contract
versions display an unsupported-content state with navigation available. No speech scoring,
recognition, translation evaluation, SRS, EXP, review, roadmap or offline sync is implemented.
Detailed component authoring remains deferred. An analysis config can explicitly request
`pagination: ONE_COMPONENT_PER_PAGE`; the mapper splits supplied reviewed components into
subpages. Missing component data yields a safe placeholder instead. Legacy configs without
this field continue to show one page per ordered character.

## Persistence and errors

The additive migration `0004_vocabulary_player` adds nullable `lesson_runs.current_scene_key`
and extends the scene-type check constraint. Existing bookmarks are retained; older runs
with no cursor open at their first scene because their original checkpoint history did not
record chronology. No arbitrary guess about the last visited scene is made.

Opening a run saves its displayed scene. Previous/Next saves the **destination** scene key
and zero-based subpage before changing the screen. Back/Exit saves the current position
before popping the player. Backgrounding attempts the same save; every displayed position
has already been saved by entry/navigation. The server updates the scene bookmark and run
cursor in one transaction. Resume uses that cursor, including backward navigation, and
clamps stale subpages to the available pages. The API's legacy page bound remains 0–10000;
it is a bookmark, not assessment evidence.

A save failure keeps the current scene, offers retry, and blocks successful exit until a
save succeeds. Retry saves the displayed position; press Continue again to move onward.
If a response is lost after the server commits, resuming uses the committed server cursor.
Empty/missing bundles, network errors and unsupported scenes have separate visible states.
Rejected session refresh returns through existing session restoration to Login; temporary
network failures preserve credentials. Logout/account changes clear private player state.

Scene/subpage bookmarks survive process death and app reopening through PostgreSQL.
Drawing strokes and media are temporary ViewModel state: they survive rotation and scene
changes but are cleared when opening another run, signing out or losing the process.
After process recreation, a restored player route without in-memory content returns to
the catalog; selecting its saved run restores the server cursor. Nothing awards completion,
EXP or mastery, and legacy learning/SRS tables are untouched.

## API changes

All routes require the existing bearer session and live under `/api/v1`.

| Method and route | Change |
| --- | --- |
| `GET /lessons` | Existing published catalog; version 2 appears after explicit publication |
| `POST /learning-runs` | Existing request shape; now resumes the same owner's existing version-pinned run |
| `GET /learning-runs` and `GET /learning-runs/{id}` | Add nullable `current_scene_key`; retain scene checkpoints |
| `GET /lesson-versions/{id}/bundle?allow_preview=true` | Existing immutable content contract; new scene configurations supported |
| `PUT /learning-runs/{id}/scenes/{key}` | Existing `{page}` input; atomically update bookmark and latest cursor |
| `GET /lesson-versions/{id}/assets/{asset_id}` | New authenticated, preview-gated asset read; only assets in that bundle |

Foreign runs and scenes/assets outside the selected bundle return 404. Auth APIs are unchanged.
The client and server still require explicit preview opt-in. The final action says save/exit,
never lesson completed.

## Native Windows PostgreSQL and physical Android over USB

Use the existing Windows PostgreSQL service and development database. No Docker is required.
Create a development database in pgAdmin only if one does not already exist. Configure its
real credentials in ignored `backend/.env`, using `postgresql+psycopg://...`; do not paste
credentials into tracked files. These commands start at the repository root.

```powershell
cd backend
if (!(Test-Path .env)) { Copy-Item .env.example .env }
# Edit .env: DATABASE_URL points to your existing local development database.
# First setup only, if .venv does not exist:
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements-dev.lock
.venv\Scripts\python -m pip install --no-deps -e .

.venv\Scripts\python -m alembic upgrade head
.venv\Scripts\python -m scripts.validate_content --content-dir content
.venv\Scripts\python -m scripts.import_content --content-dir content
# Publish version 2 ONCE. Skip this command if version 2 is already published.
.venv\Scripts\python -m scripts.publish_lesson --lesson lesson-ni --version 2 --storage-dir .content-storage
.venv\Scripts\python -m scripts.inspect_bundle --lesson lesson-ni --version 2 --storage-dir .content-storage
$env:ALLOW_CONTENT_PREVIEW = 'true'
.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --no-access-log --loop app.core.event_loop:new_event_loop --log-config logging.json
```

If `.venv` already exists, use it rather than recreating it. Restart an existing backend
after upgrading. Keep the API running in that terminal. In another PowerShell terminal,
starting from the repository root, connect an unlocked USB-debuggable phone and accept its
computer authorization prompt:

```powershell
$adb = "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe"
& $adb devices -l
& $adb -d reverse tcp:8000 tcp:8000
& $adb -d reverse --list
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health
cd android
.\gradlew.bat installDebug '-PDEV_API_BASE_URL=http://127.0.0.1:8000/'
& $adb -d shell am start -n com.example.chineselearningapp/.MainActivity
```

If the SDK is elsewhere, adjust `$adb`. With multiple devices, select the target serial.
Repeat reverse after reconnecting USB. Debug uses `http://127.0.0.1:8000/`; release continues
to require HTTPS. Rebuild/install after Kotlin/resources changes. Backend-only edits need
reload/restart; content changes require a new version and explicit publication.

Manual acceptance: log in → Home → Bắt đầu học → preview consent → version 2 → step through
introduction, information, analysis placeholder, stroke placeholder and handwriting → draw,
clear and draw again → go backward → save/exit → reopen the saved run → verify the same
scene/subpage → restart the app and repeat. Rotate while drawing to verify temporary ink
retention. Disconnect the API during navigation to verify the save error and retry behavior.
Use another account to verify that the original run is inaccessible.

## Verification

```powershell
cd backend
.venv\Scripts\python -m ruff check .
.venv\Scripts\python -m ruff format --check .
# Set TEST_DATABASE_URL to an isolated database already upgraded to head.
# Set MIGRATION_TEST_DATABASE_URL to a different fresh empty database for one rehearsal.
.venv\Scripts\python -m pytest -q
# DATABASE_URL must select the isolated migrated test database for this check:
.venv\Scripts\python -m alembic check
cd ../android
.\gradlew.bat testDebugUnitTest assembleDebug lintDebug
```

The migration rehearsal refuses existing tables and retains its fixtures. Never reset or
downgrade a shared database to repeat it. Unit/API/build checks do not establish physical
device behavior. See the [Phase 3 implementation report](phase3-implementation-report.md) for actual results.

Recommended next phase: author reviewed character/component and media content, validate the
full USB-device experience, then specify an explicit completion/evaluation contract before
adding any graded learning or rewards.
