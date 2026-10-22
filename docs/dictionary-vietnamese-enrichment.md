# Phase 3.1.1 — Revision repair and Vietnamese character enrichment

Reviewed 2026-10-21. Backend only. No Android, handwriting, personal collection,
curriculum publication, lesson completion, EXP or SRS implementation is added.

## Observed development import and repair evidence

Read-only inspection found one CC-CEDICT import:

| Property | Observed value |
| --- | --- |
| Import UUID | `66018297-d61d-5f15-a0c8-6e158077ee40` |
| Incorrect label | `your-actual-source-release` |
| Artifact SHA-256 | `3681b52f0f733e0caada3fa2fbe2236bfa1234333397f35f10f285ac292abec9` |
| Associated / active entries | 125,303 / 125,303 |
| Import timestamp, normalized to UTC | 2026-10-20T17:32:03.601119Z |
| Original local artifact | `Downloads/cedict_1_0_ts_utf-8_mdbg.txt.gz` |
| Verified artifact header | `#! date=2026-10-19T20:24:47Z`, matching epoch `1792441487` |
| Proposed truthful label | `cedict-20261019T202447Z` |

The local artifact checksum exactly matches the stored import checksum. Its header also
identifies MDBG, v1, 125,303 entries and CC BY-SA 4.0. The only incoming dictionary import
FK found is `dictionary_entries.import_id`; no table references dictionary entries yet.
Entry/import UUIDs are separate identities: simply renaming the revision would break the
old importer's assumption that a revision always determines its import UUID.

**No development database mutation was performed.** The actual maintenance dry-run
reported `changed: false`, `already_corrected: false`, `requires_migration: true`.
The proposed repair is ready for the developer to apply after reviewing the commands below.
It has been tested with committed repairs/retries only in isolated test transactions.

The maintenance command defaults to dry-run and accepts explicit `--dry-run`. Writing
requires `--confirm`. It verifies source, exact artifact hash, original deterministic import
identity, one unambiguous old/canonical row, matching artifact/import/associated row counts,
and a fully active snapshot. Missing, ambiguous, partial or superseded imports fail closed.
Confirmed writes take the same advisory lock as the CC-CEDICT importer, recheck conditions,
and update only `revision` and `revision_correction` in one transaction. The audit JSON
stores the old label, correction timestamp, checksum and header/hash evidence. Existing
import UUID, original import time, entry FKs/UUIDs, definitions, pinyin and licensing survive.
Retrying the same correction is a no-op; a conflicting history is rejected. No entries or
snapshots are recreated. This narrow command does not repair arbitrary edited databases.

The importer now looks up previous imports by `(source, revision)`, retaining their actual
UUID on replay. It refuses a second import of an artifact that still has a placeholder label;
use maintenance rather than reimporting it under another label.

## What a revision means

- **Upstream release:** an identifier actually supplied by the publisher. CC-CEDICT's
  verified artifact date produces `cedict-YYYYMMDDTHHMMSSZ`; a Git dataset can use its commit.
- **Local import revision:** an operator's immutable label for that source artifact. If
  an upstream date cannot be verified, `artifact-sha256-<full checksum>` explicitly identifies
  an internal revision without inventing a publisher date.
- **Source checksum:** SHA-256 of exact input bytes, including gzip bytes when supplied.
  It pins an artifact, not a download date or proof of linguistic correctness.

For new CC-CEDICT imports, **omit `--revision`** to derive it from verified artifact headers
or the full checksum fallback. Contradictory/malformed date metadata is rejected. Optional
explicit local labels are still accepted, but obvious placeholder tokens (`your`, `example`,
`replace`, `placeholder`, case-insensitive) are rejected, including in validate-only mode.
Changing bytes under an existing revision remains an error. Existing historic labels are
readable; rejecting placeholders is not a destructive migration or automatic repair.

## Source choice and exact coverage

Selected character source: [Kai Hanzi / hsk-sino-viet](https://github.com/xkhanhs/hsk-sino-viet),
pinned commit `7cd2805fb0bb46f8e21bda364b857759465f1ce2`. Downloaded data, LICENSE,
NOTICE, metadata and README were inspected. The data artifact SHA-256 is
`50a50b9d56374be5815c5f53a5f26569522143a9a4e94a7387ee6935d21e82ba`.

Actual parsing found **659 unique single-character records**, with **116 explicit traditional
forms**. Fields selected are `hanzi`, `traditional`, `pinyin`, `sinoViet`, `meaningVi`.
Other upstream fields are ignored. Null traditional forms are not expanded through inferred
variants. Coverage is the publisher's teaching selection; it is not a complete Chinese
dictionary, independently verified HSK inventory, or complete pronunciation inventory.

The [upstream notice](https://github.com/xkhanhs/hsk-sino-viet/blob/7cd2805fb0bb46f8e21bda364b857759465f1ce2/NOTICE.md)
attributes the text to Kai Hanzi. Manual authorship is the publisher's assertion; this
implementation does not independently certify each reading, gloss, variant or sense.
Every annotation reports `source_declared_manual_not_independently_reviewed`. A source
gloss can discuss more readings than its pinyin field; it is retained as opaque text,
not split into invented lexical senses. Word meanings and lexical Sino-Vietnamese remain
unavailable. **Zero word-level Vietnamese translations are added.**

The [CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/) allows commercial
reuse/adaptation with attribution, license/change notices and no added restrictions;
it has no share-alike condition. Preserve upstream credit and notices. English dictionary
data retains its separate CC BY-SA 4.0 provenance and obligations. Enrichment does not
relicense CC-CEDICT. Stroke geometry has separate terms and is not acquired/imported here.
Attribution returned by the API credits the Kai Hanzi dataset and links its original site.

Alternatives and rejection reasons are recorded in
[dictionary source evaluation](dictionary-source-evaluation.md#phase-311-vietnamese-enrichment).
No trustworthy word-level source was verified for this slice; missing lexical fields stay null.

## Additive schema and identity

Revision `0006_dictionary_enrichment` follows 0005. No old migration is modified.

| Change | Purpose |
| --- | --- |
| `dictionary_imports.revision_correction` nullable JSONB | Evidence/audit for the explicit metadata correction; null for ordinary imports |
| `dictionary_enrichment_imports` | Unique source/revision, exact artifact hash, provenance, license, quality status, record count and UTC import time |
| `dictionary_character_enrichments` | Character source key, optional explicit traditional form, source pronunciation, reading/gloss and import FK |

The selected source declares one record per simplified Han character. `(source, hanzi)`
is its character key, **not** a lexical entry identifier. Repeated keys, including conflicting
pronunciations, and overlapping variant aliases are rejected. The parser validates Unicode,
field bounds and JSON structure and normalizes NFC. Import also checks alias collisions
against already imported partial coverage. It runs transactionally under its own source lock,
writes in batches of 500 and rejects changed artifacts under the same source/revision.
Replaying an imported revision is a no-op. A later source revision replaces its selected
character records; omitted characters retain their last-seen provenance. There is no
deletion, synthesized word data, or automatic merge into curriculum `characters`/`vocabulary`.

## Compatible API extension

The authenticated search and detail paths, ranking, pagination, entry UUIDs, English
meanings and primary provenance retain their Phase 3.1 contracts.

Search intentionally retains `short_vi_meaning: null` and `available_languages: ["en"]`:
these describe **lexical definitions**, not the languages of optional character notes.
Detail retains `sino_vietnamese: null`, no `meanings.vi`, and empty audio/examples/POS.
It adds optional `character_enrichments`, an empty array where coverage is absent.

Each character annotation includes:

| Field | Meaning |
| --- | --- |
| `scope` | Always `character` |
| `form` | A literal matching form in this entry, not a derived word identity |
| `positions`, `traditional_positions` | Zero-based positions matched independently in each headword; repeated characters retain all positions |
| `source_hanzi`, `traditional` | Source record identity and its explicit variant, if any |
| `pinyin`, `sino_vietnamese`, `vietnamese_gloss` | Source character metadata, never composed into a word translation/reading |
| `matches_entry_pronunciation` | Conservative exact text equality for one-character entries; false for a different source reading/case, null for compounds. This is not independent phonological verification |
| `provenance` | Source/revision/checksum, source/license links, attribution, modification notice and review status |

For example, a dictionary result for 学生 can expose separate notes for its two characters
after full-source import. It still has no sourced Vietnamese lexical definition. For 行,
the notes remain character-level and explicitly flag a pronunciation mismatch on a different
CC-CEDICT reading. An annotation is never attached as a lexical sense by matching Hanzi alone.
No character positions are inferred by aligning unequal-length simplified/traditional strings.

Detail uses one additional bounded query across the literal character set, not an N+1 loop.
Search adds no enrichment DB round trip. The character PK and traditional-form index support
the extra detail query. No external runtime API or new dependency is needed.

## Exact local commands

Run from repository root. The first dry-run works even before 0006. These commands use
your existing `backend/.env`; check that a shell-level `DATABASE_URL` is not selecting an
old test database. Do not publish the connection string or overwrite its credentials.

```powershell
cd backend
$cedictFile = Join-Path $env:USERPROFILE 'Downloads/cedict_1_0_ts_utf-8_mdbg.txt.gz'
$cedictHash = '3681b52f0f733e0caada3fa2fbe2236bfa1234333397f35f10f285ac292abec9'
.venv\Scripts\python -m scripts.repair_dictionary_revision --file $cedictFile --sha256 $cedictHash --dry-run
```

Only when ready to apply changes to that local development database:

```powershell
.venv\Scripts\python -m alembic upgrade head
.venv\Scripts\python -m alembic check
.venv\Scripts\python -m scripts.repair_dictionary_revision --file $cedictFile --sha256 $cedictHash --confirm
# Safe retry: reports already_corrected=true and changed=false.
.venv\Scripts\python -m scripts.repair_dictionary_revision --file $cedictFile --sha256 $cedictHash --dry-run
```

Acquire the pinned public enrichment source and its notices (from `backend/`):

```powershell
$enrichmentCommit = '7cd2805fb0bb46f8e21bda364b857759465f1ce2'
$enrichmentDir = '.dictionary-source-cache/hsk-sino-viet'
New-Item -ItemType Directory -Force "$enrichmentDir/data" | Out-Null
$enrichmentBase = "https://raw.githubusercontent.com/xkhanhs/hsk-sino-viet/$enrichmentCommit"
Invoke-WebRequest "$enrichmentBase/LICENSE" -OutFile "$enrichmentDir/LICENSE"
Invoke-WebRequest "$enrichmentBase/NOTICE.md" -OutFile "$enrichmentDir/NOTICE.md"
Invoke-WebRequest "$enrichmentBase/data/meta.json" -OutFile "$enrichmentDir/data/meta.json"
Invoke-WebRequest "$enrichmentBase/data/characters.json" -OutFile "$enrichmentDir/data/characters.json"
$enrichmentFile = "$enrichmentDir/data/characters.json"
$enrichmentHash = '50a50b9d56374be5815c5f53a5f26569522143a9a4e94a7387ee6935d21e82ba'
(Get-FileHash -LiteralPath $enrichmentFile -Algorithm SHA256).Hash.ToLowerInvariant()
# Review LICENSE/NOTICE; the command below pins the expected data hash independently.
.venv\Scripts\python -m scripts.import_dictionary_enrichment --file $enrichmentFile --sha256 $enrichmentHash --revision $enrichmentCommit --acknowledge-license CC-BY-4.0 --validate-only
.venv\Scripts\python -m scripts.import_dictionary_enrichment --file $enrichmentFile --sha256 $enrichmentHash --revision $enrichmentCommit --acknowledge-license CC-BY-4.0
.venv\Scripts\python -m app
```

Stop an already running API before restarting it with migrated schema/code. No migration
or source import runs at application startup. For a **new** CC-CEDICT artifact, review its
license, compute its actual SHA-256, then omit the revision argument:

```powershell
$cedictHash = (Get-FileHash -LiteralPath $cedictFile -Algorithm SHA256).Hash.ToLowerInvariant()
.venv\Scripts\python -m scripts.import_dictionary --file $cedictFile --sha256 $cedictHash --acknowledge-license CC-BY-SA-4.0 --validate-only
.venv\Scripts\python -m scripts.import_dictionary --file $cedictFile --sha256 $cedictHash --acknowledge-license CC-BY-SA-4.0
```

This normal import command intentionally refuses the still-placeholder artifact; repair
it first. Do not replace the fixed maintenance checksum with a newly guessed file hash.
If the local artifact differs, stop and identify the originally imported artifact.

Swagger: login/register, Authorize with the access token, search 学/學/学生/银行, then
copy a returned UUID into detail. Verify `character_enrichments` and its provenance.
Check an uncovered character returns an empty list; English meanings remain unchanged.
401 still indicates absent/expired/revoked authentication, not a dictionary data problem.

## Tests and genuine integration demonstration

The committed genuine fixture contains **two** selected source records/five fields, with
separate original/subset hashes and attribution. It is not the 659-record distribution.
Synthetic homograph/malformed fixtures are explicitly test-only. No complete data dump,
credentials, database files or generated builds are committed.

An isolated demo database imported the actual **125,303-entry CC-CEDICT artifact** and
**all 659 source character records** (251 and 2 batches). Authenticated ASGI requests for
学生, 學, 我, 银行 and 行 returned 200 and sourced character annotations. Lexical Vietnamese
and lexical Sino-Vietnamese stayed absent. The demo's temporary account/session writes
were rolled back; its source fixtures remain for inspection. This is a genuine data
demonstration, not a claim of 659 reviewed word translations or a deployed UI.

Tests cover placeholder rejection, automatic labels, checksum/header consistency, repair
dry-run/retry/collision, stable IDs/FKs and preserved metadata/content, genuine character
coverage, ambiguous source keys/variants, independent homograph readings, missing lexical
fields, additive API behavior, partial imports, repeated imports and migrations. The
0005 → 0006 rehearsal retains every old dictionary/user/curriculum column and leaves
the correction audit null until explicit maintenance. Original legacy/current-auth migration
rehearsals are also retained. All rehearsal databases must be fresh/empty and are never reset.

Final verification: **147 passed, zero skipped, 49.55 seconds** on PostgreSQL 18, including
all three nonempty migration rehearsals and existing authentication/learning/dictionary
regressions. Ruff lint and format checks passed for 74 Python files; `pip check` passed;
isolated `alembic check` reported no new operations. Four non-failing warnings remain:
the existing Starlette/httpx TestClient deprecation and metadata reflection warnings during
the three rehearsals. No dependency changes or Android/device validation were performed.
The test cluster was stopped after verification; fixtures/databases remain intact.

Reproduction on the existing isolated test cluster (not the development database):

```powershell
# From repository root; start only if the isolated cluster is stopped.
$pgBin = 'C:/Program Files/PostgreSQL/18/bin'
& "$pgBin/pg_ctl.exe" start -D backend/.test-postgres-slice2-20261018 -l backend/.dictionary-postgres.log -o '-h 127.0.0.1 -p 55432' -w
# These names must be new. Use another suffix for another rehearsal.
& "$pgBin/createdb.exe" -h 127.0.0.1 -p 55432 -U slice2 dictionary_enrichment_test_20261021
& "$pgBin/createdb.exe" -h 127.0.0.1 -p 55432 -U slice2 enrichment_legacy_full_20261021
& "$pgBin/createdb.exe" -h 127.0.0.1 -p 55432 -U slice2 enrichment_dictionary_full_20261021
& "$pgBin/createdb.exe" -h 127.0.0.1 -p 55432 -U slice2 enrichment_upgrade_full_20261021
cd backend
$env:DATABASE_URL = 'postgresql+psycopg://slice2@127.0.0.1:55432/dictionary_enrichment_test_20261021'
$env:TEST_DATABASE_URL = $env:DATABASE_URL
$env:MIGRATION_TEST_DATABASE_URL = 'postgresql+psycopg://slice2@127.0.0.1:55432/enrichment_legacy_full_20261021'
$env:DICTIONARY_MIGRATION_TEST_DATABASE_URL = 'postgresql+psycopg://slice2@127.0.0.1:55432/enrichment_dictionary_full_20261021'
$env:ENRICHMENT_MIGRATION_TEST_DATABASE_URL = 'postgresql+psycopg://slice2@127.0.0.1:55432/enrichment_upgrade_full_20261021'
.venv\Scripts\python -m alembic upgrade head
.venv\Scripts\python -m alembic check
.venv\Scripts\python -m pytest -q
.venv\Scripts\python -m ruff check .
.venv\Scripts\python -m ruff format --check .
.venv\Scripts\python -m pip check
```

## Before Phase 3.2

Clients must label character notes and display attribution/review status without presenting
them as word translations. Choose whether this limited coverage is sufficient for the first
UI. A verified word-level Vietnamese source still needs sense/reading-specific reviewed
mapping to stable dictionary UUIDs; do not join it on Hanzi alone. Personal collection,
handwriting recognition and any linguistic review/publishing workflow remain future tasks.
