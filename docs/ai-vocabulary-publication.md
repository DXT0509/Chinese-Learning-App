# AI-assisted vocabulary publication (Phase 4.0.1)

The production policy below remains `zhvi-semantic-v1`, including its confidence
threshold. The separate [local Codex policy](runbooks/local-codex-vocabulary.md)
uses `LOCAL_CODEX_REVIEWED` with an explicit development opt-in and additive migration
0010. It does not alter AI_APPROVED or HUMAN_APPROVED evidence rules.

This guide supersedes Phase 4's human-only publication rule. Migration 0009 is additive:
no vocabulary, account, personal collection, mastery or schedule is reset. No development
database migration, import or semantic review was performed during implementation.
Batch 001's original JSONL, manifest and validation report remain historical artifacts.

Publication is HUMAN_APPROVED by default. Set ALLOW_AI_APPROVED_VOCABULARY=true explicitly
and restart the API to also publish AI_APPROVED records with matching audit evidence for
the current content version and checksum. Search, detail, save and saved-content activity
share this rule and require a usable Vietnamese meaning. The collection INSERT guard also
requires this policy via a transaction-local setting set by the save service. Turning the
flag off hides AI catalog entries without deleting collections or changing mastery.
NEEDS_REVIEW and REJECTED are excluded.

## Offline review contract

Machine-readable input/output schemas: [curated-review.schema.json](curated-review.schema.json).
Python contracts: backend/app/schemas/curated_review.py. Use one JSON object per JSONL line.
The adapter never calls Gemini or another provider, reads API keys or incurs AI charges.
An operator supplies real externally obtained review results. Protect CLI/DB maintenance
access: model provenance is an operator assertion, not cryptographically verified provider
identity. Never fill missing model/version information with guesses.

Input includes the complete normalized record, generator provider/model/version, content
SHA-256, local mechanical validation and batch lexical identities. Use --catalog-file with
a complete normalized catalog JSONL to include existing lexical identities for duplicate
assessment. PostgreSQL uniqueness and the importer independently reject exact duplicate
identities. Possible semantic duplicates are findings, never automatically merged.

Output requires schema_version=1; a unique review_id UUID; policy_version=zhvi-semantic-v1;
lexical_key; content_version; content_checksum; generator and reviewer objects containing
provider/model/version; UTC reviewed_at; decision (AI_APPROVED, NEEDS_REVIEW or REJECTED);
confidence 0..1; assessments; findings; and the unchanged automated_validation object.

Each of these nine aspects must appear exactly once with result and a substantive rationale:
simplified, mandarin_pinyin_neutral_tones, vietnamese_definitions, sino_vietnamese,
example_correctness, example_pinyin_alignment, learning_difficulty, duplicate_identity,
ambiguity. Results are pass/fail/uncertain/not_applicable; only optional Sino-Vietnamese
may be not_applicable. Findings have aspect, severity (blocking/warning), message and a
strict boolean resolved. Assess Mandarin citation and neutral tones, natural Vietnamese,
conventional optional Sino-Vietnamese, grammar, sentence/Pinyin alignment, beginner levels
0–5, lexical duplication and ambiguous pronunciations/senses. Do not infer HSK membership.

Approval requires confidence >=0.95, every required aspect passing, no unresolved blocking
finding, and a reviewer with a different model or provider from the generator. A different
version of the same model alone is insufficient. Missing examples block AI publication.
Mechanical schema/OpenCC/Pinyin validation does not establish linguistic correctness.
If independent review is unavailable, do not submit approval: leave the draft pending.
No actual independent semantic review was available or performed during implementation.

Invalid evidence aborts the whole transaction. Valid pending/rejected evidence is retained
with its status. A draft or current record on editorial hold cannot be promoted by AI:
resolve findings in a new strictly higher content_version, import it, export and review
again. Never edit published revisions or reuse old review evidence. AI import cannot
overwrite HUMAN_APPROVED. The existing explicit human approval command remains available.

## Audit and safety

curated_vocabulary_ai_reviews is a separate append-only audit table, not learner history.
It stores review UUID, catalog identity/version/checksum, full external result, original
review request, recomputed validation, effective decision, submitting operator, evidence
checksum and server receipt timestamp. Database triggers reject audit UPDATE/DELETE.
Existing revision snapshots are retained. Review submissions and catalog imports share a
transaction advisory lock; conflicts roll back the entire batch. Identical review ID replay
is a no-op, changed evidence under the same ID fails, and old replay cannot resurrect a
later rejected/pending entry. Stale content/version submissions fail.

The report counts current unique pronunciation identities, levels 0–5, pending, AI approved,
human approved, rejected, duplicate candidates from latest current-version findings, and
missing Vietnamese meanings/examples. Approved counts are independent of publication opt-in.
The target is 2,500; this change generates no additional vocabulary.

## Local commands

Run from backend in PowerShell. Select your intended database explicitly. These commands
are for the developer; the implementation never migrates the development DB.

```powershell
$env:DATABASE_URL = '<your intended postgresql+psycopg URL>'
.venv/Scripts/python -m alembic upgrade head
.venv/Scripts/python -m alembic check

# Import never grants approval.
.venv/Scripts/python -m scripts.curated_vocabulary validate --file '<batch.jsonl>'
.venv/Scripts/python -m scripts.curated_vocabulary import --file '<batch.jsonl>' --batch '<immutable-batch-id>'

# Supply ACTUAL generator metadata.
.venv/Scripts/python -m scripts.curated_review export --file '<batch.jsonl>' --output '<new-review-input.jsonl>' --generator-provider '<actual-provider>' --generator-model '<actual-model>' --generator-version '<actual-version>'
# Optional: append --catalog-file '<complete-normalized-catalog.jsonl>'.
.venv/Scripts/python -m scripts.curated_review schemas --output '<new-review-schemas.json>'

# Send input and output schema to your independent reviewer externally.
# Request all nine assessments and JSONL output, preserving checksum/validation metadata.
# Record model/version from the actual invocation. If unavailable, leave records pending.
.venv/Scripts/python -m scripts.curated_review submit --request '<review-input.jsonl>' --results '<actual-review-results.jsonl>' --operator '<submitting-operator>'
.venv/Scripts/python -m scripts.curated_review report

# Effective after API restart:
$env:ALLOW_AI_APPROVED_VOCABULARY = 'true'
.venv/Scripts/python -m app
```

For Batch 001, convert to NEW files first; do not run its generator to overwrite originals:

```powershell
.venv/Scripts/python -m scripts.curated_review convert-batch001 --file ../docs/datasets/original-zhvi/level-0-batch-001.jsonl --output '<new-batch001-import.jsonl>' --provenance '<new-batch001-provenance.json>'
.venv/Scripts/python -m scripts.curated_vocabulary validate --file '<new-batch001-import.jsonl>' --manifest '<new-batch001-import-manifest.json>'
.venv/Scripts/python -m scripts.curated_vocabulary import --file '<new-batch001-import.jsonl>' --batch original-zhvi-L0-B001-adapted-v1
```

The adapter retains source checksum, original records/keys/readings/issues in the provenance
sidecar. It selects Simplified forms, splits reading-specific identities, retains Vietnamese
senses and reading-specific examples, and canonicalizes only Pinyin spacing/case using the
existing renderer. It does not infer missing content or provenance. There are 51 identities
from 50 source entries (谁 has two readings), 46 unreviewed and five on hold. The alternate
谁 reading has no matching example and stays pending. Obtain actual generator model/version
provenance before exporting review input; the staging files do not establish it. Conversion
alone never makes any record publishable.

## Verification

Use distinct isolated databases. The migration rehearsal refuses nonempty databases and
retains fixtures. Never reset/drop existing data.

```powershell
$env:DATABASE_URL = '<isolated regression PostgreSQL URL>'
.venv/Scripts/python -m alembic upgrade head
.venv/Scripts/python -m alembic check
$env:TEST_DATABASE_URL = $env:DATABASE_URL
$env:AI_REVIEW_MIGRATION_TEST_DATABASE_URL = '<fresh EMPTY isolated migration PostgreSQL URL>'
.venv/Scripts/python -m pytest -q
.venv/Scripts/python -m ruff check app scripts tests
```

Executed during implementation: full backend regression run against an isolated temporary
PostgreSQL 18 instance: 188 passed, 6 skipped (optional legacy rehearsals without their
separate database URLs). After the final evidence-integrity and publication tests, all
13 focused review tests passed. The new 0008 -> 0009 nonempty migration rehearsal passed,
including existing saved vocabulary/mastery/schedule and catalog snapshot preservation;
alembic check reported no new upgrade operations. Ruff check passed for app/scripts/tests/
alembic; formatting checks passed for changed Python files. Existing Starlette/httpx
deprecation and SQLAlchemy reflection warnings were observed. No Android/device validation,
real independent semantic review, paid API call or development-database write was performed.
