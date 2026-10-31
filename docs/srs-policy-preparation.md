# Phase 4.1C: catalog grading-policy preparation

Prepared 2026-10-27 (Asia/Bangkok) against revision **0011**. Migration 0012 was
[applied on 2026-10-28](runbooks/srs-0012-deployment-20261028.md) after explicit
authorization. The exact 2,148-policy bundle was subsequently installed after
separate approval; see the [final deployment receipt](runbooks/srs-policy-deployment-20261028.md).
The [fresh 0012 pre-installation preview](srs-0012-policy-installation-preview-20261028.json)
confirmed the same coverage. The counts below describe the original preparation
snapshot. No vocabulary, collection, mastery, review history or
user rows were changed. The full detailed [preparation audit](srs-policy-coverage-audit.json) lists every
identity, content version, checksum, publication decision and exclusion reason.
The [approved bundle](datasets/srs-catalog-policies-v1.json) is now installed in local development.

## Coverage

| Measure | Records |
| --- | ---: |
| Total catalog | 2,810 |
| Currently published, eligible for policy consideration | 2,804 |
| Automatically gradable using explicitly cued recall | 2,145 |
| Prepared manually reviewed policies preserved verbatim | 3 |
| Installed policies in development | 0 (0012 table absent) |
| Published records needing grading review | 656 |
| Excluded by publication status | 6 |
| Final proposed coverage | **2,148 / 2,804 (76.60%)** |
| Missing POS | 0 |
| Missing or unsuitable Vietnamese question text | 2 |

The three manual policies are the existing Codex-reviewed examples, not independent
human certification. Publication uses the same `visible()` predicate as the
dictionary, including environment opt-ins and exact current review evidence. This
snapshot uses development's local-review opt-in. It does not authorize enabling
that publication mode in production. Every bundle policy is checked again against
the target environment at import time.

## Safe automatic question contract

A unique Vietnamese gloss is insufficient evidence for unrestricted translation.
The generator instead asks explicitly for the studied catalog word with its
existing Hán-Việt cue, character count and **all** Vietnamese meanings. Example:

> Viết từ đã học có âm Hán-Việt «nhất thiết» (2 chữ Hán). Nghĩa trong danh mục:
> tất cả; toàn bộ.

This identifies `一切|yi2 qie4`. The Hán-Việt cue is part of the question from the
start, not a requested assistance event. These policies assess cued recall; they
do not certify free Vietnamese-to-Chinese translation. Android must render the
entire prompt without removing the cue. This pedagogical constraint is necessary
for the reported automatic coverage.

Mandatory inputs are the catalog UUID, positive content version, exact checksum,
Hanzi-only Simplified form, matching lexical key, one numbered Pinyin syllable per
character, matching marked Pinyin, usable Vietnamese meanings, a usable Hán-Việt
cue with one alphabetic syllable per character, and one supported source POS.
The cue must be unique across **all** catalog records, including unpublished holds;
the Hanzi form must have only one pronunciation identity in that same catalog.
Unicode NFC, case and whitespace normalization apply to collision checks.

The approved catalog is the linguistic source. The pipeline does not independently
certify its translations or Hán-Việt annotations. Policy attribution explicitly
identifies deterministic preparation, rather than a fictitious human reviewer.
Operator review and authorization of this batch-generation rule and bundle are
required before installation.

All glosses of a qualifying pronunciation identity are retained together. Of the
automatic policies, 1,697 retain multiple glosses. No first-gloss selection,
gloss/POS delimiter alignment, new pronunciation, synonym, or grammatical
classification is inferred. Because the question asks for a specific cued lexical
identity, a different synonym with a different Hán-Việt cue is not an answer to
this question. Missing cues and unresolved collisions remain excluded.

POS must be a single supported source label; `measure word` maps to `classifier`
using the existing engine convention. Compound POS, idioms, phrases, quantifiers
and unknown labels require editorial decisions. The existing manual contract
still supports reviewed multi-select POS and explicit POS skips; automatic
preparation never invents those decisions. Multiple readings require separately
reviewed pronunciation-specific questions. Neither of the held `谁` identities is
made gradable. Legitimate alternate answers in existing manual policies remain
unchanged; no unsupported alternates are synthesized.

## Unresolved and excluded cases

Counts below overlap. The first count is across the complete catalog; the second
is among the 656 published unresolved records. Prepared manual policies can
resolve a reason (for example `他` shares a cue); such records are covered.

| Reason | All / published unresolved | Representative examples and action |
| --- | ---: | --- |
| Multiple/compound POS | 214 / 214 | `上|shang4`, `noun; verb`: author a sense-specific context and supported POS set |
| Unsupported POS | 241 / 239 | `一帆风顺`, `idiom`; `一点儿`, `quantifier`: require linguistic review; never map arbitrarily to adjective/classifier |
| Missing/unsuitable Hán-Việt cue | 209 / 202 | `一样`, `一起`: author a disambiguating manual context or review source annotations in a new content version |
| Shared Hán-Việt cue | 62 / 61 | `七` and `失`, both `thất`: automatic generation abstains even where meanings differ |
| Multiple pronunciation identities | 2 / 0 | `谁|shei2`, `谁|shui2`: both held, retain both identities and pronunciations for editorial review |
| Unsuitable Vietnamese prompt | 2 / 2 | `小姐` has a Chinese example inside a gloss; `明` has Chinese compounds inside a gloss: copying these would expose Chinese text in the question |
| Invalid lexical identity or prompt validation | 2 / 2 | The same `小姐` and `明` fail the existing policy prompt validator; this does not assert invalid lexical Pinyin |
| Missing POS | 0 / 0 | No current examples; synthetic missing-POS tests cover this exclusion |
| Publication excluded | 6 / n/a | `不客气`, `什么`, `厕所`, `没关系`, `谁|shei2`, `谁|shui2`: do not prepare or install policies |

Every unresolved/excluded record, its original meanings/POS/cue and every applicable
reason is in the JSON audit. Correct content through the existing versioned
authoring workflow; do not edit a published version to increase coverage.

## Pipeline and commands

From `backend/`, preview without writing files or database rows:

```powershell
.venv\Scripts\python -m scripts.prepare_review_policies --dry-run --preserve-file ..\docs\datasets\srs-review-policies-v1.json
```

Prepare new operator-selected output paths (existing files are refused):

```powershell
.venv\Scripts\python -m scripts.prepare_review_policies --dry-run --preserve-file ..\docs\datasets\srs-review-policies-v1.json --output .vocabulary-backups\catalog-policies-candidate.json --audit .vocabulary-backups\catalog-policy-audit-candidate.json
if ($LASTEXITCODE -ne 0) { throw 'Preparation failed' }
```

Preparation runs in a repeatable-read, read-only transaction and works at 0011 or
0012. Output order and JSON bytes are deterministic for the same source and
preservation input. The audit includes the bundle SHA-256. The prepared repository
bundle hash is `1eda6b46b0c568c9bfaa891f83cc05be14e21d77cffaa1df5c7d33e97fce77b2`.
`--preserve-file` is only needed for uninstalled manual policies; installed manual
policies are always loaded and preserved. Old-version installed policies are
reported separately, never carried into the new version automatically. Existing
generated policies are reassessed, not mistaken for manual reviews.

After separately authorized 0012 deployment, validate the exact approved bundle:

```powershell
.venv\Scripts\python -m scripts.review_policies --file ..\docs\datasets\srs-catalog-policies-v1.json
if ($LASTEXITCODE -ne 0) { throw 'Validation failed; do not install' }
```

Only after explicit operator authorization for bulk installation:

```powershell
.venv\Scripts\python -m scripts.review_policies --file ..\docs\datasets\srs-catalog-policies-v1.json --install
if ($LASTEXITCODE -ne 0) { throw 'Installation failed; inspect before restarting' }
```

The importer owns no transaction; the CLI wraps the complete batch in one
transaction. Installation briefly locks catalog/meaning/review-evidence tables
against changes and serializes policy importers. It checks publication, identity,
duplicates and the deterministic current-catalog result before inserting. A
matching reimport inserts zero rows. Existing manual policies win over automatic
candidates for the same exact identity. Other policy conflicts fail the batch;
there is no upsert that rewrites reviewed policy JSON. Held/stale/unknown entries
fail closed. No HTTP policy-write route exists.

At runtime, existing exact-version/checksum resolution still applies. Generated
policies additionally revalidate current catalog cue/readings and prompt/POS
support, with a per-transaction cache. Later catalog collisions can therefore
disable a previously generated target. Already initialized attempts retain the
engine's pinned, immutable target; new policy installation never upgrades them
silently. Ungradable targets remain unavailable for submissions and cannot produce
a learner failure or schedule penalty.

Follow the [0012 deployment runbook](runbooks/srs-0012-deployment.md) for backup,
preservation fingerprints, exact migration target and post-installation checks.
No additional schema revision is required for this preparation pipeline.

## Android readiness

The server's existing three-stage protocol can use these policies after authorized
migration and installation. Android still has no SRS review screens or protocol
implementation; this phase changes no Android files and claims no emulator/device
validation. Phase 4.2 must render the full Vietnamese prompt including its cue,
use `/review-targets` rather than dashboard due counts, handle unavailable records
without submitting failures, and implement server stages, first-answer feedback,
POS selection, idempotent submissions, resume/expiry and finalization as specified
in [the engine contract](srs-review-engine.md). No client-side correctness or
schedule computation is needed.

See [verification](srs-policy-verification.md) for executed checks and limitations.
