# Phase 4.0.2 bulk vocabulary pipeline

For local deployment, use the [ordered operator runbook](runbooks/local-vocabulary-deployment.md).
It includes a tested local-file-only version 2 snapshot procedure that preserves the
existing 厕所 hold, exact confirmation commands, provenance recovery, paid-review
authorization gates and Android verification. The original-source conflict below
remains accurate; the new snapshot resolves import compatibility without removing it.

The pipeline extends the existing importer and review service. It never migrates a
database, resets data, grants human approval, or changes the publication setting.
No Android or SRS behavior is added. There are no new dependencies or migrations.

Actual development status: **BLOCKED for genuine semantic review and bulk writes**.
See [integrity audit](datasets/phase4.0.2-integrity-audit.json) and
[database reconciliation and coverage](datasets/phase4.0.2-coverage-report.json).
These are snapshots; regenerate the read-only plan before any write.

| Stage | Development snapshot |
| --- | --- |
| GENERATED | 2,501 pronunciation records / 2,500 distinct written learning items |
| STRUCTURALLY_VALIDATED | 2,501 across all 50 batches |
| Catalog identities already present | 51, all from the historical Batch 001 import |
| IMPORTED with exact source checksum/version | 50 |
| Conflicting existing records | 1: 厕所\|ce4 suo3, version 1 |
| New records awaiting import | 2,450 |
| AI_REVIEWED / AI_APPROVED / HUMAN_APPROVED / PUBLISHED | 0 / 0 / 0 / 0 |
| Existing catalog pending | 51: 45 GENERATED_UNREVIEWED, 6 NEEDS_REVIEW |
| Existing catalog rejected | 0 |
| Migration | 0009_vocabulary_ai_review (also the repository head) |

The distinct-written-item distribution is 100/100/150/300/600/1,250 at Levels 0–5.
Level 0 has 101 pronunciation records because 谁 has two readings. 谁|shui2 has no
example. Five source records carry editorial holds. The database additionally holds
厕所|ce4 suo3: its revision payload is NEEDS_REVIEW while the source says
GENERATED_UNREVIEWED. This is a real checksum conflict, even though the linguistic
fields match. Do not replace it with version 1 or remove its hold. A correction must
use a new content version and preserve unresolved issues; linguistic changes need
review on the new checksum. No source artifacts were rewritten to conceal this conflict.

All source hashes, historical Batch 001 conversion/mappings, stable UUIDs, review
input contents, per-record manifest checksums and cumulative registry reconcile.
Exact form and shared Vietnamese gloss candidates are recorded for semantic review;
they are heuristics and are never merged automatically.

Generator provenance is **unverified**. `generator_core.py` accepts supplied text
and defaults provider/model/version strings. Neither those defaults nor their copies
in manifests and review inputs establish the model that authored the vocabulary.
No generation receipt was available. No reviewer credentials/model/budget were
configured for this run. No real semantic review or paid API call occurred.

Run commands from `backend/` in PowerShell. Output files must be new; create their
parent directories first. Local receipts are stored under the ignored directory.

```powershell
New-Item -ItemType Directory -Force .vocabulary-pipeline | Out-Null
.venv/Scripts/python -m scripts.curated_pipeline audit --output .vocabulary-pipeline/audit.json

# Select a URL explicitly; the CLI never silently falls back to the development DB.
$env:VOCABULARY_DATABASE_URL = '<operator-selected postgresql+psycopg URL>'
.venv/Scripts/python -m scripts.curated_pipeline plan --database-env VOCABULARY_DATABASE_URL --output .vocabulary-pipeline/import-plan.json
```

Read the plan's server/database/role, migration, conflicts, file hashes and per-batch
actions. Missing migration head blocks execution; apply reviewed migrations separately.
The operator must explicitly approve development writes before running execute. A token
does not override conflicts. Re-run plan after resolving them or after an interrupted run.

```powershell
$pipelineConfirmation = (Get-Content .vocabulary-pipeline/import-plan.json -Raw | ConvertFrom-Json).confirmation_token
# Run only after explicit approval of this concrete database/write plan:
.venv/Scripts/python -m scripts.curated_pipeline execute --database-env VOCABULARY_DATABASE_URL --confirm $pipelineConfirmation --output .vocabulary-pipeline/import-result.json
```

Each batch uses the existing importer, its transaction and advisory lock. An immutable
batch ID includes its full SHA-256. A successful commit prints a progress receipt.
The database is authoritative after a lost checkpoint: repeat execution skips identical
batches but verifies their current catalog checksums/versions. Same-version changes
and inconsistent receipts fail. Current user tables, accounts, saved words, mastery and
schedules are untouched. A concurrent conflicting revision fails under the importer lock.
This is not an all-50-batches transaction: already committed batches survive a later failure.

To review, first establish actual generator identity for **every** batch. Create a local
ledger with the following shape, replacing placeholders from authentic generation
records; do not copy manifest claims as proof. Include all 50 batch keys.

```json
{
  "operator": "<person verifying generation provenance>",
  "batches": {
    "L0-B001": {
      "artifact_sha256": "<SHA-256 of converted import artifact>",
      "generator": {
        "provider": "<actual provider>",
        "model": "<actual generating model>",
        "version": "<actual version from generation record>"
      },
      "evidence_file": "generation-receipts/batch001.json",
      "evidence_sha256": "<SHA-256 of authentic local generation evidence>",
      "verification_note": "<how this evidence establishes identity and artifact lineage>"
    }
  }
}
```

Receipt paths stay below the ledger directory. The pipeline verifies byte bindings,
not authenticity of arbitrary operator-supplied files. Local maintenance access remains
a trust boundary, as in Phase 4.0.1. Protect receipts and credentials. Obtain authentic
generation history rather than assigning a guessed model to legacy content.

The implemented provider is the official
[Anthropic Messages API](https://platform.claude.com/docs/en/api/messages/create).
Use an actual exact model identifier available to your account. There is no default
model or provider fallback. The response's model must equal the configured model;
the exact returned identifier is recorded as its version identifier, not a guessed
internal model build. Same provider/model with a different version is not independent.

```powershell
$env:VOCAB_REVIEW_PROVIDER = 'anthropic'
$env:ANTHROPIC_API_KEY = '<credential from your secret manager>'
$env:VOCAB_REVIEW_MODEL = '<exact provider-returned model identifier>'
# Optional: a DIFFERENT model to independently review proposed corrections.
$env:VOCAB_REVIEW_SECONDARY_MODEL = '<different exact model identifier>'

# Example bounded pilot: at most 10 paid calls, each with <=4096 output tokens.
.venv/Scripts/python -m scripts.curated_pipeline review --provenance .vocabulary-pipeline/generator-ledger.json --run-dir .vocabulary-pipeline/review-pilot --max-calls 10 --max-output-tokens 4096 --attempts 2 --output .vocabulary-pipeline/review-pilot-summary.json
```

Calls and output tokens are explicit budget limits, not a dollar quote. Input includes
the full record and global lexical identities; account for input charges in your API
spending limit. A run's call reservations persist across restarts and cannot be increased
by reusing its directory with new options. No calls were authorized by the example alone.
Choose an adequate budget deliberately after inspecting pilot findings.

Each response is retained with its actual receipt time and provider message ID. The
service derives a stable review UUID from that ID. The model supplies linguistic
assessments, confidence, findings and an optional corrected record; it does not supply
fabricated invocation metadata. The adapter builds and validates the existing strict
ReviewResult schema. All nine aspects, confidence >=0.95, current checksums and all
existing policy checks still apply. Confidence remains a model estimate.

Correction suggestions preserve lexical identity, increment content_version by one,
and create an unapproved draft. A correction is now authored by the proposing reviewer;
the other model must independently review it. With no secondary model, suggestions
remain unresolved. Identity-changing suggestions require separate editorial resolution.
Every attempt and old finding remains in the run directory. The attempt limit includes
initial review and corrected drafts. Invalid responses consume their reserved calls;
uncertain or exhausted entries remain pending. No rows are silently discarded.

Restart with the identical review command and a NEW summary output filename. Completed
responses are revalidated without more paid calls. A transport failure or reservation
without a receipt stops the run to avoid repeating an invocation with an unknown outcome.
Investigate that reservation before choosing a new run directory and spending again.
A crashed process may leave `run.lock`: remove only that file after verifying the process
has stopped. Do not remove reservations to recover call budget. Malformed receipts fail
closed or remain invalid; standalone result files are never accepted as provider proof.

To import corrected content, supply the review directory consistently to plan and execute.
Its reviewed request contents overlay the immutable source in memory; source files stay
unchanged. Import happens before review submission. Intermediate approvals for old versions
are never submitted. Latest unresolved corrected drafts may be imported but stay unpublished.

```powershell
.venv/Scripts/python -m scripts.curated_pipeline plan --database-env VOCABULARY_DATABASE_URL --review-dir .vocabulary-pipeline/review-pilot --output .vocabulary-pipeline/corrected-import-plan.json
# After approval, execute with the same --review-dir and the NEW plan token.

.venv/Scripts/python -m scripts.curated_pipeline plan --database-env VOCABULARY_DATABASE_URL --operation submit --review-dir .vocabulary-pipeline/review-pilot --output .vocabulary-pipeline/submission-plan.json
# After explicit approval of submission-plan.json:
$pipelineConfirmation = (Get-Content .vocabulary-pipeline/submission-plan.json -Raw | ConvertFrom-Json).confirmation_token
.venv/Scripts/python -m scripts.curated_pipeline execute --database-env VOCABULARY_DATABASE_URL --operation submit --review-dir .vocabulary-pipeline/review-pilot --operator '<named submitting operator>' --confirm $pipelineConfirmation --output .vocabulary-pipeline/submission-result.json
```

Submission re-derives results from receipts, then uses `import_reviews`, preserving
append-only evidence, stale-checksum rejection, editorial holds and human approvals.
Replay uses the same provider-derived review IDs. Local files are not cryptographically
signed provider attestations; never present mocked transport fixtures as real review.
Unit tests explicitly label their providers synthetic and cannot be selected by CLI.

Publication remains an explicit backend setting. Only after eligible genuine review:

```powershell
$env:ALLOW_AI_APPROVED_VOCABULARY = 'true'
# Restart the intended backend with that setting; do not silently change production.
.venv/Scripts/python -m app
# In another shell with the same policy/configuration:
.venv/Scripts/python -m scripts.curated_pipeline report --database-env VOCABULARY_DATABASE_URL --output .vocabulary-pipeline/final-coverage.json
```

Verify `/api/v1/dictionary/search`, dictionary detail and authenticated personal save
using real authenticated sessions. Pending/rejected content must stay hidden; AI content
requires matching current-version evidence. The report's visibility count uses the
application's exact visibility predicate and its process setting; it does not prove the
running API was restarted with that setting. Existing API integration tests exercise
search/detail/save, holds, stale evidence and cross-user isolation using synthetic data.
No live development HTTP/session validation was performed during this phase.

Executed verification and final counts are recorded in the linked coverage report and
[implementation verification](phase4.0.2-verification.md). Development bulk import,
genuine semantic review, correction approval and publication remain unperformed.
