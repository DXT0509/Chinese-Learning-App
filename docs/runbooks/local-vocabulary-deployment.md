# Local chinese_learning deployment operator runbook

For the newly authorized direct Codex workflow, use
[the local Codex runbook](local-codex-vocabulary.md). The historical 0009/head
snapshot below predates additive migration 0010. Its paid-provider procedure
is optional and is not required for local Codex acceptance.

Verified read-only on 2026-10-25: `127.0.0.1:5432`, database `chinese_learning`,
role `postgres`, Alembic **0009_vocabulary_ai_review applied**. Repository head is
also 0009. No migration is currently needed. No database writes or paid API calls
were performed while preparing this runbook. A local-file-only deployment snapshot
was prepared and audited to verify the hold-preserving procedure below.

The original dataset has 2,500 written learning items and 2,501 pronunciation records
in 50 batches. Importing pending records can be completed independently of semantic
review. Publishing them still requires authentic generation provenance, genuine
independent review and explicit backend policy opt-in. No instruction below grants
permission for this agent to execute a paid or database-writing step.

**1. Open PowerShell and select the existing local database**

```powershell
Set-Location 'C:\Users\ADMIN\AndroidStudioProjects\ChineseLearningApp\backend'
$ErrorActionPreference = 'Stop'
$python = (Resolve-Path '.venv\Scripts\python.exe').Path
$env:PYTHONUTF8 = '1'
$env:PYTHONPATH = (Get-Location).Path

# Reuse the private backend configuration without printing its password.
$env:VOCABULARY_DATABASE_URL = (& $python -c 'from app.core.config import get_settings; print(get_settings().database_url)')
if ($LASTEXITCODE -ne 0) { throw 'Cannot read backend database configuration' }
& $python -c "import os; from sqlalchemy.engine import make_url; u=make_url(os.environ['VOCABULARY_DATABASE_URL']); assert u.drivername=='postgresql+psycopg' and u.database=='chinese_learning' and u.host in ('127.0.0.1','localhost') and (u.port or 5432)==5432; print('Selected local chinese_learning on port 5432')"
if ($LASTEXITCODE -ne 0) { throw 'Wrong target; inspect backend/.env privately' }
$env:DATABASE_URL = $env:VOCABULARY_DATABASE_URL

$operationDir = Join-Path (Get-Location).Path ('.vocabulary-pipeline\local-deploy-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $operationDir | Out-Null
$dataset = Join-Path $operationDir 'dataset'
$env:VOCAB_DEPLOY_DIR = $operationDir
$env:VOCAB_DEPLOY_DATASET = $dataset

& $python -m alembic heads
& $python -m alembic current
if ($LASTEXITCODE -ne 0) { throw 'Migration inspection failed' }
```

Both Alembic commands should identify `0009_vocabulary_ai_review`. These inspect
state; do not run `upgrade`, `downgrade`, a reset, or database recreation as part of
this deployment. If current changes, stop and inspect the new state.

**2. Understand and preserve the exact hold conflict**

| Field | Existing PostgreSQL revision | Incoming original dataset |
| --- | --- | --- |
| lexical_key | 厕所\|ce4 suo3 | 厕所\|ce4 suo3 |
| vocabulary UUID | b58c0607-76a4-527c-a6ea-d77170d7dfd8 | same deterministic UUID |
| content_version | 1 | 1 |
| review_status | NEEDS_REVIEW | GENERATED_UNREVIEWED |
| checksum | 8cacc9b365454fb299bc079f50eb04cf3499ed3ea08c037628ee28229ee60026 | 8c34ca8ead7e0c31373c408222690ef5c49d9aefae83bb493870fad09cee71f6 |
| batch | gemini-vi-level-0-batch-001-c0c177afc29f | L0-B001, level-0-batch-001.converted.jsonl |

All linguistic fields match: simplified `厕所`, numbered Pinyin `ce4 suo3`, rendered
Pinyin `cè suǒ`, noun, Level 0, Vietnamese `nhà vệ sinh`, no English meanings or
Sino-Vietnamese reading, and example `厕所在哪儿？` / `Cèsuǒ zài nǎer?` /
`Nhà vệ sinh ở đâu?`. Both use APP_CURATED and HSK_2_0 reference classification.
The status is included in the content checksum. This is not a harmless checksum
formatting discrepancy, and the existing hold must survive.

The original-source preview below is useful evidence and is expected to show
`IDENTICAL:50`, `VERSION_CONFLICT:1`, `INSERT:2450`. Its execute command would refuse:

```powershell
& $python -m scripts.curated_pipeline plan --database-env VOCABULARY_DATABASE_URL --output "$operationDir\original-plan.json"
if ($LASTEXITCODE -ne 0) { throw 'Original preview failed' }
```

The safe deployment amendment makes **only this draft version 2, NEEDS_REVIEW** in
a new snapshot. It changes no linguistic content, resolves no editorial issue,
retains its lexical key/UUID and preserves the historical revision. Original files
under `docs/datasets/original-zhvi/` stay unchanged. It does not grant approval.

```powershell
& $python ..\docs\runbooks\prepare_local_vocabulary.py --source ..\docs\datasets\original-zhvi --destination $dataset
if ($LASTEXITCODE -ne 0) { throw 'Snapshot preparation failed; do not import' }
& $python -m scripts.curated_pipeline --dataset $dataset audit --output "$operationDir\deployment-audit.json"
if ($LASTEXITCODE -ne 0) { throw 'Deployment integrity failed' }
```

Expected: PASSED, 2,501 records, 2,500 written items, **six** holds, no duplicate
lexical identities. Missing example `谁|shui2` remains reported. The helper updates
the snapshot's Batch 001 staging JSONL, converted JSONL, conversion provenance,
manifest, review input, lexical registry and coverage hash consistently. Its
`deployment-amendment.json` records the original hashes and exact version/status
change. It asserts that generator claims remain unverified. Do not rerun any
vocabulary generator/build script.

**3. Preview all import changes, then explicitly confirm import**

This exact preview was rehearsed read-only against the current local database:

```powershell
& $python -m scripts.curated_pipeline --dataset $dataset plan --database-env VOCABULARY_DATABASE_URL --output "$operationDir\import-plan.json"
if ($LASTEXITCODE -ne 0) { throw 'Import preview failed' }
$importPlan = Get-Content "$operationDir\import-plan.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$importPlan.database.identity | Format-List
$importPlan.database.action_counts | Format-List
$importPlan.per_batch_reconciliation | Format-Table
$importPlan.database.actions | Where-Object action -ne 'IDENTICAL' | Format-Table lexical_key,action,source_version,existing_version
```

Expected initially: **50 IDENTICAL, 1 NEW_REVISION, 2,450 INSERT**. L0-B001 has 50
identical records and the one held new revision; the remaining 49 batches contain
the new records. Only catalog/batch/meaning/example/revision tables are targeted.
Accounts, sessions, saved-word associations, mastery and schedules are not written.
If any conflict remains or the identity differs, stop; confirmation cannot override it.

Before confirming, take a local read-only PostgreSQL custom-format backup. The
following command passes credentials through the child environment rather than
printing a URL or placing a password in command arguments:

```powershell
@'
import os, subprocess
from pathlib import Path
from sqlalchemy.engine import make_url
u = make_url(os.environ['VOCABULARY_DATABASE_URL'])
backup = Path(os.environ['VOCAB_DEPLOY_DIR']) / 'chinese_learning-before-import.dump'
if backup.exists():
    raise ValueError('Backup output must be new')
env = dict(os.environ, PGHOST=u.host, PGPORT=str(u.port or 5432),
           PGUSER=u.username, PGDATABASE=u.database, PGPASSWORD=u.password or '')
subprocess.run([r'C:\Program Files\PostgreSQL\18\bin\pg_dump.exe',
                '-Fc', '-f', str(backup)], env=env, check=True)
print('Backup created:', backup.name, backup.stat().st_size, 'bytes')
'@ | & $python -
if ($LASTEXITCODE -ne 0) { throw 'Backup failed; do not import' }

# DATABASE WRITE: operator executes this block only after reviewing import-plan.json.
if ((Read-Host 'Type IMPORT chinese_learning to approve the displayed write plan') -cne 'IMPORT chinese_learning') { throw 'Import not confirmed' }
& $python -m scripts.curated_pipeline --dataset $dataset execute --database-env VOCABULARY_DATABASE_URL --confirm $importPlan.confirmation_token --output "$operationDir\import-result.json"
if ($LASTEXITCODE -ne 0) { throw 'Import stopped; follow recovery instructions below' }
```

Do not reuse a token from this document or an older report. Execute recomputes the
plan before writing. Expected result with the current snapshot: 50 committed batch
receipts, 2,501 catalog records, 2,495 GENERATED_UNREVIEWED and six NEEDS_REVIEW,
zero AI/HUMAN approvals and zero published entries. All are still pending.

**4. Recover actual Gemini generation evidence and correct metadata**

Currently missing: authenticated historical generation records identifying the model
that actually authored each batch, its actual version identifier, and a trace from
that response/transcript to the corresponding original artifact. A filename starting
with `gemini`, a batch import label, current model availability, and an operator's
guess do not establish that history.

`generator_core.py` defaults `google` / `gemini-3.8-flash` / `2026-10` without making
a Gemini request. `generate_batch_002.py` also embeds that identity. The 49 later
batch manifests and all 50 review-input files repeat these unverified claims; Batch
001's historical manifest has no generator identity. None of these establishes that
the named model exists or was the author. Do not record `2026-10` as a model version
merely because it is an authoring month.

Recover the original Gemini API responses/request logs or original UI session export
that actually identifies the model. For Gemini API responses, `modelVersion` reports
the model version and `responseId` identifies the response, per Google's
[GenerateContentResponse documentation](https://ai.google.dev/api/generate-content).
Retain original response content so lineage can be checked, and keep request metadata
if available. Never fabricate missing response IDs or timestamps. A UI export showing
only a marketing name may be insufficient for this repository's mandatory version
field. If no authentic version/lineage can be recovered, **stop semantic review**:
under the current policy there is no truthful metadata value to fill in. The pending
database import above can remain; provenance does not magically become verified.

Create `$operationDir\generation-receipts\L0-B001.json` through `L5-B025.json`,
following the 50 batch keys in coverage-manifest.json. Each file must be the authentic
Gemini GenerateContentResponse for that batch, not a JSON object invented to satisfy
this example. For multiple responses per batch or UI evidence, assemble the ledger
manually using the schema in the existing bulk pipeline guide and retain all authentic
source evidence. Do not force other evidence formats into this single-response recipe.
If history identifies another author/provider for any batch, record that actual identity
in its ledger entry; do not relabel it Gemini to fit the recipe. Do not run the recipe
unless all 50 receipts genuinely establish Gemini authorship and the mappings are verified.

After independently verifying every receipt's correspondence to its ORIGINAL batch,
the following LOCAL-ONLY command builds the byte-bound ledger and corrects generator
metadata in the deployment copy. It intentionally fails on missing modelVersion or
responseId. It uses the returned modelVersion as the exact model and version identifier;
it does not infer a separate internal build. The amendment links the mechanically
adapted Batch 001 snapshot to its original Gemini-authored linguistic content.

```powershell
New-Item -ItemType Directory -Path "$operationDir\generation-receipts" -Force | Out-Null
# Copy authentic historical responses into that directory before continuing.
$env:VOCAB_PROVENANCE_OPERATOR = Read-Host 'Your name as the provenance-verifying operator'
if ((Read-Host 'Type VERIFIED only after checking all 50 receipt-to-original-batch mappings') -cne 'VERIFIED') { throw 'Provenance not verified' }
@'
import json, os
from pathlib import Path
from app.schemas.curated_review import ModelIdentity
from app.services.curated_audit import scan_dataset
from app.services.curated_import import digest, load_records
from app.services.curated_review import review_inputs
from app.services.curated_reviewer import verified_generators
root = Path(os.environ['VOCAB_DEPLOY_DATASET'])
operation = Path(os.environ['VOCAB_DEPLOY_DIR'])
operator = os.environ['VOCAB_PROVENANCE_OPERATOR'].strip()
assert operator
audit, catalog = scan_dataset(root)
assert audit['structural_integrity'] == 'PASSED'
ledger = {'operator': operator, 'batches': {}}
for batch in audit['files']:
    receipt = operation / 'generation-receipts' / (batch['batch'] + '.json')
    response = json.loads(receipt.read_text(encoding='utf-8-sig'))
    version, response_id = response.get('modelVersion'), response.get('responseId')
    assert isinstance(version, str) and version.strip()
    assert isinstance(response_id, str) and response_id.strip()
    identity = ModelIdentity(provider='google', model=version, version=version)
    ledger['batches'][batch['batch']] = {
        'artifact_sha256': batch['sha256'], 'generator': identity.model_dump(),
        'evidence_file': receipt.relative_to(operation).as_posix(),
        'evidence_sha256': digest(receipt.read_bytes()),
        'verification_note': 'Operator verified authentic Gemini response-to-original-batch lineage; deployment-amendment.json records the nonlinguistic version/status adaptation for L0-B001.',
    }
ledger_path = operation / 'generator-ledger.json'
with ledger_path.open('x', encoding='utf-8') as f:
    json.dump(ledger, f, ensure_ascii=False, indent=2)
identities = verified_generators(root, audit, ledger_path)
# Correct only snapshot metadata. Original datasets and evidence bytes stay intact.
coverage = json.loads((root / 'coverage-manifest.json').read_text(encoding='utf-8'))
for b in coverage['batches']:
    slug = f"level-{b['level']}-batch-{b['batch_number']:03d}"
    manifest_path = root / (slug + '.manifest.json')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest['generator'] = identities[b['batch_key']].model_dump()
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    _, rows = load_records(root / b['artifact_file'])
    requests = review_inputs(rows, identities[b['batch_key']], catalog)
    (root / (slug + '.review-input.jsonl')).write_text('\n'.join(r.model_dump_json() for r in requests)+'\n', encoding='utf-8')
final, _ = scan_dataset(root)
assert final['structural_integrity'] == 'PASSED'
print('Ledger bound to 50 artifacts; snapshot metadata corrected; no provider called')
'@ | & $python -
if ($LASTEXITCODE -ne 0) { throw 'Provenance preparation failed; do not review' }
```

The ledger is an operator assertion backed by retained evidence, not a provider signature.
The audit scanner will still say UNVERIFIED_MANIFEST_ASSERTION because it only scans
dataset artifacts; the reviewer separately validates the ledger's byte bindings.
Do not reinterpret that structural scanner label as a new linguistic review failure.
No vocabulary JSONL content/version changes are needed just to correct generator
metadata. The registry and coverage only need the versioned hold amendment from step 2.
Historical generator scripts need no execution or guessed default replacement.

**5. Configure the actual independent reviewer and budget**

Only **direct Anthropic Messages API** is implemented by `AnthropicReviewer`. There
is no automated Gemini, OpenAI, Bedrock, Vertex, proxy, or alternative-provider adapter
in this CLI. Offline `scripts.curated_review` can accept externally obtained strict
ReviewResult files, but that is a different exchange path, not an automatic adapter.
Use a Claude Console API key, not a chat subscription credential or a Gemini API key.

```powershell
$env:VOCAB_REVIEW_PROVIDER = 'anthropic'
$env:VOCAB_REVIEW_MODEL = 'claude-sonnet-5-5'
# Optional second, DIFFERENT model for independent review of the first model's corrections.
$env:VOCAB_REVIEW_SECONDARY_MODEL = 'claude-haiku-5-5'
$reviewSecret = Read-Host 'Anthropic API key from your secret manager' -AsSecureString
$env:ANTHROPIC_API_KEY = [System.Net.NetworkCredential]::new('', $reviewSecret).Password
```

These are currently documented model IDs, not claims of an invocation already made:
[Sonnet 5.5](https://platform.claude.com/docs/en/models/sonnet-5-5/overview) and
[Haiku 5.5](https://platform.claude.com/docs/en/models/haiku-5-5/overview). Confirm
availability in your account before authorizing a pilot. The exact response model
must match the configured ID. Choose a model compatible with text-only JSON replies;
thinking/tool blocks, truncated answers or model aliases returning a different ID
are rejected by this adapter. No real compatibility call has been made here.

Anthropic is a different provider from Gemini. A different version of the SAME
provider/model alone is insufficient. A reviewer that proposes corrected content
becomes that draft's generator; the other configured model must review that content.
Without a secondary model, suggested corrections remain unresolved. All nine aspects,
confidence >=0.95, exact checksum/version and no unresolved blocking finding remain
mandatory. Model confidence is not proof, and cheap models are not guaranteed to
give adequate linguistic assessments. Existing holds cannot be overridden by a
pass on the held version: they require genuinely corrected, newly versioned content.

Set these variables in the shell running review. This adapter reads `os.environ`;
putting reviewer variables only in `backend/.env` does not configure it. Never commit
the key. Set the spending ceiling for the key's dedicated workspace in the
[Claude Console workspace controls](https://platform.claude.com/docs/en/manage-claude/workspaces).

Cost planning: the first actual global-catalog request is approximately 42,930
characters / 54,026 UTF-8 bytes before the system prompt/schema. Every record includes
all 2,501 lexical keys; the CLI is synchronous per record, **not** the discounted
provider Batch API, and it does not configure prompt caching. Do not price this as
50 tiny requests. There are 2,501 initial calls plus bounded retry/correction calls.

At current Sonnet 5.5 base rates of $2/million input and $10/million output tokens,
an illustrative 15k–30k input and 1k–4k output tokens per call gives roughly
**$100–$250 for one full pass**, or **$200–$500 for two attempts per record** if all
calls were priced at those rates. This is an assumption-based estimate, not a quote
or a hard cap; actual tokenization, selected secondary model and usage determine cost.
See [current provider pricing](https://platform.claude.com/docs/en/about-claude/pricing).
Measure the pilot receipts' `usage` before choosing the full-run budget.

`--max-calls` limits lifetime reservations for one run directory;
`--max-output-tokens` limits each response, and `--attempts` limits each record's
initial/retry/correction chain. None is a dollar limit or input-token cap. With
5,002 calls and 4,096 output tokens, the output ceiling is 20,488,192 tokens.
Use the provider workspace spend limit as well. Do not increase budgets automatically.

**6. Authorize a small pilot, then separately authorize all 50 batches**

These commands are supplied for later operator execution. They were NOT run.
The pilot spends at most three calls; it may stop within the first batch. A
max-call pilot does not select three entire batches.

```powershell
$pilotDir = Join-Path $operationDir 'review-pilot'
if ((Read-Host 'Type PAY PILOT to authorize up to 3 review calls') -cne 'PAY PILOT') { throw 'Paid pilot not authorized' }
& $python -m scripts.curated_pipeline --dataset $dataset review --provenance "$operationDir\generator-ledger.json" --run-dir $pilotDir --max-calls 3 --max-output-tokens 4096 --attempts 2 --output "$operationDir\pilot-summary.json"
if ($LASTEXITCODE -ne 0) { throw 'Pilot failed; inspect receipts before any more spending' }
Get-Content "$operationDir\pilot-summary.json" -Raw -Encoding UTF8

# Local receipt inspection only; never prints the API key.
Get-ChildItem $pilotDir -Filter '*.receipt.json' | ForEach-Object {
    $receipt = Get-Content $_.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
    $receipt.response | Select-Object id,model,stop_reason,usage
}
```

Inspect actual assessments, findings, nine-aspect coverage, schema errors, returned
model IDs and spend. The summary can exit successfully with unresolved records;
exit zero does not mean all words were reviewed or approved. The first records
include existing editorial holds, so reviewer decisions may not be publishable.

The run config is immutable. Do not enlarge the pilot's budget in place. The full
run uses a NEW directory and will repeat the pilot records, incurring those calls
again. Budget that explicitly; this CLI does not merge paid receipts across runs.

```powershell
$reviewDir = Join-Path $operationDir 'review-all-50'
if ((Read-Host 'Type PAY FULL to authorize up to 5002 calls under the workspace spending limit') -cne 'PAY FULL') { throw 'Full paid run not authorized' }
& $python -m scripts.curated_pipeline --dataset $dataset review --provenance "$operationDir\generator-ledger.json" --run-dir $reviewDir --max-calls 5002 --max-output-tokens 4096 --attempts 2 --output "$operationDir\review-all-summary.json"
if ($LASTEXITCODE -ne 0) { throw 'Full review stopped; inspect recovery guidance' }
Get-Content "$operationDir\review-all-summary.json" -Raw -Encoding UTF8
```

This traverses all 50 batches and all 2,501 records. At most two attempts per record
include correction re-review; unresolved records remain pending and retain receipts.
The 5,002-call ceiling does not guarantee that spending limits or rate limits permit
the run to finish. Check summary counts, invalid/error files and all original keys.

**7. Import independently reviewed corrections, then automatically submit evidence**

Initial import was unapproved. If review produced higher-version requests, import
those exact drafts before submission. Keep the SAME `$dataset` and `$reviewDir`.
Old checksums cannot approve new drafts. The CLI reconstructs evidence from actual
stored provider receipts; standalone result files are insufficient for this path.

```powershell
& $python -m scripts.curated_pipeline --dataset $dataset plan --database-env VOCABULARY_DATABASE_URL --review-dir $reviewDir --output "$operationDir\reviewed-import-plan.json"
if ($LASTEXITCODE -ne 0) { throw 'Reviewed-content preview failed' }
$reviewedPlan = Get-Content "$operationDir\reviewed-import-plan.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$reviewedPlan.database.identity | Format-List
$reviewedPlan.database.action_counts | Format-List
if ((Read-Host 'Type IMPORT REVIEWED to approve this reviewed-content write plan') -cne 'IMPORT REVIEWED') { throw 'Reviewed import not confirmed' }
& $python -m scripts.curated_pipeline --dataset $dataset execute --database-env VOCABULARY_DATABASE_URL --review-dir $reviewDir --confirm $reviewedPlan.confirmation_token --output "$operationDir\reviewed-import-result.json"
if ($LASTEXITCODE -ne 0) { throw 'Reviewed-content import stopped' }

& $python -m scripts.curated_pipeline --dataset $dataset plan --database-env VOCABULARY_DATABASE_URL --operation submit --review-dir $reviewDir --output "$operationDir\submit-plan.json"
if ($LASTEXITCODE -ne 0) { throw 'Review submission preview failed' }
$submitPlan = Get-Content "$operationDir\submit-plan.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$submitPlan.database.identity | Format-List
$submitPlan.database.write_plan | Format-List
$operatorName = Read-Host 'Named submitting operator'
if ((Read-Host 'Type SUBMIT REVIEWS to approve appending genuine evidence and applying review decisions') -cne 'SUBMIT REVIEWS') { throw 'Submission not confirmed' }
& $python -m scripts.curated_pipeline --dataset $dataset execute --database-env VOCABULARY_DATABASE_URL --operation submit --review-dir $reviewDir --operator $operatorName --confirm $submitPlan.confirmation_token --output "$operationDir\submit-result.json"
if ($LASTEXITCODE -ne 0) { throw 'Review submission stopped' }
```

This calls the existing review service, not SQL status updates. Valid pending and
rejected decisions are also retained. Each record submission has its own transaction.
Review IDs derive from actual provider message IDs; identical replays are no-ops.
HUMAN_APPROVED records cannot be overwritten. A pass on any still-held draft is
effectively NEEDS_REVIEW. Missing examples remain a publication blocker. Corrections
must resolve actual findings, not merely erase status/version fields to reach 100%.

**8. Explicitly enable local AI publication and verify Android**

After genuine evidence submission, stop the existing port-8000 backend with Ctrl+C
in its terminal. In a SEPARATE backend terminal, start exactly one API:

```powershell
Set-Location 'C:\Users\ADMIN\AndroidStudioProjects\ChineseLearningApp\backend'
$env:DATABASE_URL = (& .venv\Scripts\python.exe -c 'from app.core.config import get_settings; print(get_settings().database_url)')
$env:ALLOW_AI_APPROVED_VOCABULARY = 'true'
& .venv\Scripts\python.exe -m app
```

That is a local process setting, not a production change. A restart is necessary;
editing `.env` or setting a variable in another terminal does not update an existing
backend. Back in the ORIGINAL operator PowerShell, which still holds `$operationDir`,
`$dataset`, `$reviewDir` and the selected URL, set the same policy before reporting:

```powershell
$env:ALLOW_AI_APPROVED_VOCABULARY = 'true'
& $python -m scripts.curated_pipeline --dataset $dataset report --database-env VOCABULARY_DATABASE_URL --review-dir $reviewDir --output "$operationDir\final-coverage.json"
if ($LASTEXITCODE -ne 0) { throw 'Final coverage report failed' }
$coverage = Get-Content "$operationDir\final-coverage.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$coverage.database.stages | Format-List
$coverage.database.actual_review_models | Format-List
$coverage.database.linguistic_failure_categories | Format-List
```

The count uses that reporting process's policy, so also verify HTTP. To avoid making
new login/session writes solely for this check, use an unexpired existing bearer
token from your normal development session. Do not print/store it in the runbook.
If unavailable, signing in normally is a separate authenticated action after write
authorization, not part of the read-only verification performed for this runbook.

```powershell
$tokenSecret = Read-Host 'Existing unexpired development access token' -AsSecureString
$httpHeaders = @{ Authorization = 'Bearer ' + [System.Net.NetworkCredential]::new('', $tokenSecret).Password }
Invoke-RestMethod 'http://127.0.0.1:8000/api/v1/health'
# Pick an ACTUAL currently AI_APPROVED word from submitted evidence or the UI.
$approvedWord = Read-Host 'Actual approved Simplified word to verify'
$q = [uri]::EscapeDataString($approvedWord)
$search = Invoke-RestMethod "http://127.0.0.1:8000/api/v1/dictionary/search?q=$q&limit=20&offset=0" -Headers $httpHeaders
$search.items | Format-Table entry_id,simplified,primary_pinyin,short_vi_meaning
$hit = $search.items | Where-Object simplified -eq $approvedWord | Select-Object -First 1
if (!$hit) { throw 'Approved word is not searchable; check evidence, API setting and database' }
$detail = Invoke-RestMethod "http://127.0.0.1:8000/api/v1/dictionary/entries/$($hit.entry_id)" -Headers $httpHeaders
$detail | Select-Object simplified,review_status,content_version,active
Remove-Variable httpHeaders,tokenSecret
```

Expect the actual approved word, usable Vietnamese meaning, detail AI_APPROVED and
active true. Choose an unresolved held UUID from the report and confirm its detail
returns 404; a search term alone may match other approved records. A 401 means the
session expired, not that vocabulary publication failed. Do not use fake login.

For the USB Android workflow, in a root/Android PowerShell:

```powershell
Set-Location 'C:\Users\ADMIN\AndroidStudioProjects\ChineseLearningApp'
$adb = "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe"
& $adb devices -l
& $adb -d reverse tcp:8000 tcp:8000
& $adb -d reverse --list
Set-Location android
# Only needed if the installed APK is outdated or has a different API base URL.
.\gradlew.bat installDebug '-PDEV_API_BASE_URL=http://127.0.0.1:8000/'
& $adb -d shell am start -n com.example.chineselearningapp/.MainActivity
```

Use the existing signed-in account. Open **Học tập → Tra từ điển**, search the same
approved Simplified word, open detail, verify Pinyin/Vietnamese/examples, and save
it to the personal vocabulary list if desired (saving is a user write). Verify a
held item stays unavailable. Existing personal mastery/schedules should be retained.
Do not uninstall the app or clear its data. `-d` assumes one USB device; with multiple
devices use the selected `-s` serial. Server vocabulary changes alone need no APK
rebuild when the installed client already points to this API. No Android device
validation has been claimed from unit tests or this runbook.

**9. Failure recovery**

| Failure | Exact recovery |
| --- | --- |
| Output already exists | Keep the prior report; choose a new output filename. Preparation requires a new destination. Do not overwrite receipts. |
| Original source still conflicts | Confirm every command includes `--dataset $dataset`; importing the original v1 snapshot is intentionally refused. |
| Preparation/audit fails | Do not import the partial snapshot. Keep it for inspection and prepare a new destination after correcting the cause. |
| Token stale or import interrupted | Generate a NEW plan on the same dataset and DB, inspect remaining actions, explicitly confirm its new token, execute with a new output filename. Committed batches remain intact and identical batches skip. No rollback/reset command is needed. |
| Genuine generator history unavailable | Leave data pending. Do not copy default strings into a ledger as evidence. |
| Ledger creation partly failed | Keep partial artifacts. Correct missing authentic evidence first; use a new ledger filename or operation directory and update commands consistently. Do not edit receipts to fabricate metadata. |
| Provider error / reservation without receipt | Stop spending. An invocation may have happened. The same directory deliberately stops at that unknown outcome; do not delete reservations to reclaim budget. The current CLI has no skip/continue switch for this case. After investigating, a separately authorized NEW run directory restarts review and repeats prior calls. Budget repeats explicitly; preserve the old run. |
| Review process stopped after saved receipts | Re-run the identical review config/run directory with a NEW summary output filename. Stored receipts are revalidated without repeating completed paid calls. |
| `run.lock` left by a crash | First establish the reviewer process is no longer running. Remove only that stale lock, retaining all reservations/receipts. Never remove a live process's lock. |
| Invalid JSON, model mismatch, thinking blocks or truncation | Inspect `.invalid.json` and raw receipt. No approval is accepted. Changing model/token/attempt settings requires a new run directory and fresh spending approval. |
| Review budget exhausted / unresolved entries | They remain pending. Configuration cannot be enlarged in place. Inspect findings; authorize a separate bounded run only if warranted. |
| Submission interrupted | Re-plan submit with the SAME review directory, inspect DB changes, explicitly confirm the new token, execute with new output. Existing IDs replay safely; stale checksum/version errors require new review, not modified old evidence. |
| Approval absent from Android | First verify actual HTTP search/detail with an unexpired session. Then check backend restart/flag, current checksum/version evidence, active holds, ADB reverse, API base URL and installed APK. |
| Publication must be withdrawn | Set ALLOW_AI_APPROVED_VOCABULARY=false and restart the API. This hides AI entries while retaining catalog evidence and user state. |

The backup is for a deliberate recovery investigation. Do not automatically restore
it over `chinese_learning`: that could overwrite user activity created after backup.
Per-batch transactions and read-only reconciliation are the normal recovery path.

At the end, distinguish imported, reviewed, approved and actually search-visible
counts. Six holds and one missing example exist before linguistic review; nobody
can promise 2,500 published words merely because all source records were imported.
Remove the API credential from the operator shell when done:

```powershell
Remove-Item Env:ANTHROPIC_API_KEY -ErrorAction SilentlyContinue
Remove-Variable reviewSecret -ErrorAction SilentlyContinue
```
