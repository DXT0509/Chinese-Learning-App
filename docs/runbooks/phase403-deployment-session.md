# Phase 4.0.3 development deployment — imported and locally published

Subsequent confirmed update, 2026-10-26: the
[beginner supplement](../datasets/basic-gaps-20261026/README.md) added 322 reviewed
entries as operator dxt. **Current database totals: 2,810 catalog rows, 2,804 locally
accepted/search-eligible entries, six unchanged holds, thirteen unresolved drafts
excluded**. Every existing row was preserved. Counts below describe the original
Phase 4.0.3 import before that supplement.

Session date: 2026-10-26, Asia/Bangkok. Follow the governing
[local Codex runbook](local-codex-vocabulary.md),
[review report](../phase4.0.3-codex-review.md) and
[dataset README](../datasets/codex-review-4.0.3/README.md).

**Stages 1–8 are complete. Migration 0010 and the explicitly confirmed import are applied.** The user explicitly
requires confirmation before every database write. Migration, import, login/refresh,
and the personal-vocabulary save test must each respect that boundary. The commands
below for stage 9 are prepared instructions, not executed authenticated actions.

## Target and observed coverage

- PostgreSQL database: **chinese_learning**.
- Server: **127.0.0.1:5432**; server-returned address `127.0.0.1/32`.
- Database role: **postgres**; environment: **development**.
- Applied revision and repository head: **0010_local_codex_review**.
- Reviewed: 2,501 records / 50 batches; 2,482 eligible; 640 corrected.
- Preview: every one of the 2,482 actions checked; **2,437 inserts + 45 acceptances**;
  zero conflicts. All nineteen pending keys excluded.
- Preservation baseline: counts and content fingerprints for **27 protected tables**,
  covering accounts, sessions, existing personal data and progress; six held catalog
  records separately bound by key/version/checksum/status.

| Coverage | Before deployment | Verified after import |
| --- | ---: | ---: |
| Total catalog records | 51 | 2,488 |
| GENERATED_UNREVIEWED | 45 | 0 |
| LOCAL_CODEX_REVIEWED | 0 | 2,482 |
| Protected NEEDS_REVIEW rows in DB | 6 | 6 |
| Unresolved drafts outside DB | 13 | 13 |
| Local evidence receipts | 0 | 2,482 |
| Eligible under enabled application search predicate | 0 | 2,482 |

All 2,482 accepted entries satisfy the actual application publication predicate.
The locally enabled API is running at `http://127.0.0.1:8000`; `/health` returns 200/ok
and unauthenticated dictionary search returns 401. Actual authenticated HTTP/device
checks remain pending: no access token was supplied and `adb devices -l` returned no connected devices.
No physical-device success is claimed from static contract inspection.

## 1. Configuration and dataset validation — executed, passed

Run PowerShell from the backend directory. Keep the private URL out of logs:

```powershell
Set-Location 'C:\Users\ADMIN\AndroidStudioProjects\ChineseLearningApp\backend'
$ErrorActionPreference = 'Stop'
$python = (Resolve-Path '.venv\Scripts\python.exe').Path
$env:PYTHONUTF8 = '1'
$env:PYTHONPATH = (Get-Location).Path
$reviewRoot = '..\docs\datasets\codex-review-4.0.3'
$deploymentRoot = '.vocabulary-pipeline\phase403-deploy-20261026-a8f3'
$env:LOCAL_VOCABULARY_DATABASE_URL = (& $python -c 'from app.core.config import get_settings; print(get_settings().database_url)')
if ($LASTEXITCODE -ne 0) { throw 'Cannot read private DB configuration' }
$env:DATABASE_URL = $env:LOCAL_VOCABULARY_DATABASE_URL
& $python -c "import os; from sqlalchemy.engine import make_url; u=make_url(os.environ['DATABASE_URL']); assert u.database=='chinese_learning' and u.host in ('127.0.0.1','localhost') and (u.port or 5432)==5432; print('Target: local chinese_learning:5432; role='+str(u.username))"
if ($LASTEXITCODE -ne 0) { throw 'Unexpected DB target' }
& $python -m alembic current
& $python -m alembic heads
& $python "$reviewRoot\checkpoint.py"
if ($LASTEXITCODE -ne 0) { throw 'Checkpoint validation failed' }
& $python "$reviewRoot\final_audit.py"
if ($LASTEXITCODE -ne 0) { throw 'Evidence reconciliation failed' }
& $python -m scripts.curated_vocabulary validate --file "$reviewRoot\provisional-deployment.jsonl"
if ($LASTEXITCODE -ne 0) { throw 'Strict JSONL validation failed' }
& $python -m scripts.local_codex_vocabulary validate --checkpoint $reviewRoot
if ($LASTEXITCODE -ne 0) { throw 'Local evidence validation failed' }
```

Expected: 2,501 reviewed, 2,500 written items, 50 complete batches, 2,482 candidates,
19 exclusions, no duplicates or missing examples. Original and reviewed checksums,
content versions and notes match. Full catalog hash remains
`1e490609d214cd9b3fc3d038e60f31570cb3568f4795dcc20c5a3f0ab28fa8fc`;
accepted subset hash remains
`3c17f51cba7f558bb8c8648a5475bf59c4935a8c5822b2e8ed768bea9b91773e`.

## 2. Read-only preview and inspection — executed, passed

The session's exact plan is stored at
`backend/.vocabulary-pipeline/phase403-deploy-20261026-a8f3/pre-migration-plan.json`.
The private `preflight.py` helper called the existing `load_checkpoint` and `preview`
functions inside `REPEATABLE READ READ ONLY`, checked every action against the
actual existing record and all excluded keys, and created preservation fingerprints.
It then performed stage 3. Its exact executed command was:

```powershell
& $python "$deploymentRoot\preflight.py"
```

Do not rerun that command into the same directory: it deliberately refuses to replace
baseline/backup files. To create another ordinary preview without a database write:

```powershell
& $python -m scripts.local_codex_vocabulary plan --checkpoint $reviewRoot --database-env LOCAL_VOCABULARY_DATABASE_URL --output "$deploymentRoot\pre-migration-preview-recheck.json"
if ($LASTEXITCODE -ne 0) { throw 'Read-only preview failed' }
$plan = Get-Content "$deploymentRoot\pre-migration-preview-recheck.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$plan.database
$plan.migrations
$plan.changes | Group-Object action | Select-Object Name,Count
$plan.changes | Format-Table lexical_key,action,incoming_version,before -Wrap
$plan.coverage.excluded | Format-Table lexical_key,reason -Wrap
```

Expected: 2,437 INSERT_AND_ACCEPT_LOCAL, 45 ACCEPT_LOCAL, no conflict; six source/DB
holds and thirteen unresolved drafts excluded. The pre-migration token becomes stale
after 0010 and must not be used for import.

## 3. Fresh backup — executed and archive-verified

Backup:
`backend/.vocabulary-pipeline/phase403-deploy-20261026-a8f3/before-local-codex.dump`.
Size **114,349 bytes**; SHA-256
`ed281a1fcf4d01e697758510634dfd14bf84c648b72ec6c5a9fbe71f61a1f079`.
The helper used PostgreSQL 18 `pg_dump --no-password -Fc`, with credentials passed
only through the child process environment from the private application settings.
`pg_restore --list` passed; every archive entry decompressed and rendered to an SQL
sink via `pg_restore --file=NUL`. **No restore into any database was performed.**
This verifies archive readability, not a complete restore rehearsal. Backup and
preservation metadata are kept in the already ignored `.vocabulary-pipeline` directory.

Exact verification commands:

```powershell
$backup = Join-Path $deploymentRoot 'before-local-codex.dump'
Get-Item -LiteralPath $backup | Select-Object FullName,Length
Get-FileHash -LiteralPath $backup -Algorithm SHA256
& 'C:\Program Files\PostgreSQL\18\bin\pg_restore.exe' --list $backup
if ($LASTEXITCODE -ne 0) { throw 'Backup table-of-contents verification failed' }
& 'C:\Program Files\PostgreSQL\18\bin\pg_restore.exe' --file=NUL $backup
if ($LASTEXITCODE -ne 0) { throw 'Backup archive verification failed' }
```

If a fresh backup is needed after external activity, create a new directory, copy
`preflight.py` into it, and execute that copy from the backend working directory.
Do not overwrite the present backup. Do not restore over the development database.

## 4. Migration 0010 — explicitly confirmed and completed

The user confirmed **MIGRATE chinese_learning TO 0010** in chat. The migration was
then executed against the verified target. Post-migration verification completed at
**2026-10-26 10:57:37 +07:00**. `alembic current` reports 0010 at head and
`alembic check` reports **No new upgrade operations detected**. All 27 protected
table counts/content fingerprints and all six editorial hold records are unchanged.
Catalog remains 51 (45 generated, six held), with zero local receipts or visible entries.
The existing backup checksum was rechecked before applying the migration.

Alembic emitted a nonfatal SQLAlchemy `dialect_options` warning during schema
comparison; the command exited successfully and reported no schema differences.
No historical migration or application schema code was changed in response.

Target: **postgres@127.0.0.1:5432/chinese_learning**.
Expected effects: add the append-only `curated_vocabulary_local_reviews` table and
immutability trigger; extend the quality constraint with LOCAL_CODEX_REVIEWED;
extend the personal-vocabulary INSERT guard to require matching local evidence and
transaction opt-in. No catalog content/status or personal row is rewritten/deleted.
Migration history 0001–0009 remains unchanged. Catalog count should stay **51**.

Exact migration command executed following that confirmation:

```powershell
# Explicit confirmation already received in chat; do not request it again.
& $python -m alembic upgrade 0010_local_codex_review
if ($LASTEXITCODE -ne 0) { throw 'Migration failed; inspect current and fix forward' }
& $python -m alembic current
if ($LASTEXITCODE -ne 0) { throw 'Migration inspection failed' }
& $python -m alembic check
if ($LASTEXITCODE -ne 0) { throw 'Schema check failed' }
& $python "$deploymentRoot\verify.py" --revision 0010_local_codex_review --catalog 51 --local 0 --visible 0 --output "$deploymentRoot\post-migration-coverage.json"
if ($LASTEXITCODE -ne 0) { throw 'Preservation verification failed' }
```

Expected: head 0010, Alembic reports no new upgrade operations, 51 unchanged catalog
records, six unchanged holds, 27 protected tables unchanged and no local receipts.
The read-only verifier passed both before and after this migration. Results are in
`backend/.vocabulary-pipeline/phase403-deploy-20261026-a8f3/post-migration-coverage.json`.

## 5. NEW preview after migration — executed and inspected

The new preview is bound to **0010_local_codex_review**. All 2,482 proposed changes
are identical to the previously inspected actions: **2,437 inserts + 45 acceptances**,
zero conflicts and nineteen unchanged exclusions. Database identity and all review
evidence match. The new confirmation differs from the pre-migration token:

`LOCAL-CODEX-7d667d17e762196dcebea1fbd06437a00cf44fc71ba0ed87b564b6e3c1e3675f`

Files: `post-migration-plan.json` and `post-migration-preview-inspection.json` in
the session's ignored deployment directory. The following preview commands are safe
to rerun, but any changed plan must be inspected and explicitly reconfirmed for import.

```powershell
& $python -m scripts.local_codex_vocabulary plan --checkpoint $reviewRoot --database-env LOCAL_VOCABULARY_DATABASE_URL --output "$deploymentRoot\post-migration-plan.json"
if ($LASTEXITCODE -ne 0) { throw 'Post-migration preview failed' }
$plan = Get-Content "$deploymentRoot\post-migration-plan.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$plan.database
$plan.migrations
$plan.changes | Group-Object action | Select-Object Name,Count
$plan.changes | Format-Table lexical_key,action,incoming_version,before -Wrap
$plan.coverage.excluded | Format-Table lexical_key,reason -Wrap
if ($plan.migrations.Count -ne 1 -or $plan.migrations[0] -ne '0010_local_codex_review') { throw 'Wrong revision' }
if ($plan.changes | Where-Object { $_.action -like '*CONFLICT' }) { throw 'Resolve conflicts first' }
```

Expected unchanged actions/counts but a **new** confirmation bound to 0010. Show the
actual resulting plan and target to the user before requesting import confirmation.

## 6. Explicitly confirmed atomic import/local approval — executed, passed

The user explicitly confirmed **IMPORT AND ACCEPT LOCAL chinese_learning** and
provided operator name **dxt**. Before writing, the target, inspected confirmation,
backup checksum and preservation baseline were rechecked successfully. Import then
committed atomically and returned `accepted_local: 2482`,
`production_AI_APPROVED_created: 0`. Do not rerun the completed import using its old
confirmation: the database state has changed and that token is stale.

Expected DB effects: 2,437 new catalog rows, 45 existing generated rows accepted,
2,482 matching local evidence receipts; 2,488 total catalog rows. Six protected DB
holds remain unchanged; thirteen unresolved drafts remain outside the database.
No account, session, saved word, mastery or progress table is an import target.

```powershell
$env:ENVIRONMENT = 'development'
$env:ALLOW_LOCAL_CODEX_REVIEWED_VOCABULARY = 'true'
$operator = 'dxt'
# Explicit confirmation received in chat before this command was executed.
& $python -m scripts.local_codex_vocabulary apply --checkpoint $reviewRoot --database-env LOCAL_VOCABULARY_DATABASE_URL --enable-local-codex-review --operator $operator --confirm $plan.confirmation
if ($LASTEXITCODE -ne 0) { throw 'Atomic import failed; generate and inspect a new plan' }
```

Expected `accepted_local: 2482`, `production_AI_APPROVED_created: 0`. Actual notes
automatically supply local evidence across all 50 batches; no confidence score,
provider model snapshot or paid API receipt is invented. The process-local flag
above does not by itself enable a separately running API process.

## 7. Counts, pending keys and preservation — executed, passed

Verified at **2026-10-26 11:07:45 +07:00**: 2,488 catalog records, 2,482 local
receipts and local statuses, six unchanged held rows, thirteen unresolved drafts
still absent, and all **27 protected tables unchanged**. Existing accounts, sessions,
personal vocabulary, mastery and progress match their original fingerprints.
All 2,482 receipts were additionally checked against the actual checkpoint evidence
and evidence checksum, and every receipt's `submitted_by` is **dxt**.

Before any learner save/login write test:

```powershell
& $python "$deploymentRoot\verify.py" --revision 0010_local_codex_review --catalog 2488 --local 2482 --visible 2482 --output "$deploymentRoot\post-import-coverage.json"
if ($LASTEXITCODE -ne 0) { throw 'Post-import coverage or preservation failed' }
```

Expected: all 2,482 current versions/checksums have matching local receipts, six
original holds unchanged, thirteen excluded keys absent, and all 27 protected-table
counts/fingerprints unchanged. Visibility here is the exact application predicate
using this process's explicit flag; HTTP/device checks below are still required.

## 8. Enable local API publication — configured and running

Only `ENVIRONMENT=development` and `ALLOW_LOCAL_CODEX_REVIEWED_VOCABULARY=true`
were set in the already ignored `backend/.env`; other settings were preserved.
The API was started hidden on loopback port 8000 (PID recorded in the ignored
`api-process-id.txt`; stdout/stderr in the same session directory). Startup performs
no database writes. A future restart reads the same persistent local configuration.
The command below is the equivalent foreground startup command; do not run it while
the current server owns port 8000.

Start the API with the same private target and explicit development settings:

```powershell
$env:DATABASE_URL = $env:LOCAL_VOCABULARY_DATABASE_URL
$env:ENVIRONMENT = 'development'
$env:ALLOW_LOCAL_CODEX_REVIEWED_VOCABULARY = 'true'
& $python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Keep that terminal running. A new terminal must repeat the configuration/setup as
needed; environment variables are process-specific. For persistent local settings,
use the untracked `backend/.env`, then restart the API. Production policy and
ALLOW_AI_APPROVED_VOCABULARY do not need changing.

## 9. Authenticated APIs and Android — partially verified, credentials/device pending

Swagger convenience update: open `http://127.0.0.1:8000/docs` and click **Authorize**.
Use the account email as **username**, enter **password**, leave client fields empty,
then click **Authorize** and **Close**. The new `/api/v1/auth/token` form adapter uses
the existing login service, validation and rate limiter; Swagger supplies the returned
Bearer token automatically. Clicking Authorize performs a real login/session write.
This change was tested without invoking a real login: 154 backend tests passed,
73 database-dependent tests skipped, lint/format and dependency checks passed, and
live OpenAPI/docs/health/missing-credential checks passed. All 27 protected tables
and deployed coverage were reverified unchanged afterward. API restart used the
repository's Windows-compatible `python -m app` entry point with private logging;
current logs are `swagger-api-stdout.log` and `swagger-api-stderr.log` in the ignored
deployment directory. Existing JSON login and Android authentication remain unchanged.

Read-only checks against the real deployed database passed: Chinese search for
材料, Vietnamese search for tài liệu and current detail return the same v2
LOCAL_CODEX_REVIEWED entry `f5357e42-4640-51d3-8856-79e7e948d5ca`, including the
corrected shōují example. The protected 厕所 detail is rejected with 404 by the real
catalog service. These were **service-level checks**, not authenticated HTTP tests.
Live HTTP health passed and missing-token dictionary search returned 401. OpenAPI
and Android Retrofit contracts match the search/detail/save routes and response
fields; Android renders the LOCAL_CODEX_REVIEWED source label. No device is connected,
so no on-device success is claimed. No session creation/refresh or save was executed.
Results are in `publication-verification.json` in the ignored session directory.

Use an existing unexpired access token. Do not print/store it. Login or refresh would
write session rows and therefore needs separate explicit authorization if necessary.

```powershell
$tokenSecret = Read-Host 'Existing development access token' -AsSecureString
$headers = @{ Authorization = 'Bearer ' + [System.Net.NetworkCredential]::new('', $tokenSecret).Password }
$base = 'http://127.0.0.1:8000/api/v1'
$me = Invoke-RestMethod "$base/auth/me" -Headers $headers
$me | Select-Object id,email
$q = [uri]::EscapeDataString('材料')
$search = Invoke-RestMethod "$base/dictionary/search?q=$q&limit=20&offset=0" -Headers $headers
$hit = $search.items | Where-Object simplified -eq '材料' | Select-Object -First 1
if (!$hit) { throw 'Reviewed word not searchable' }
$detail = Invoke-RestMethod "$base/dictionary/entries/$($hit.entry_id)" -Headers $headers
if ($detail.review_status -ne 'LOCAL_CODEX_REVIEWED' -or $detail.content_version -ne 2) { throw 'Wrong review/content version' }
$detail.examples
$qVi = [uri]::EscapeDataString('tài liệu')
Invoke-RestMethod "$base/dictionary/search?q=$qVi&limit=20&offset=0" -Headers $headers
```

Expected: authenticated identity matches the intended test account; 材料 is visible,
v2 LOCAL_CODEX_REVIEWED, with corrected example shōují. The protected 厕所 ID
`b58c0607-76a4-527c-a6ea-d77170d7dfd8` must return 404 from authenticated detail.
401 means token expired/missing; do not bypass authentication.

Saving is a **separate database write** to the displayed user's curated personal
vocabulary. First read existing status/detail and show the account, entry UUID and
expected effect to the user. Require explicit confirmation before the POST:

```powershell
$status = Invoke-RestMethod "$base/me/vocabulary/status?dictionary_entry_id=$($hit.entry_id)" -Headers $headers
$beforeSaved = $null
if ($status.saved_id) { $beforeSaved = Invoke-RestMethod "$base/me/vocabulary/$($status.saved_id)" -Headers $headers }
Write-Output ('Target: chinese_learning; account=' + $me.id + '; entry=' + $hit.entry_id)
$beforeSaved | Select-Object id,mastery_level,next_review_at,last_reviewed_at
if ((Read-Host 'Type SAVE VERIFIED ENTRY FOR DISPLAYED ACCOUNT') -cne 'SAVE VERIFIED ENTRY FOR DISPLAYED ACCOUNT') { throw 'Save not confirmed' }
$body = @{ dictionary_entry_id = $hit.entry_id } | ConvertTo-Json -Compress
$saved = Invoke-RestMethod "$base/me/vocabulary" -Method Post -Headers $headers -ContentType 'application/json' -Body $body
if (!$beforeSaved -and $saved.mastery_level -ne 0) { throw 'Unexpected initial mastery' }
if ($beforeSaved -and ($saved.mastery_level -ne $beforeSaved.mastery_level -or $saved.next_review_at -ne $beforeSaved.next_review_at -or $saved.last_reviewed_at -ne $beforeSaved.last_reviewed_at)) { throw 'Existing mastery/schedule changed' }
Invoke-RestMethod "$base/me/vocabulary/$($saved.id)" -Headers $headers
Remove-Variable headers,tokenSecret
```

Expected: one new save at mastery zero, or existing save reactivated without changing
mastery/review dates. Do not delete existing saves or clear app data as cleanup. Any
additional replay POST is another write and needs authorization. The preservation
baseline verifier intentionally runs before these authorized test writes.

Android uses the same `/api/v1/dictionary/search`, `/dictionary/entries/{id}` and
`/me/vocabulary` contracts. Once one USB device is connected:

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

Open **Học tập → Tra từ điển**, search 材料 and tài liệu, inspect the local review label
and corrected content. Saving from the device also requires approval for that user
write. Reuse an existing valid session; a new login needs session-write authorization.
No uninstall, app data clearing or database reset is needed.

## Recovery and completion boundary

If migration fails, inspect `alembic current` and fix forward; do not downgrade.
If import confirmation is stale or apply fails, rerun and inspect a new plan before
requesting another confirmation. Import/status/evidence writes are atomic. If a
connection outcome is uncertain, inspect current catalog/receipts first. Never clear
holds, patch review hashes to pass, truncate tables or restore over learner data.
To hide local publication, disable the local flag and restart; retain saved data.

Current coverage is **post-import with local API publication enabled**. Database
deployment and evidence/preservation checks passed. Authenticated HTTP verification
requires an existing valid token; actual Android verification requires a connected
device. Creating/refreshing a session or saving a word still requires the user's
separate explicit write confirmation after the account and effects are shown.
No automatic approval rejection occurred. Do not treat the import confirmation as
authorization for these additional writes.
