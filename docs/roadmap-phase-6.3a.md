# Phase 6.3A: lesson content and asset preparation

Implemented 1 November 2026. This phase prepares filesystem drafts only. No development
roadmap was imported, published or activated. No development schema, catalog, learner,
EXP or FSRS data was changed. Existing Phase 6.1/6.2 working-tree changes are preserved.

## Architecture and output

`app/schemas/roadmap_preparation.py` defines strict authoring sidecars;
`app/services/roadmap_preparation.py` compiles them into the **existing**
`RoadmapDefinition` schema version 1. There is no second lesson database, new migration,
activity kind, paid provider, download, or Android contract change.

Inputs are an ordered preparation plan, existing **converted CuratedRecord JSONL** files,
optional enrichment and local asset manifests. Use the converted catalog artifacts, not
the richer original authoring schema. Conflicting versions of an identity are errors;
select the intended source revision explicitly. Records are validated by the existing
curated contract, including Simplified-only characters, exact tone-marked/numbered
Pinyin agreement, syllable counts, meanings and lexical identity. UUIDs use the existing
curated import namespace. The compiler never regenerates or overwrites dictionary data.
Hanzi, Pinyin, Hán-Việt and meanings remain catalog fields, accessed through pinned
revision references. Quiz prompts/options are educational content derived from those
fields, not another dictionary table. Existing catalog examples retain their own catalog
review policy; the pipeline does not assume source examples have been human-reviewed.

Each NEW_WORD introduces one identity. Explicit groups have stable keys and section
metadata. Groups split at `review_interval` (default 3); every final short group also
gets a REVIEW. Reviews contain exactly the immediately preceding ordered identities and
revisions. Review quiz distractors come exclusively from that scope. There is no graded
FSRS invocation, memory update, EXP write, or learner API call in the compiler.

Node IDs derive from roadmap and vocabulary identity; activity IDs derive from node,
target and template. Review IDs include explicit group key and ordered stable scope.
Changing review scope creates a different stable review identity, requiring careful
operator review before a future release because first-completion rewards use that ID.
Reordering unchanged words preserves their stable IDs. Changing roadmap/content version
preserves node/activity identities, while existing publication code binds new immutable
lesson/node versions. Do not reuse a roadmap ID/code for a different course.

Generation writes:

| Artifact | Purpose |
| --- | --- |
| `roadmap.json` | Complete existing executable draft contract, private answer keys included |
| `lessons/<node UUID>.json` | Individual compatible node/lesson checkpoints |
| `manifest.json` | Compiler, plan and definition hashes; exact catalog checksums and asset sidecars |
| `assets.json` | Versioned asset registrations and full provenance/review metadata |
| `objects/sha256/*` | Verified original bytes using existing immutable CAS adapter |
| `asset-library/assets/*.json` | Assets-only files accepted by the existing content importer |
| `quality.json`, `quality.md` | Machine/human quality findings and publication prerequisites |
| `missing-assets.json` | Explicit inventory of absent optional enrichment |
| `publication-candidate.json` | Optional private DRAFT package, never a published bundle |

Keep the entire directory together. Definition, plan and catalog bindings are immutable
within an output directory; corrections need a new roadmap version and output directory.
Writes are atomic per artifact. An interrupted run resumes missing files, and byte-identical
files retain modification times. Generation compiles batches in memory, indexes catalog
records by identity, and skips unchanged writes; it does not claim zero recomputation.
Existing roadmap limits remain (10,000 nodes, 100 activities per lesson). Large review
intervals with many quiz templates can exceed activity limits and must be reduced.
The phase generates only three words, not thousands of unfinished lessons.

## Operator commands

From `backend/`, in PowerShell:

```powershell
$prepArgs = @(
  '--plan', 'content/roadmaps/preparation/hsk-0.plan.json',
  '--catalog', '../docs/datasets/original-zhvi/level-0-batch-001.converted.jsonl',
  '--output', 'content/roadmaps/preparation/hsk-0-v1'
)
.venv/Scripts/python -m scripts.roadmap --help
.venv/Scripts/python -m scripts.roadmap generate-drafts @prepArgs
.venv/Scripts/python -m scripts.roadmap check-content @prepArgs
.venv/Scripts/python -m scripts.roadmap missing-assets @prepArgs
.venv/Scripts/python -m scripts.roadmap preview-file @prepArgs
.venv/Scripts/python -m scripts.roadmap build-reviews @prepArgs
.venv/Scripts/python -m scripts.roadmap quality-report @prepArgs
.venv/Scripts/python -m scripts.roadmap prepare-bundle @prepArgs
```

`--catalog` accepts multiple explicitly selected files; `--asset-root` bounds local asset
paths (default current directory). `build-reviews` regenerates the complete definition
with exact review groups; it does not append duplicate reviews. `preview-file` removes
correct answer indices. Operator draft/package files retain keys and must never be
served through learner endpoints. Existing authenticated detail already removes keys.
Exit 0 means structural gates passed, **not educational approval or publication readiness**.
Exit 1 means reported quality/integrity errors; exit 2 means malformed input or I/O failure.
No command offers a blanket approval flag. Validation recompiles against inputs and checks
the complete manifest, per-lesson checkpoints, asset registrations and CAS bytes; stale or
tampered artifacts block candidate preparation. Reports refresh on validation.

The existing `validate FILE` checks the executable contract only. Use `check-content` for
the preparation gates. The existing `import`, `publish` and `activate` commands retain their
explicit write semantics and are **not part of this phase's execution**. A private candidate
has `publication_ready=false`; it is not accepted as a publication attestation.

After separate future write authorization, assets can use the existing assets-only
`scripts.import_content --assets-only --content-dir <output>/asset-library --storage-dir <output>/objects`
workflow. Preserve `assets.json` and `manifest.json` alongside that library: they contain
the source, attribution, license, origin and exact review evidence, while the older asset
import schema persists only its supported display metadata. The API's configured storage
must have those exact CAS objects before preview/publication; using an isolated preparation
directory as importer storage does not copy bytes into deployment storage automatically.
The generated `roadmap.json` then uses existing draft import/preview/publication contracts.
Review the source/candidate and database reconciliation **before authorizing any such writes**.
The additive `--assets-only` loader mode refuses vocabulary, templates and lesson files;
the default importer retains its original lesson requirement. No manual DB editing or new
registration service is needed.

## Reviewed enrichment

`enrichments` entries target exact `{vocabulary_id, content_version}` references. Components,
examples and notes are sidecar authoring inputs; only reviewed renderable projections enter
the existing lesson. Missing content stays explicitly UNAVAILABLE (components stay empty).

Every review is initially `UNREVIEWED`. An operator-supplied `REVIEWED` entry requires a
named reviewer, an evidence/ticket reference and `content_sha256`. The hash is
`roadmap_preparation.checksum(item.model_dump(mode='json', exclude={'review'}))` for assets,
components and examples. Notes use the enrichment payload excluding `review` and
`notes_review` (including its reference, examples and components). These are local operator
attestations, not authenticated third-party proof. The compiler never fills them in or
claims a person has reviewed generated content. Changes invalidate the exact review binding.

Component entries contain character position **and exact character**, component, spatial
position, SEMANTIC_RADICAL/PHONETIC/STRUCTURAL role, Vietnamese explanation and interpretation:

- HISTORICAL requires a source and content-bound review.
- MODERN_MNEMONIC is explicitly rendered as a modern memory aid without historical claims.
- ORIGIN_UNAVAILABLE explicitly states that historical origin is unverified/unavailable.

LEFT, RIGHT, TOP, BOTTOM, ENCLOSING, ENCLOSED, OVERLAPPING and WHOLE are supported positions.
Repeated/multiple characters use distinct character positions. Wrong characters, invalid
positions, duplicate/conflicting slots, missing explanations, stale review and historical
claims without sources are rejected. Multiple components per character are supported.
Neither spatial validity nor citation presence proves historical truth or that a component
contributes semantically. Reviewers must verify that explanation, role and cited source agree;
automatic checks cannot detect all contradictory natural-language explanations. The renderer
receives position/interpretation labels in the existing reviewed explanation field.

Examples contain Chinese, readable Pinyin, numbered Pinyin, Vietnamese translation, exact
target occurrence offset, difficulty, optional audio reference and review. The target must
occur at the supplied character offset; target numbered syllables must match its specific
catalog pronunciation. Sentence Pinyin forms/counts must agree and difficulty cannot exceed
the word's learning level. Grammar, translation, sense and real beginner suitability require
human review. Until reviewed, examples are omitted. Publication status is inherited from
the containing version (this phase remains DRAFT). Per-example audio is modeled but currently
rejected with a clear error because lesson v1 has no per-example audio player/binding.
Optional example audio must be omitted until that explicit extension is implemented.

## Audio and stroke preparation

Every local asset declares stable source UUID, positive version, exact vocabulary revision,
ordered Simplified text, file path, SHA-256, byte length, media type, source, attribution,
license, redistribution permission, origin and review. Audio additionally requires exact
numbered Pinyin; polyphonic readings are separate curated identities. Human recording and
TTS are distinct origins; TTS requires a provider. Review evidence must cover actual audible
pronunciation, tones, licensing and deployment rights/costs. No TTS provider is invoked.
No external dataset is downloaded, endorsed, licensed or redistributed by this change.

Versioned lesson asset UUIDs derive from source UUID, version **and byte checksum**. Stable
CAS keys retain exact original bytes; the existing adapter uses a `.json` key suffix even
for binary bytes, while media type controls playback. Paths cannot escape the supplied
asset root. Maximum size is Android's 16 MiB limit. Missing files, checksum/length mismatches,
wrong words/readings, unsupported formats and unconfirmed redistribution rights are errors.
Unreviewed content is omitted with a warning, never silently made available.

Audio import supports WAV and MP3, matching Android and the existing asset importer. WAV
validation checks full PCM frame length, channels and sample rate. MP3/image signatures
are structural screening, **not full decoder validation or proof of linguistic accuracy**;
review must include actual playback/rendering on supported Android versions.
The existing graph-scoped 16 MiB media cache and authenticated integrity-checked asset
endpoint are reused. There is no new persistent media cache or sync framework.

Stroke assets support reviewed PNG diagrams or GIF animations. One asset must depict the
**entire exact ordered word**, including repeated characters: v1 has one lesson-level asset,
not a per-character mapping. Never attach a single-character animation to a multi-character
word. The original sequence/order must be reviewed against a trustworthy cited source;
byte validation cannot establish correct calligraphy. A static diagram is not labeled an
animation, and no different character is substituted.

Structured centerline JSON is also accepted for **preparation only**: schema version 1,
ordered `characters`, each with exact `character` and ordered `strokes` arrays of original
normalized `[x,y]` points. Empty/out-of-range/nonfinite paths and wrong/reordered characters
are rejected. These are reviewed imported trajectories, never generated stroke sequences.
JSON receives `STRUCTURED_RENDERER_PENDING` and does not create an AVAILABLE stroke activity.
Phase 6.2 Android cannot animate it. A future explicit renderer/per-character contract can
consume it after Android compatibility and device tests; this phase preserves current UI.

## Quizzes and participation

CHARACTER, PINYIN, WORD_TO_MEANING and MEANING_TO_WORD templates compile to existing QUIZ
activities with server-owned EXACT_CHOICE answers. Deterministic choice ordering avoids
putting every answer at index zero. Distractors exclude identical written forms, identical
pronunciations, intersecting normalized Vietnamese meanings and duplicate labels. Prompts
include pronunciation/meaning context where useful. Too few conservative distractors omit
the template with a warning; they never expand a review into future vocabulary. Reviewers
must still inspect synonyms, near-synonyms and misleading choices. Matching needs a new
activity/submission/evaluator and Android renderer; it is not simulated through CHOICE.

HANDWRITING preserves original freehand, has snapping disabled and uses existing multi-character
UI. PRONUNCIATION is generated only when reviewed reference audio exists, with configurable
1–20 repetitions. Both use PARTICIPATION. Neither activity creates handwriting scores, tone
accuracy, phoneme grades or trusted assessment evidence. Future evaluations need explicit
versioned server evaluators and trusted receipts, not invented numeric fields in drafts.

## HSK 0 draft and readiness

`backend/content/roadmaps/preparation/hsk-0.plan.json` selects existing source revision 1:

| Word | Existing curated UUID |
| --- | --- |
| 我 (`wo3`) | `4ae81805-45f9-5d4f-a576-2a03b4ba27c9` |
| 你 (`ni3`) | `e611f2a1-17bb-5215-8862-7f69f32ca0fb` |
| 好 (`hao3`) | `48fd5063-1606-5d90-9943-74d05d8dfc48` |

`hsk-0-v1/roadmap.json` contains three NEW_WORD nodes and their REVIEW, 31 activities:
four introductions, three freehand activities and 24 quizzes. The draft has **0 ERROR,
2 WARNING, 15 OPTIONAL_MISSING**. Each word lacks newly supplied reviewed audio, stroke
asset, components, examples and notes. Those are honest preparation omissions, not claims
that the curated dictionary lacks examples. The complete inventory is `missing-assets.json`.

Publication remains blocked on individual educational review, reconciling current approved
database revisions against the filesystem bindings, any asset registration/storage verification,
and separate operator authorization. The report always says publication readiness is false;
this phase establishes draft readiness only. No real review approval has been manufactured.

## Verification and Phase 6.3B

Executed check results are recorded in [the runbook](runbooks/roadmap-phase-6.3a.md).
No dependency or schema change was required. Android wire/activity contracts are unchanged;
no new device-validation claim is made.

Recommended Phase 6.3B scope: have qualified reviewers review the three-word pedagogy,
examples and component explanations; obtain pronunciation and stroke assets with verified
redistribution rights; compare exact live catalog revisions through a read-only operator
preflight; review asset registration/storage plans; run the six activity types on a device.
Only after separate authorization should an operator import and publish/activate the first
small course. Treat per-character structured animation, per-example audio and matching as
explicit subsequent contract extensions. Keep graded handwriting/pronunciation evaluation
and FSRS scheduling changes outside content preparation.
