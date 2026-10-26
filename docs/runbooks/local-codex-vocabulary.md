# Local Codex vocabulary acceptance — local-codex-session-v1

Deployment update, 2026-10-26: **0010_local_codex_review has now been explicitly
confirmed, applied and verified** on local `chinese_learning`. The separately confirmed
import has also completed as operator **dxt**. A later explicitly confirmed
[322-entry beginner supplement](../datasets/basic-gaps-20261026/README.md) brings the
current totals to **2,810 catalog rows, 2,804 locally accepted entries/receipts**,
six unchanged holds and thirteen unresolved drafts excluded.
Local API publication is enabled; authenticated HTTP/device checks remain pending.
Use the [deployment session report](phase403-deployment-session.md) for current state,
backup and preservation verification. The review-completion snapshots below predate
this authorized deployment.

This is the explicitly enabled **development-only** alternative for genuine recorded
Codex session reviews. It uses `LOCAL_CODEX_REVIEWED`, not `AI_APPROVED` or
`HUMAN_APPROVED`. There is no numerical confidence threshold and no paid API call.
The production `zhvi-semantic-v1` contract, including confidence >= 0.95, is unchanged.

Review-completion read-only snapshot on 2026-10-26 (Asia/Bangkok): database `chinese_learning`, host `127.0.0.1`, port
5432, role `postgres`, current migration **0009_vocabulary_ai_review**. New repository
head **0010_local_codex_review has not been applied to this database**. No development
database writes or paid API calls were made during implementation. Isolated test
databases on port 55442 were migrated and used for verification.

## Exact acceptance rules

1. Read every field and complete example of each record. Record a specific linguistic
   note covering simplified spelling, Mandarin tones/neutral tones, Vietnamese senses,
   Sino-Vietnamese, POS, example grammar/naturalness, example pinyin/translation,
   app difficulty and duplicate/alternate-reading ambiguity. Structural validation
   alone never supplies a linguistic pass.
2. Correct errors in a separate canonical copy, increase `content_version`, retain the
   lexical key/UUID, validate with `load_records`/`CuratedRecord`, and re-read the corrected
   content. The same Codex session can do that recheck; no second model is claimed.
3. Accept only `PASS` or `CORRECTED_PASS` with all nine checked areas, a nonempty actual
   note, at least one example, no pending reason, no source hold and no incoming hold.
   Current source bytes, reviewed bytes, canonical record checksums and versions must
   match the recorded notes. Duplicate identities and incomplete batch notes fail.
4. On explicitly confirmed import, store append-only local evidence and automatically
   set **LOCAL_CODEX_REVIEWED** for eligible records. There is no per-word manual
   approve command and no confidence assertion. Exact session model/version remain
   null when unavailable. UUIDs identify local receipts, not provider invocations.
5. Preserve existing database NEEDS_REVIEW/REJECTED decisions, even when an incoming
   note passes. Preserve identical HUMAN_APPROVED/AI_APPROVED decisions. Changed
   approved content and non-increasing versions are conflicts, not overrides.
6. Publish locally only with `ENVIRONMENT=development` and
   `ALLOW_LOCAL_CODEX_REVIEWED_VOCABULARY=true`, matching current-version/checksum local
   evidence and a usable Vietnamese meaning. Search, detail, save and saved-entry
   activity use this rule; the collection INSERT trigger requires the same local
   transaction opt-in and mastery zero. Disabling the flag hides local entries and
   preserves saved entries, mastery and schedules. Enabling it in test/production
   configuration is rejected. API authentication and ownership remain required.

Missing confidence, model snapshot or provider receipt is **not** a local linguistic
failure and does not create NEEDS_REVIEW. These local files are operator-attested
session evidence, not cryptographically authenticated model identity. Only unresolved
linguistic findings create new holds. Six pre-existing editorial holds are retained
under the earlier instruction not to bypass them; they are reported separately from
the thirteen pronunciation/sense/identity findings. Clearing those decisions needs
an explicit documented editorial resolution, not a threshold change.

## Completed coverage

The checkpoint covers **2,501 / 2,501 pronunciation records**, in **50 / 50 batches**,
Levels 0–5. All 2,500 distinct written learning items remain represented.
**2,482 records are local candidates; 2,488 pass linguistically**, including six retained
editorial holds. **640 records have corrected linguistic fields**, including 634
accepted candidates and six drafts with another retained issue. There are **13 unresolved
pronunciation/sense/identity findings**, separately from the six editorial holds.
No batches remain unfinished. None is imported or published by this review.

See [progress](../datasets/codex-review-4.0.3/progress.json),
[all exact corrections](../datasets/codex-review-4.0.3/corrections.json),
[all pending reasons](../datasets/codex-review-4.0.3/pending.json) and
[the read-only plan](../datasets/codex-review-4.0.3/local-plan.json).
The freshly executed read-only plan shows **2,437 INSERT_AND_ACCEPT_LOCAL** and
**45 ACCEPT_LOCAL** actions, with no conflicts. Nineteen held drafts are excluded.
See [final reconciliation](../datasets/codex-review-4.0.3/final-audit.json) for per-level
counts and full-catalog/accepted-subset hashes. `accepted-deployment.jsonl` contains
the 2,482 candidates; the local operator command still uses the checksum-bound batch
copies and notes, rather than trusting a standalone JSONL as approval evidence.

The protected conflict is **厕所|ce4 suo3**, UUID
`b58c0607-76a4-527c-a6ea-d77170d7dfd8`. Exact public records and checksums are in
[hold-conflict.json](../datasets/codex-review-4.0.3/hold-conflict.json):

| Record | Version / status | SHA-256 content checksum |
| --- | --- | --- |
| Current DB | 1 / NEEDS_REVIEW | `8cacc9b365454fb299bc079f50eb04cf3499ed3ea08c037628ee28229ee60026` |
| Original incoming dataset | 1 / GENERATED_UNREVIEWED | `8c34ca8ead7e0c31373c408222690ef5c49d9aefae83bb493870fad09cee71f6` |
| Separate reviewed draft | 2 / NEEDS_REVIEW | `1dbd1cabb4085c1ad629f96aef9f6a5b3ce4c29dd0101d76cd7c7121dbd6cf5c` |

The safe resolution for this deployment is exclusion. The importer preserves DB v1
and its editorial decision; it does not clear the hold or reset personal data.

All 50 batches were read and reviewed in Codex sessions. `batch_notes_01.py`–`45.py`
record authored findings; they are not unattended AI reviewers and must not be rerun
over their existing directories. `record_batch.py` only serializes explicit notes.
The four final targeted rechecks preserve earlier evidence under `superseded/`,
record new checksums and increase the affected versions. A prior 引起 first-pass
review is likewise archived after its identity error was caught. No provider API
review or authenticated model identity is asserted.

## PowerShell execution order

Only the validation/preview steps were executed against development here. The backup,
migration, import and API/device actions below are instructions for the operator.

### 1. Select the existing database and validate the checkpoint — no DB writes

```powershell
Set-Location 'C:\Users\ADMIN\AndroidStudioProjects\ChineseLearningApp\backend'
$ErrorActionPreference = 'Stop'
$python = (Resolve-Path '.venv\Scripts\python.exe').Path
$env:PYTHONUTF8 = '1'
$env:PYTHONPATH = (Get-Location).Path
$reviewRoot = '..\docs\datasets\codex-review-4.0.3'
$env:LOCAL_VOCABULARY_DATABASE_URL = (& $python -c 'from app.core.config import get_settings; print(get_settings().database_url)')
if ($LASTEXITCODE -ne 0) { throw 'Cannot read private database configuration' }
& $python -c "import os; from sqlalchemy.engine import make_url; u=make_url(os.environ['LOCAL_VOCABULARY_DATABASE_URL']); assert u.database=='chinese_learning' and u.host in ('localhost','127.0.0.1') and (u.port or 5432)==5432; print('Selected local chinese_learning:5432')"
if ($LASTEXITCODE -ne 0) { throw 'Wrong database target' }
$env:DATABASE_URL = $env:LOCAL_VOCABULARY_DATABASE_URL
& $python -m alembic current
if ($LASTEXITCODE -ne 0) { throw 'Cannot inspect current migration' }
& $python -m alembic heads

& $python "$reviewRoot\checkpoint.py"
if ($LASTEXITCODE -ne 0) { throw 'Checkpoint source/content validation failed' }
& $python "$reviewRoot\final_audit.py"
if ($LASTEXITCODE -ne 0) { throw 'Full review/evidence reconciliation failed' }
& $python -m scripts.curated_vocabulary validate --file "$reviewRoot\provisional-deployment.jsonl"
if ($LASTEXITCODE -ne 0) { throw 'JSONL validator failed' }
& $python -m scripts.local_codex_vocabulary validate --checkpoint $reviewRoot
if ($LASTEXITCODE -ne 0) { throw 'Recorded session evidence validation failed' }

$progress = Get-Content "$reviewRoot\progress.json" -Raw -Encoding UTF8 | ConvertFrom-Json
if ($progress.reviewed_records -ne 2501 -or $progress.unreviewed_records -ne 0 -or $progress.completed_batches.Count -ne 50) { throw 'Full review coverage is required' }

& $python -m scripts.local_codex_vocabulary plan --checkpoint $reviewRoot --database-env LOCAL_VOCABULARY_DATABASE_URL --output "$reviewRoot\local-plan.json"
if ($LASTEXITCODE -ne 0) { throw 'Read-only preview failed' }
$plan = Get-Content "$reviewRoot\local-plan.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$plan.database
$plan.migrations
$plan.coverage | Select-Object reviewed,accepted,unreviewed
$plan.changes | Group-Object action | Select-Object Name,Count
$plan.changes | Format-Table lexical_key,action,incoming_version,before -AutoSize
$plan.coverage.excluded | Format-Table lexical_key,reason -Wrap
Get-Content "$reviewRoot\hold-conflict.json" -Raw -Encoding UTF8 | ConvertFrom-Json | Format-List
```

The plan uses `REPEATABLE READ READ ONLY` and includes every proposed content/status
change, existing version/checksum/status, incoming version/checksum and evidence hash.
It also binds database identity, migration and review coverage into the confirmation.
This first plan reports 0009; its token **cannot execute after migration 0010**.
The historical filename `provisional-deployment.jsonl` now contains the complete
reviewed catalog, including held rows, and is not the import input
of this local command. It selects passing reviewed batch copies itself.

### 2. Back up and explicitly apply additive 0010 — operator DB write

```powershell
$backupDirectory = Join-Path (Get-Location).Path ('.vocabulary-pipeline\codex-local-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $backupDirectory | Out-Null
$env:LOCAL_VOCABULARY_BACKUP_DIR = $backupDirectory
@'
import os, subprocess
from pathlib import Path
from sqlalchemy.engine import make_url
u = make_url(os.environ['LOCAL_VOCABULARY_DATABASE_URL'])
backup = Path(os.environ['LOCAL_VOCABULARY_BACKUP_DIR']) / 'before-local-codex.dump'
if backup.exists():
    raise ValueError('Backup must be new')
child = dict(os.environ, PGHOST=u.host, PGPORT=str(u.port or 5432),
             PGUSER=u.username, PGDATABASE=u.database, PGPASSWORD=u.password or '')
subprocess.run([r'C:\Program Files\PostgreSQL\18\bin\pg_dump.exe',
                '-Fc', '-f', str(backup)], env=child, check=True)
print('Backup complete:', backup.name, backup.stat().st_size, 'bytes')
'@ | & $python -
if ($LASTEXITCODE -ne 0) { throw 'Backup failed' }

if ((Read-Host 'Type MIGRATE chinese_learning TO 0010') -cne 'MIGRATE chinese_learning TO 0010') { throw 'Migration not confirmed' }
& $python -m alembic upgrade 0010_local_codex_review
if ($LASTEXITCODE -ne 0) { throw 'Migration failed; inspect current before retry' }
& $python -m alembic current
& $python -m alembic check
if ($LASTEXITCODE -ne 0) { throw 'Schema check failed' }
```

Expected: 0010 adds a separate append-only local evidence table, permits the distinct
local status and extends the collection guard. No existing row is rewritten or
deleted. Historical revisions 0001–0009 are unchanged. Do not downgrade or reset.

### 3. Fresh preview, then explicitly confirmed atomic import and local approval

```powershell
$env:ENVIRONMENT = 'development'
$env:ALLOW_LOCAL_CODEX_REVIEWED_VOCABULARY = 'true'
# No change to ALLOW_AI_APPROVED_VOCABULARY is required.
& $python -m scripts.local_codex_vocabulary plan --checkpoint $reviewRoot --database-env LOCAL_VOCABULARY_DATABASE_URL --output "$reviewRoot\local-plan.json"
if ($LASTEXITCODE -ne 0) { throw 'Fresh preview failed' }
$plan = Get-Content "$reviewRoot\local-plan.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$plan.database
$plan.migrations
$plan.changes | Group-Object action | Select-Object Name,Count
$plan.changes | Format-Table lexical_key,action,incoming_version,before -AutoSize
if ($plan.migrations.Count -ne 1 -or $plan.migrations[0] -ne '0010_local_codex_review') { throw 'Wrong migration' }
if ($plan.changes | Where-Object { $_.action -like '*CONFLICT' }) { throw 'Resolve conflicts first' }
$operator = Read-Host 'Your name as the local evidence-submitting operator'
if ([string]::IsNullOrWhiteSpace($operator)) { throw 'Named operator required' }
if ((Read-Host 'Type IMPORT AND ACCEPT LOCAL chinese_learning') -cne 'IMPORT AND ACCEPT LOCAL chinese_learning') { throw 'Import not confirmed' }
& $python -m scripts.local_codex_vocabulary apply --checkpoint $reviewRoot --database-env LOCAL_VOCABULARY_DATABASE_URL --enable-local-codex-review --operator $operator --confirm $plan.confirmation
if ($LASTEXITCODE -ne 0) { throw 'Atomic operation failed; preview again before retry' }
```

With the verified dataset/state, expect **2,482 local approvals**, zero production AI approvals,
**2,488 total catalog records** (the existing 51 plus 2,437 inserts), and six existing held
database records untouched. The thirteen other uncertain/identity drafts are excluded and not
inserted by this command. The command imports only reviewed passing records and
records their actual notes automatically; it does not submit a production AI result.
It rechecks the plan under the shared import advisory lock. Content import and receipt/
status updates commit together in one outer transaction; any failure rolls back both.
Batch IDs and local receipt IDs are deterministic for replay. No personal table is
updated by this operation.

### 4. Enable the API process and verify Android search

Use the same private DB configuration and development flag in the API process, or
add these two settings to your untracked `backend/.env`, then restart the API:

```powershell
$env:ENVIRONMENT = 'development'
$env:ALLOW_LOCAL_CODEX_REVIEWED_VOCABULARY = 'true'
& $python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In another backend PowerShell, use an existing unexpired development token. Logging
in normally is also possible after operator authorization; it creates session writes.

```powershell
$tokenSecret = Read-Host 'Existing development access token' -AsSecureString
$httpHeaders = @{ Authorization = 'Bearer ' + [System.Net.NetworkCredential]::new('', $tokenSecret).Password }
$q = [uri]::EscapeDataString('材料')
$search = Invoke-RestMethod "http://127.0.0.1:8000/api/v1/dictionary/search?q=$q&limit=20&offset=0" -Headers $httpHeaders
$hit = $search.items | Where-Object simplified -eq '材料' | Select-Object -First 1
if (!$hit) { throw 'Local accepted word not searchable; inspect API flag and database' }
$detail = Invoke-RestMethod "http://127.0.0.1:8000/api/v1/dictionary/entries/$($hit.entry_id)" -Headers $httpHeaders
$detail | Select-Object simplified,review_status,content_version
if ($detail.review_status -ne 'LOCAL_CODEX_REVIEWED') { throw 'Unexpected publication basis' }
$detail.examples
Remove-Variable httpHeaders,tokenSecret
```

Expect 材料, version 2, LOCAL_CODEX_REVIEWED, Vietnamese tài liệu/vật liệu, and
corrected **shōují** in its example. 厕所 UUID
`b58c0607-76a4-527c-a6ea-d77170d7dfd8` must still return 404 from authenticated detail.
401 means expired authentication, not a publication failure.

For one USB Android device:

```powershell
Set-Location 'C:\Users\ADMIN\AndroidStudioProjects\ChineseLearningApp'
$adb = "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe"
& $adb devices -l
& $adb -d reverse tcp:8000 tcp:8000
Set-Location android
.\gradlew.bat installDebug '-PDEV_API_BASE_URL=http://127.0.0.1:8000/'
if ($LASTEXITCODE -ne 0) { throw 'Debug installation failed' }
& $adb -d shell am start -n com.example.chineselearningapp/.MainActivity
```

Open **Học tập → Tra từ điển**, search 材料 and Vietnamese tài liệu, then open the
entry. Expect correct pinyin/meanings and the local Codex review label. Saving it to
personal vocabulary is an optional learner write; verify initial mastery zero and
that re-saving an existing entry preserves its mastery/schedule. No uninstall, app
data clear or database reset is needed. Device validation was not performed here.

## Recovery and provenance

| Failure | Recovery |
| --- | --- |
| Stale source/content/note hash | Stop. Preserve old evidence, inspect changed bytes, perform a real re-review and record its new checksum/version. Never patch a hash merely to pass. |
| Stale confirmation | Re-run plan, inspect every change and explicitly confirm the new token. Dataset, notes, DB statuses or migration can invalidate it. |
| Version/approved-content conflict | Prepare a reviewed higher version with explicit editorial resolution. Do not overwrite approved history or rename a lexical key silently. |
| Existing hold | PRESERVE_HOLD skips it. Resolve and document the underlying editorial decision separately; this command deliberately cannot clear it. |
| Interrupted/failed apply | Outer transaction rolls back; preview again. If connection outcome is uncertain, inspect a fresh plan/current evidence before retry. Exact receipts replay without duplication. |
| Hidden word | Check API's actual development flag, current checksum/version evidence and Vietnamese meaning; restart API after configuration changes. |
| Disable local publication | Set ALLOW_LOCAL_CODEX_REVIEWED_VOCABULARY=false and restart. Keep evidence, saved rows, mastery and migration intact. |
| Migration failure | Run alembic current, inspect transactional failure and fix forward. Do not downgrade, drop tables, restore over existing learner data, or delete volumes. |

Gemini attribution is a historical user/source claim. The source defaults
`google/gemini-3.8-flash/2026-10` do not prove the actual generator model or version;
the month is not a verified snapshot. Missing evidence is an original export/API
response with actual model identifier and artifact binding. Keep original JSONL,
manifests and the generator scripts unchanged until that evidence is recovered.
If recovered, correct a separate snapshot's `level-*-batch-*.manifest.json`, associated
`level-*-batch-*.review-input.jsonl` files and byte-bound generator ledger using the detailed
[provenance procedure](local-vocabulary-deployment.md); do not regenerate vocabulary
or guess a model ID. The local path only needs the verifiable source/content checksums
and honest recorded Codex notes, so missing historical generator snapshot is not a
local acceptance blocker. It never asserts authenticated independent provider identity.

The existing production runner supports Anthropic Messages; it is unchanged and is
not used by any command above. There are no required ANTHROPIC_API_KEY,
VOCAB_REVIEW_PROVIDER or paid-model settings for this workflow. Its incremental
third-party API cost is zero; ordinary Codex subscription/session usage is separate.

Final review verification executed: all 50 batch JSONL files and the complete 2,501
record catalog passed the repository validator; full source/current checksums,
versions, identities, example presence and local evidence reconciled. The read-only
development snapshot and plan were refreshed with 2,482 candidates and no conflicts.
Migration 0009 is applied; 0010 remains unapplied. See
[read-only snapshot](../datasets/codex-review-4.0.3/database-inspection-read-only.json).

Earlier implementation verification (not rerun for this dataset-only continuation):
backend suite 212 passed / 7 skipped; nonempty 0008 → 0010
preservation rehearsal and Alembic check passed; source audit and strict JSONL
validation passed. An additional isolated operator rehearsal passed confirmation,
atomic rollback and replay checks. Android unit tests, debug assembly and debug lint
passed with cached Gradle 9.2.1 offline. No claim of
physical Android validation or development publication is made.
