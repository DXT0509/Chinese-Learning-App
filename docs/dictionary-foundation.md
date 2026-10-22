# Phase 3.1 — Dictionary foundation

Phase 3.1.1 adds [verified revision repair and Vietnamese character enrichment](dictionary-vietnamese-enrichment.md).
Its documentation supersedes the manual revision-label examples and English-only detail
metadata description below. Search lexical fields still have English-only coverage.
New CC-CEDICT imports should omit `--revision` and use the verified header/hash default.
Only the explicit audited maintenance command can correct an existing label while retaining
its original import identity; ordinary source revision contents remain immutable.

Implemented backend lookup only. No Android changes, handwriting recognition, wordbook
writes, lesson completion, EXP, SRS or curriculum publication changes are part of this slice.
Source selection and verified licensing are in [source evaluation](dictionary-source-evaluation.md).

## Source and data limits

The importer accepts manually acquired CC-CEDICT **v1** UTF-8 text or gzip, after verifying
its license notice. Production data is not bundled or installed by application startup.
Acquire the offered dataset from [MDBG](https://www.mdbg.net/chinese/dictionary?page=cedict)
using the browser; retain its header/notices and record the release date and checksum.
Do not scrape the site's search interface or automate website access. Current selected
license is [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); inspect the
actual artifact, since historic copies may have different notices. Preserve attribution,
license links, change notices and share-alike obligations when redistributing adaptations.

Chinese forms, pronunciation and ordered English glosses are sourced fields. Tone-marked
pinyin is a deterministic rendering of numbered citation pinyin, without sandhi inference.
Original numbered pinyin remains available, including source case and punctuation.
Meanings are language-keyed; MVP has only `en`. `short_vi_meaning` and `sino_vietnamese`
are null. POS, reviewed examples and audio are empty arrays. No English gloss is relabeled
Vietnamese, and no character-reading concatenation or LLM translation supplies missing data.
Glosses can contain source labels, classifier references and cross references as text;
these are not parsed into verified POS, examples, or semantic links.

The fixture at `backend/tests/fixtures/dictionary/cedict-test.u8` contains ten synthetic
entries for format/behavior tests. Its definitions deliberately say "test". It is not a
dictionary release. The benchmark generates artificial headwords; never import those into
a user-facing database or represent their provenance as an actual CC-CEDICT release.

## Schema and service boundary

Revision `0005_dictionary_foundation` follows the existing `0004_vocabulary_player`.
Revisions 0001–0004 are unchanged. Two new shared tables:

| Table | Role |
| --- | --- |
| `dictionary_imports` | Immutable source/revision key, exact artifact SHA-256, source/license URLs, attribution, transformation notice, entry count and timezone-aware UTC import timestamp |
| `dictionary_entries` | Stable UUID, source, latest-seen import FK, both forms, numbered/rendered pinyin, ordered English glosses in JSONB, searchable `active` flag |

Existing `vocabulary` requires Vietnamese meaning and represents authored curriculum.
`characters` has unique character text and reviewed/media metadata, not lexical identity.
`vocabulary_characters` describes authored positions. `user_vocabulary` owns private catalog
or custom data. `assets` participates in immutable publication/media. None can safely hold
unreviewed external dictionary entries with different licensing and optional Vietnamese.
They are all preserved; this slice adds no cross-links or per-user dictionary copies.

Entry UUIDv5 uses a fixed namespace and JSON `[source, traditional, simplified,
pinyin_numbered]`, normalized to NFC with pinyin whitespace collapsed and case preserved.
Do not change this identity algorithm for the same source. Different readings are separate
entries; glosses stay ordered within their source reading. Conflicting rows with the same
lexical key abort import rather than merging unverified senses. Definitions and revision
do not enter the ID. A source correction to a headword/reading creates a new ID; never
silently redirect an old saved reference based on Hanzi alone.

Each import atomically publishes one source snapshot under a PostgreSQL advisory transaction
lock. New/changed entries upsert by ID in batches of 500. Missing entries become inactive,
remain retrievable by ID with last-seen provenance, and leave suggestions. Repeating the
current identical artifact/revision is a no-op; changing bytes under the same revision or
replaying a superseded revision is rejected. Use a new revision for a deliberate source
rollback. Old import metadata remains, but this is **not** a full historical definition store:
an entry detail contains the latest seen definition. Preserve downloaded artifacts externally
if historical reconstruction is required. No dictionary or curriculum rows are deleted.

Acquisition is manual; `services/cedict.py` parses/normalizes; `dictionary_import.py` owns
write transactions; `repositories/dictionary.py` owns queries; `DictionaryService` maps
domain behavior to Pydantic contracts. Request-scoped sessions and existing identity
dependencies are reused. There is no generic provider framework or external runtime call.

## HTTP contracts

Both routes require the existing Bearer access token, like learning catalog reads.
Data is shared across users; reading never writes learning or personal collection state.
`Cache-Control: no-store`, generic validation errors, and session revocation follow existing
middleware/authentication. Empty installed data produces an empty search, not a synthetic
fallback. No external provider timeouts are needed because requests use PostgreSQL only.

`GET /api/v1/dictionary/search?q=学&limit=20&offset=0`

Parameters: required `q`, 1–64 Unicode codepoints **before trimming**, then NFC-normalized;
whitespace-only queries and Unicode control/format/surrogate/private/unassigned characters
are rejected. `limit`: 1–50, default 20; `offset`: 0–1000, default 0. Invalid requests are
422 with `{"detail":"Invalid request"}`. Chinese, supplementary Han and compound queries
are supported; no substring/fuzzy/pinyin/English search is promised. `%` and `_` are literal.

```json
{
  "items": [{
    "entry_id": "stable-uuid",
    "simplified": "学生",
    "traditional": "學生",
    "primary_pinyin": "xué shēng",
    "short_vi_meaning": null,
    "available_languages": ["en"],
    "source": "cc-cedict",
    "source_revision": "operator-selected-release"
  }],
  "next_offset": null
}
```

This is an illustrative contract, not an installed production entry. Exact matches in either
form precede prefix matches in either form. Ties sort by simplified, traditional, numbered
pinyin using `C` collation, then UUID. A match through both forms appears once. The query
uses bound range parameters over indexed `C`-collated forms: `q <= form < prefix_end(q)`.
There are ordinary B-tree indexes on both forms, plus the stable ID primary key. No extension,
trigram index or external search engine is needed. Query plans below demonstrate benefit.
One lookup query fetches `limit+1`; there is no total-count query. `next_offset` is null when
exhausted or the next offset would exceed 1000. This is a bounded suggestions window, not
a bulk-export API. Ordering is stable for an unchanged dataset; an import between pages
can move results. Restart suggestions after an import rather than assuming snapshot cursors.

`GET /api/v1/dictionary/entries/{entry_id}` returns the suggestion fields plus:

| Field | Contract |
| --- | --- |
| `pinyin_numbered`, `citation_pinyin` | Source numbered spelling and deterministic tone-marked citation rendering |
| `meanings` | Language → array of `{sense_number, gloss}`; source-order one-based gloss positions, not durable semantic IDs |
| `sino_vietnamese` | Null until a reviewed lexical source is implemented |
| `parts_of_speech` | Empty string array for this source |
| `examples` | Empty array; future items have text, language-keyed translations and source |
| `audio` | Empty array; future items have reference, source and license |
| `active` | Whether included in the current source suggestions |
| `provenance` | Source, revision, artifact checksum, source URL, license identifier/URL, attribution and modifications |

Unknown UUID returns 404 `Dictionary entry not found`; malformed UUID returns 422;
missing/expired/revoked authentication returns 401. Future providers can map into these
same service/response contracts after their licensing and linguistic fields are verified.

## Import and run locally

Commands start at repository root. Use your existing native PostgreSQL development
configuration in ignored `backend/.env`; do not replace credentials or an existing database.
For optional Docker PostgreSQL with the repository's default local-only credentials:

```powershell
docker compose up -d postgres
cd backend
# Native PostgreSQL users can skip Docker and this default URL assignment.
$env:DATABASE_URL = 'postgresql+psycopg://chinese:local-dev-only@127.0.0.1:5433/chinese_learning'
.venv\Scripts\python -m alembic upgrade head
.venv\Scripts\python -m alembic check
```

After manually downloading the offered v1 gzip and reviewing its notices (from `backend/`):

```powershell
$dictionaryFile = Join-Path $env:USERPROFILE 'Downloads/cedict_1_0_ts_utf-8_mdbg.txt.gz'
$dictionaryHash = (Get-FileHash -LiteralPath $dictionaryFile -Algorithm SHA256).Hash.ToLowerInvariant()
# Revision is derived from the verified artifact header, or its full checksum.
.venv\Scripts\python -m scripts.import_dictionary --file $dictionaryFile --sha256 $dictionaryHash --acknowledge-license CC-BY-SA-4.0 --validate-only
.venv\Scripts\python -m scripts.import_dictionary --file $dictionaryFile --sha256 $dictionaryHash --acknowledge-license CC-BY-SA-4.0
.venv\Scripts\python -m app
```

Archive SHA is over the exact supplied gzip/text bytes, not decompressed text. Retain this
checksum in an acquisition manifest; hashing your download detects replay changes but is
not an independent authenticity signature. The operator verifies its origin/license.
CLI summaries report entry count, duplicate rows, batch count and replay status. Blank/comment
lines are skipped. Exact duplicates collapse; malformed/conflicting rows abort before DB
writes with total error count and at most twenty line numbers. No row payloads are logged.
DB failures roll back the entire source snapshot, including failures after earlier batches.
UTF-8/gzip/checksum errors fail closed. Parsing holds one source dataset in memory; only
DB writes are batched. Very large future datasets need a separately measured streaming path.

Swagger: open `http://127.0.0.1:8000/docs`, register/login through `/api/v1/auth`, copy
`access_token`, choose **Authorize** for HTTP Bearer, then try the dictionary search with
你, 你好, 学 or 学生. Copy an actual returned UUID into detail. If search is empty, verify a
real source was imported into the same `DATABASE_URL`; the test fixture is not auto-seeded.
An expired token requires the existing refresh/login flow.

## Verification and performance

Executed against an isolated PostgreSQL 18 cluster on loopback port 55432, using fresh
databases; the development database on 5432 was untouched. Exact reproduction commands:

```powershell
# From repository root; PostgreSQL 18 binaries installed in this environment.
$pgBin = 'C:/Program Files/PostgreSQL/18/bin'
& "$pgBin/pg_ctl.exe" start -D backend/.test-postgres-slice2-20261018 -l backend/.dictionary-postgres.log -o '-h 127.0.0.1 -p 55432' -w
# Choose NEW names if these databases already exist; never reset/recreate them.
& "$pgBin/createdb.exe" -h 127.0.0.1 -p 55432 -U slice2 dictionary_test_20261020
& "$pgBin/createdb.exe" -h 127.0.0.1 -p 55432 -U slice2 dictionary_legacy_upgrade_20261020
& "$pgBin/createdb.exe" -h 127.0.0.1 -p 55432 -U slice2 dictionary_upgrade_20261020
cd backend
$env:DATABASE_URL = 'postgresql+psycopg://slice2@127.0.0.1:55432/dictionary_test_20261020'
$env:TEST_DATABASE_URL = $env:DATABASE_URL
$env:MIGRATION_TEST_DATABASE_URL = 'postgresql+psycopg://slice2@127.0.0.1:55432/dictionary_legacy_upgrade_20261020'
$env:DICTIONARY_MIGRATION_TEST_DATABASE_URL = 'postgresql+psycopg://slice2@127.0.0.1:55432/dictionary_upgrade_20261020'
.venv\Scripts\python -m alembic upgrade head
.venv\Scripts\python -m alembic check
.venv\Scripts\python -m pytest -q
.venv\Scripts\python -m scripts.benchmark_dictionary --rows 125000
```

Both nonempty migration rehearsals refuse existing tables and intentionally leave their
fixtures. One upgrades from legacy 0001 and checks original columns/references; the new
rehearsal populates 0004 curriculum, publication assets, password credentials, access/refresh
sessions, run cursors and scene checkpoints, then verifies every old table/column after 0005.
Normal integration tests and the benchmark roll back their data. No SQLite evidence
substitutes for PostgreSQL. The optional Docker command above uses the repository's
default host port 5433; honor `POSTGRES_PORT` if customized in your local root environment.

Final run: **122 passed, zero skipped, 33.53 seconds**, including both nonempty migration
rehearsals, existing content/authentication/learning regressions, and a forced second-batch
failure proving complete import rollback. Ruff lint and formatting checks passed across
all 64 Python files; `pip check` passed; isolated `alembic check` reported no new operations.
Three warnings remain: the existing Starlette/httpx TestClient deprecation and PostgreSQL
reflection warnings about `dialect_options` during the two migration rehearsals. No
dependencies were changed. Android/device checks were not run for this backend-only slice.
The final nonempty rehearsal databases use suffix `_03`; prior attempts also retain their
fixtures. The isolated test cluster was stopped after verification; no database was reset,
downgraded or dropped. The development database was not migrated or populated.

The synthetic benchmark imported 125,975 unique entries in 252 batches, 36.916 seconds.
On this local run, 100 warm service/repository searches had median **3.197 ms**, p95
**4.534 ms**. Five query shapes included broad prefix, selective prefix and absent results.
`EXPLAIN ANALYZE` on 学 used both form indexes through BitmapOr, scanned 1,000 matching
entries and used top-N sort; SQL execution was **1.526 ms**. A sequential scan of the
single-row import metadata table is expected. Normal planner settings were used.
These historical Phase 3.1 measurements are synthetic, excluding HTTP, authentication,
network and cold caches. Phase 3.1.1 subsequently verified the developer's actual artifact
and demonstrated it in an isolated database; see the linked enrichment report. Production
linguistic review and deployment latency remain unmeasured. Run against an approved real
release before setting a public latency SLA. Use `ANALYZE dictionary_entries` after a large
real import if autovacuum has not refreshed planner statistics yet.

## Phase 3.2 assumptions

Android can consume the authenticated stable search/detail contracts and nullable/empty
metadata, with English fallback explicitly labeled and visible attribution/license notices.
Handwriting recognition can later supply selected Chinese query text to the same search;
it must not invent entry IDs or conflate readings. Debounce/cancellation belongs to the
future client; ranking remains backend-authoritative.

A future personal collection API should reference the dictionary UUID **and source
revision**, with an explicit reviewed decision about saved-definition snapshots and inactive
entries. It must use authenticated ownership and an additive schema change; the existing
curriculum `vocabulary_id` must not be repurposed. Saving an external dictionary entry must
not grant TEACHES eligibility, completion, EXP or SRS mastery. No such persistence or API
is implemented in Phase 3.1.
