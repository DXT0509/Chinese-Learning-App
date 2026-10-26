# Phase 3.4 — Personal vocabulary collection

Implemented 2026-10-22. Authenticated users can save an exact dictionary entry,
browse/search their collection, reopen dictionary detail and remove the association.
No curriculum completion, EXP, TEACHES eligibility, SRS scheduling or mastery is granted.

## Persistence and identity

Revision `0007_personal_vocabulary` follows `0006_dictionary_enrichment`; previous
revisions are unchanged. `personal_vocabulary_entries` contains:

| Column | Purpose |
| --- | --- |
| `id` | Association UUID |
| `user_id` | Required users FK, cascading only on account deletion |
| `dictionary_entry_id` | Exact dictionary UUID, RESTRICT deletion |
| `source_revision_at_save` | Original revision label |
| `saved_snapshot` | Small immutable-at-API-level saved-time JSONB snapshot |
| `saved_at` | Timezone-aware server timestamp |

Unique `(user_id, dictionary_entry_id)` prevents duplicates. The `(user_id, saved_at, id)`
B-tree supports owner listing and cursor ordering. The association has no update operation,
so an `updated_at` field would add no useful information. Remove/re-save creates a new
association and snapshot. Foreign keys preserve canonical references.

The existing `user_vocabulary` represents catalog/custom vocabulary with a learned timestamp;
`srs_states.user_vocabulary_id` cascades from it. Repurposing it would mix private bookmarks
with learning history. All existing models and records are preserved. A read-only inspection
of the local development DB found 0 user vocabulary rows, 0 SRS rows, 1 curriculum vocabulary
row and 125,303 dictionary entries. This observation does not change the semantic separation.

Saving uses PostgreSQL INSERT ON CONFLICT with a no-op ID update and RETURNING. This returns
and locks the winning association without changing its timestamp or snapshot, even if two
devices save concurrently. The source entry/import are share-locked while taking the snapshot.
The service owns the transaction. Concurrent removal cannot delete the returned association
before the save transaction finishes; a later removal naturally wins after that point.

## Dictionary revisions, snapshots and language coverage

Dictionary UUIDs remain canonical. Identical Hanzi with different source lexical identities
remain separate saved entries. There is no Hanzi-based redirection or inferred sense mapping.
Inactive entries can still be saved, listed and opened by exact UUID, and the UI labels them.

A minimal snapshot is justified because later imports may revise definitions. It retains
forms, citation/numbered Pinyin, language-keyed English glosses, source/import identity,
revision, source/license URLs, attribution and modification notice. It contains no character
annotations, binaries, examples, audio or unrelated learning data. Duplicate saves leave the
snapshot unchanged. Normal cards/detail show the latest retained canonical entry; the API
also returns saved-time evidence. A historical-definition viewer is not implemented.

The current source has no verified lexical Vietnamese coverage. `short_vi_meaning` is null;
cards use the first stored English gloss, explicitly labeled English. Character-level
Vietnamese notes remain separate in the reused detail screen. No translation is synthesized.
Existing CC-CEDICT attribution/license controls remain in dictionary detail. Revision strings,
internal IDs and checksums are not displayed in normal wordbook UI.

## Authenticated API

All paths below require the existing Bearer session and are under `/api/v1/me/vocabulary`.
Ownership always comes from authentication; the save body forbids extra fields such as user_id.
Existing no-store middleware, generic errors and session revocation apply.

| Method | Suffix | Result |
| --- | --- | --- |
| POST | empty | `{dictionary_entry_id: UUID}` → 200 saved association, including duplicate saves |
| GET | empty | `{items, total, next_cursor}`; total is the matching owner-scoped count |
| GET | `/status?dictionary_entry_id=UUID` | `{saved_id: UUID or null}` |
| GET | `/{saved_id}` | Saved association and exact dictionary UUID; 404 for absent/foreign IDs |
| DELETE | `/{saved_id}` | 204 for removed, already absent, or foreign IDs; no ownership disclosure |

An unknown dictionary UUID on save returns 404. Malformed UUID/query/body returns 422;
missing/expired/revoked authentication returns 401. Status is an association lookup: unknown
dictionary UUIDs have null saved_id. DELETE touches only the authenticated owner's association.

Listing accepts `q` (0–64 Unicode code points), `limit` (1–50, default 20) and optional
`cursor` (maximum 160 characters). Query normalization matches the dictionary's Unicode
policy and rejects control/format characters. Literal, case-insensitive substring matching
covers simplified/traditional forms and tone-marked or numbered Pinyin. `%` and `_` are
escaped; SQL parameters are bound. Toneless Pinyin and fuzzy search are not promised.

Ordering is descending `(saved_at, id)`. The cursor encodes this tuple; it is not an
authorization credential and cannot bypass the owner filter. Keyset pagination has no
1000-item cutoff and remains valid when the boundary row is removed or newer rows are saved.
Each page fetches at most limit+1 rows. Counts and pages reflect live data, not an immutable
multi-request snapshot. Search scans the owner's indexed collection and joins dictionary PKs;
it is not full-dictionary search. No additional global trigram index is introduced.

## Android behavior

Learning offers both dictionary search and **Từ vựng của tôi**. The existing Vocabulary
detail destination now renders MyVocabularyScreen; the four bottom tabs are unchanged.
Profile remains the sole logout entry point.

Hilt supplies PersonalVocabularyRepository through the shared Retrofit/client and existing
RemoteSessionRepository.authorized path. Refresh/retry and rejected-session cleanup are
reused. There is no private Room cache, plain credential preference, second session manager,
new dependency or offline queue.

Dictionary detail has an independent SavedEntryViewModel so status/save failures preserve
selected detail. Status must succeed before Save is enabled. Loading disables duplicate taps;
only confirmed backend success shows the saved state. Failure offers retry/status reconciliation,
which also resolves a response lost after a successful server commit.

The wordbook has real matching counts, debounced search, stable card keys, load-more,
empty/explore, error/retry, inactive notices, English labels and confirmed removal. Removal
failure retains the item and confirmation dialog. Query is in SavedStateHandle; list/scroll
state survives ordinary Back. Returning from detail refreshes the previously loaded window.
Process restoration refetches data. Navigation away cancels ViewModel-owned requests when
the back-stack entry is destroyed. The identity-keyed graph discards private state on logout.

## Apply to the existing native PostgreSQL database

No development migration, reimport, correction, reset or data write was performed during
this phase. Use the existing ignored `backend/.env` and its native PostgreSQL credentials.
In a fresh PowerShell terminal, from repository root:

```powershell
cd backend
# Confirm no shell DATABASE_URL is overriding the intended .env configuration.
.venv\Scripts\python -m alembic current
.venv\Scripts\python -m alembic history
# After reviewing revision 0007 and taking the normal database backup:
.venv\Scripts\python -m alembic upgrade head
.venv\Scripts\python -m alembic check
.venv\Scripts\python -m app
```

Startup never runs migrations. Existing dictionary data is reused; do not reimport the
dictionary to enable this feature. Downgrade deliberately refuses to drop private collections
without a reviewed retention plan. Roll back application code independently if necessary.

## Verification

Backend: **152 passed, zero skipped**, including real independent-transaction concurrent
saves/removals, authenticated ownership, exact identities, pagination/search, snapshots,
inactive entries, no mutation of seeded completed lessons/learned words/SRS state, and all
four nonempty migration rehearsals. Ruff lint/format passed (81 files). Alembic check found
no new operations. Existing Starlette TestClient and SQLAlchemy reflection warnings remain.
No EXP implementation exists; the service writes only its association table and tests compare
all pre-existing tables for unintended changes.

Test execution used the isolated PostgreSQL 18 cluster on port 55432. Reproduction commands
below require fresh rehearsal database names; retain fixtures and never reset an old rehearsal:

```powershell
# Repository root, only if the isolated cluster is stopped:
$pgBin = 'C:/Program Files/PostgreSQL/18/bin'
& "$pgBin/pg_ctl.exe" start -D backend/.test-postgres-slice2-20261018 -l backend/.wordbook-postgres.log -o '-h 127.0.0.1 -p 55432' -w
# Create new databases with createdb; use a new suffix on subsequent rehearsals.
& "$pgBin/createdb.exe" -h 127.0.0.1 -p 55432 -U slice2 wordbook_test_NEW
& "$pgBin/createdb.exe" -h 127.0.0.1 -p 55432 -U slice2 wordbook_legacy_NEW
& "$pgBin/createdb.exe" -h 127.0.0.1 -p 55432 -U slice2 wordbook_dictionary_NEW
& "$pgBin/createdb.exe" -h 127.0.0.1 -p 55432 -U slice2 wordbook_enrichment_NEW
& "$pgBin/createdb.exe" -h 127.0.0.1 -p 55432 -U slice2 wordbook_upgrade_NEW
cd backend
$env:DATABASE_URL = 'postgresql+psycopg://slice2@127.0.0.1:55432/wordbook_test_NEW'
$env:TEST_DATABASE_URL = $env:DATABASE_URL
$env:MIGRATION_TEST_DATABASE_URL = 'postgresql+psycopg://slice2@127.0.0.1:55432/wordbook_legacy_NEW'
$env:DICTIONARY_MIGRATION_TEST_DATABASE_URL = 'postgresql+psycopg://slice2@127.0.0.1:55432/wordbook_dictionary_NEW'
$env:ENRICHMENT_MIGRATION_TEST_DATABASE_URL = 'postgresql+psycopg://slice2@127.0.0.1:55432/wordbook_enrichment_NEW'
$env:WORDBOOK_MIGRATION_TEST_DATABASE_URL = 'postgresql+psycopg://slice2@127.0.0.1:55432/wordbook_upgrade_NEW'
.venv\Scripts\python -m alembic upgrade head
.venv\Scripts\python -m pytest -q
.venv\Scripts\python -m ruff check .
.venv\Scripts\python -m ruff format --check .
.venv\Scripts\python -m alembic check
# Close this terminal afterward so test database overrides are not reused for development.
```

Actual final database suffixes were `wordbook_test_20261022`,
`wordbook_legacy_final_20261022`, `wordbook_dictionary_final_20261022`,
`wordbook_enrichment_final_20261022` and `wordbook_upgrade_final_20261022`.

Android commands, from repository root:

```powershell
cd android
$env:JAVA_HOME = 'C:\Program Files\Android\Android Studio\jbr'
.\gradlew.bat testDebugUnitTest assembleDebug lintDebug assembleDebugAndroidTest
```

Android: **67 unit tests passed**; `assembleDebug`, `lintDebug` and
`assembleDebugAndroidTest` passed. Nine new unit tests cover ViewModel and authenticated
repository behavior. Four new UI instrumentation tests are compiled, not device-executed. No physical-device or emulator
validation is claimed. Backend tests use explicitly synthetic fixtures only; production
screens have no synthetic fallback. Repository tests use MockWebServer, not a deployed API.

## Physical-device checklist (not performed)

1. Apply the migration explicitly as above, restart the backend, and follow
   [USB development](android-usb-development.md) for API_BASE_URL and `adb reverse tcp:8000 tcp:8000`.
2. `cd android; .\gradlew.bat installDebug`. Log in with a real account. Open Learning,
   dictionary search, type or handwrite Chinese, select a specific entry and tap Save.
   Check loading, success and a disabled saved button without losing detail.
3. Open My Vocabulary. Check simplified/traditional/Pinyin and the English label. Search
   by both forms and numbered/tone-marked Pinyin. Save two same-Hanzi entries with distinct
   IDs and verify independent saved states. Use enough real entries to test Load more.
4. Open a saved detail and go Back: query, loaded window and scroll should remain useful.
   Rotate; restart the app; log out from Profile and log in again. Confirm persistence.
   Log in as a second user and confirm the first collection is not exposed.
5. Cancel removal, then confirm it. Verify shared dictionary detail still exists. Repeat
   save/remove from a second session; verify duplicates never appear. Disconnect network
   during save/remove and retry; failed requests must never show unconfirmed success.
6. Test refresh success and expired/rejected refresh returning to login. In an isolated
   fixture environment, mark a source entry inactive and verify its retained detail/card
   notice. Do not alter the real imported dictionary merely for this test.
7. Run `.\gradlew.bat connectedDebugAndroidTest -Pandroid.testInstrumentationRunnerArguments.class=com.example.chineselearningapp.PersonalVocabularyUiTest`
   on the connected device/emulator. Tests cover empty/explore, exact-entry navigation,
   saved-button states, removal confirmation and Back/query restoration.

## Files

New backend files: `app/models/personal_vocabulary.py`, `app/schemas/personal_vocabulary.py`,
`app/services/personal_vocabulary.py`, `app/api/v1/endpoints/personal_vocabulary.py`,
`alembic/versions/0007_personal_vocabulary.py`, and the two `tests/test_personal_vocabulary*.py`
files. Model registration and API router are updated.

New Android files: `core/network/PersonalVocabularyApi.kt`,
`domain/repository/PersonalVocabularyRepository.kt`,
`feature/vocabulary/data/RemotePersonalVocabularyRepository.kt`,
`feature/vocabulary/PersonalVocabularyViewModel.kt`, `feature/vocabulary/MyVocabularyScreen.kt`,
`res/values/wordbook_strings.xml`, two PersonalVocabulary unit-test classes and
`PersonalVocabularyUiTest.kt`. MainActivity, AppModule, MainNavigation, SessionNavigation,
LearningScreen, DictionaryScreens and dictionary DTO/model/mapping integrate the feature.

Documentation: this design, database-design, mvp-implementation-plan, development-guide
and api-conventions. No dependency versions, previous migrations, handwriting engine,
curriculum publication or lesson player behavior were changed.
