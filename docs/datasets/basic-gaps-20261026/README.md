# Beginner vocabulary gaps — imported and locally approved

Audit date: 2026-10-26. Target: **postgres@127.0.0.1:5432/chinese_learning**, revision
**0010_local_codex_review**, development-only local publication already enabled.

The active Codex session compared a **709-form, session-curated beginner checklist**
against all 2,488 current curated catalog rows and the original 2,501-record reviewed
source (including excluded findings). This is a bounded coverage scan, not a claim
of exhaustive vocabulary coverage or official HSK alignment. **322 forms are absent**;
387 already exist. There are no matches hidden among the original excluded drafts.

All **322 missing entries** are now manually authored and linguistically reviewed,
with one complete Chinese/Pinyin/Vietnamese example and an individual review note.
This includes both ordinary words and basic character/word elements; bound/literary
elements such as 今、朋、目 are explicitly labelled, not passed off as unrestricted
standalone spoken words. 女、口、男 and common words such as 时间、学校、水果、可以
are included. App levels are 0: 123, 1: 189, 2: 10 (eight recorded batches).

## Provenance and review

These are **new Codex-session-authored entries, not Gemini output**. No old Gemini
data, old review notes, old holds or historical migrations were modified. Actual
individual notes are in `checkpoint/L*-B*/review-notes.json`; `authored.psv` is their
human-readable authoring source. Exact model/version and confidence remain null.
The same session authored and reviewed the supplement; no independent AI provider
or authenticated model receipt is claimed. There were no paid API calls.

The existing `local-codex-session-v1` validator and importer are reused without any
policy or architecture change. Nine linguistic areas were reviewed, including
optional Sino-Vietnamese (provided only where confidently known), example naturalness,
tones, senses, level and polyphonic identities. Native citation tones are kept in
stable keys (e.g. 一起 yi1 qi3, 不是 bu4 shi4), while examples can show spoken sandhi.
Before canonical evidence was packaged, 别人 was normalized to full citation bié rén
and the 上课 teacher-example translation/gloss was clarified. These are authoring
edits, not invented historical versioned corrections. The 别人 citation was checked
against the [MOE concise dictionary](https://dict.concised.moe.edu.tw/dictView.jsp?ID=1450&la=0&powerMode=0).

`original-zhvi/` is the directory name expected by the existing checkpoint loader;
its manifest explicitly records **Codex-session authoring**, not Gemini provenance.
`package_review.py` only packages these actual manually authored records/notes; it
does not conduct an unattended linguistic review and refuses evidence overwrites.

## Verified preview and backup

- Strict JSONL and recorded-checkpoint validation passed for all 322 entries.
- `import-plan.json`: **322 INSERT_AND_ACCEPT_LOCAL**, zero updates/conflicts.
- All 34 existing tables were fingerprinted; after import, every old row must remain
  unchanged. Only the six catalog/import/evidence tables may gain rows.
- Fresh backup: ignored `backend/.vocabulary-pipeline/basic-gaps-20261026/before-basic-supplement.dump`.
- Size: **2,682,203 bytes**; SHA-256
  `23e4ac21c177d0a48fe44f181cb7203f7242466716323984cfc19b94e5895326`.
- `pg_restore --list` and full `pg_restore --file=NUL` archive-read verification passed.
  No restore into any database was performed.
- The user explicitly confirmed **Xác nhận nhập và duyệt 322 mục** after reviewing
  the exact target, effects and command. The atomic import then succeeded with
  `accepted_local: 322`, `production_AI_APPROVED_created: 0`, operator **dxt**.
- Post-import read-only verification passed at **2026-10-26 12:02:24 +07:00**:
  every existing row across all 34 tables is unchanged, 28 non-append tables are
  identical, and only the six planned catalog/import/evidence tables gained rows.
- All 322 new current versions/checksums have matching actual recorded review
  evidence/checksums and operator dxt. Every new entry passed real catalog-service
  Chinese search and detail lookup; this is not a claim of authenticated HTTP or
  physical Android testing.

Verified committed coverage: **2,810 catalog rows**, **2,804 LOCAL_CODEX_REVIEWED**
with matching local receipts, **six unchanged DB holds**, **thirteen unresolved drafts
still excluded**, and **2,804 search-eligible entries** under the enabled local policy.
No HUMAN_APPROVED or production AI_APPROVED evidence was created. Operator: **dxt**.
See `deployment-results.json` and `added-vocabulary.csv` for the current report and
all added entries; private detailed fingerprints are in the ignored deployment directory.

## Exact PowerShell execution order

The commands below document the completed import. **Do not rerun its old confirmation**:
the database has changed, so the original plan/token is now stale. Future additions
require a separately validated and reviewed source/preview.

```powershell
Set-Location 'C:\Users\ADMIN\AndroidStudioProjects\ChineseLearningApp\backend'
$ErrorActionPreference = 'Stop'
$python = (Resolve-Path '.venv\Scripts\python.exe').Path
$env:PYTHONUTF8 = '1'
$env:PYTHONPATH = (Get-Location).Path
$env:LOCAL_VOCABULARY_DATABASE_URL = (& $python -c 'from app.core.config import get_settings; print(get_settings().database_url)')
if ($LASTEXITCODE -ne 0) { throw 'Private configuration unavailable' }
$env:ENVIRONMENT = 'development'
$env:ALLOW_LOCAL_CODEX_REVIEWED_VOCABULARY = 'true'
$reviewRoot = '..\docs\datasets\basic-gaps-20261026\checkpoint'
& $python -m scripts.local_codex_vocabulary validate --checkpoint $reviewRoot
if ($LASTEXITCODE -ne 0) { throw 'Recorded evidence validation failed' }
$plan = Get-Content '..\docs\datasets\basic-gaps-20261026\import-plan.json' -Raw -Encoding UTF8 | ConvertFrom-Json
if ($plan.confirmation -cne 'LOCAL-CODEX-2a10666aa754f1d865541e1c1d731d4200b74220e9b53229dbb694baddc64365') { throw 'Inspected confirmation changed' }

# DATABASE WRITE: already executed after explicit confirmation for this supplement.
& $python -m scripts.local_codex_vocabulary apply --checkpoint $reviewRoot --database-env LOCAL_VOCABULARY_DATABASE_URL --enable-local-codex-review --operator dxt --confirm $plan.confirmation
if ($LASTEXITCODE -ne 0) { throw 'Inspect outcome before retry; never bypass a stale confirmation' }

# Read-only verification: already executed, including every new search/detail lookup.
& $python '..\docs\datasets\basic-gaps-20261026\verify_deployment.py' after
if ($LASTEXITCODE -ne 0) { throw 'Inspect preservation/coverage failure; do not reset or remove holds' }
```

The before-stage preflight/backup has already executed; do not rerun it over existing
baseline/backup files. If the plan is stale, generate and inspect a fresh read-only
plan and obtain confirmation for its actual effects. Import is atomic; if an outcome
is uncertain, read catalog/status/receipts before retrying. Never restore over learner
data, truncate tables, bypass holds or patch checksums to force acceptance.

After this completed import, an authenticated dictionary GET with `q=女` or `q=口` must
find the new local entry, and the detail must include its verified example and local
status. The running API reads the same database; no app reinstall is required for
these server-side additions. Existing authentication remains required. Login/save
writes still need separate authorization under the earlier deployment instruction.
