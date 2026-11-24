# Phase 6.1: executable lesson and vocabulary roadmap foundation

Local development migration 0015 is applied and preservation-verified following explicit
authorization; see the [deployment report](runbooks/roadmap-0015-deployment-20261101.md).
Content import/publication/activation remain pending authorization. Android is unchanged. Historical
CONTENT_PREVIEW bundles and preview runs retain their original semantics.

## Architecture and persistence

Existing `lessons`, `lesson_versions`, `lesson_templates`, template versions,
`assets`, content-addressed storage, catalog revisions, async sessions and authentication
are reused. `lesson_versions.engine_definition` distinguishes executable curated lessons
from legacy previews. No legacy lesson/vocabulary association is repurposed, and no
TEACHES provenance is inferred. The executable template identifies this contract;
its activities are held in the existing lesson version rather than forced into the
preview-only scene enum. A roadmap node is an ordering reference to that version,
not a second lesson definition table.

Additive revision `0015_roadmap_engine`, after `0014_fsrs_only`, adds nine tables:

| Table | Responsibility |
| --- | --- |
| roadmaps | Stable identity/code; nullable active published version pointer |
| roadmap_versions | Draft/release definition, title, immutable publication and bundle asset |
| roadmap_node_identities | Stable node/type and single curated identity for NEW_WORD |
| roadmap_nodes | Ordered membership in a roadmap version; exact lesson version |
| roadmap_vocabulary | Explicit scope with catalog-revision composite foreign key |
| roadmap_progress | Identity-scoped durable status and first completed node version |
| roadmap_runs | Owned execution against one immutable node version; separate replay runs |
| roadmap_activity_receipts | Append-only evidence, request identity, evaluator version and result |
| roadmap_exp_grants | Append-only first-completion grant, unique by user/stable node |

Published versions, node membership, scope, assets and referenced catalog revisions have
database immutability guards. Stable node identities cannot be repurposed. The existing
preview publication trigger retains its original branch; a separate explicit engine
branch accepts curated lessons. Publication prerequisites are also checked in the service.
No migration performs data conversion, learner updates, publication or automatic activation.
Append-only audit tables intentionally require a future reviewed account-retention procedure
before account deletion; cascading deletion must not silently erase these records.

## Authoring and one-word contract

`app/schemas/roadmap.py` contains strict Pydantic contracts; extra fields are rejected.
`NEW_WORD` has exactly one `{vocabulary_id, content_version}`. These references target
the curated catalog and its revision history. Simplified, Pinyin, Hán-Việt, Vietnamese
meanings and shared examples come from that revision, never a lesson-specific dictionary.
Learner detail returns an educational projection of those pinned revisions, excluding
reviewer data. Missing optional Hán-Việt is null, not an invented reading.

Each lesson has explicit activities and at least one required activity. Supported kinds:
INTRODUCTION, COMPONENTS, STROKE_ORDER, HANDWRITING, QUIZ and PRONUNCIATION. Activities
have stable UUIDs, required flags, prompts and bounded repetition counts. Quizzes have
server-only correct choices. Writing/speaking are participation contracts only.

Audio, examples, notes and stroke order use enrichment declarations with `required`
and AVAILABLE / UNAVAILABLE / UNREVIEWED states. AVAILABLE requires reviewed text or a
stable asset UUID; unavailable/unreviewed material cannot contain renderable content.
Required unavailable enrichment is invalid. Publication refuses any UNREVIEWED
enrichment and verifies referenced asset bytes, SHA-256, length and audio media type.
Unavailable optional media remains an explicit omission, not fabricated content.
Component and stroke-order activities require their supporting enrichment.

Components include character position (allowing repeated/multiple Hanzi), component,
SEMANTIC_RADICAL / PHONETIC / STRUCTURAL role and reviewable explanation. Several
components can occupy one character. Their explanations belong to the immutable lesson
version. Publication validates character positions; it never infers semantic meaning
from a visible component.

Freehand submissions store original normalized stroke point sequences without snapping.
Bounds limit points/strokes and require nonempty strokes plus participation duration;
there is no handwriting-quality grade or ML Kit confidence claim. Speaking records a
bounded repetition and participation duration, without storing private audio or claiming
that STT measures pronunciation quality. The evidence JSON and versioned evaluator field
allow future trusted evaluation receipts without changing progress/reward identity.

## Review groups and progression

Default `review_interval=3`; configurable per roadmap version from 1 to 100. Nodes have
contiguous zero-based positions, globally stable UUIDs, titles, section keys and optional
string visual metadata. Sections may represent future HSK levels; progression is linear
across sections for this phase. The final shorter group must also have a REVIEW node.
Earlier groups may deliberately be shorter; the interval is the maximum group size.

Review scope is stored explicitly, in order, with exact vocabulary revisions. It must
equal the immediately preceding NEW_WORD group. Missing scope, future vocabulary,
duplicate introductions, duplicate nodes, missing review gates and reordered positions
are rejected. A changed review scope uses a new roadmap/lesson version; first completion
and rewards remain attached to the stable node identity. Use a new node identity when
a new reward-bearing educational unit is intended.

Availability is calculated by the backend: the first unresolved node is available,
later nodes are locked, and completed/skipped nodes remain revisitable. NEW_WORD can
be skipped. REVIEW gates cannot be skipped unless `allow_review_skip` is explicitly
true in that publication. Stable statuses carry across versions; inserting new preceding
nodes does not erase completion or prevent revisiting resolved nodes.

| Current state | Action | Result |
| --- | --- | --- |
| NOT_STARTED | start | IN_PROGRESS |
| NOT_STARTED / IN_PROGRESS | deliberate skip | SKIPPED, zero EXP |
| SKIPPED | start/resume | IN_PROGRESS, existing receipts retained |
| IN_PROGRESS / SKIPPED | complete an owned run with all required evidence | COMPLETED |
| COMPLETED | start/replay/complete | Completion record preserved |
| COMPLETED | skip | Remains COMPLETED |

Returning to an unfinished skipped node makes it IN_PROGRESS again; it is once again
an unresolved gate until completed/skipped. Previously resolved later nodes remain
revisitable. No complete endpoint can create a run implicitly or accept `completed=true`.

First runs resume by `(user, node version)`; repeated start calls return the same run.
Replay requires a client UUID `request_id`, used as the run UUID. Retrying it resumes
that exact replay; another UUID creates another practice run. Replays must satisfy the
published requirements but award zero additional EXP and never replace first completion.
Old owned runs remain accessible after activation changes or depublication. New starts
must use the active version, preventing silent upgrades of unfinished lesson content.
Depublication withdraws discovery/new starts; it is not emergency revocation of old runs.

## Completion, EXP and FSRS

Each write locks the authenticated user row before reading/writing runs or progress,
serializing even absent progress rows. This follows the daily planner's lock order.
Completion checks every required activity and each distinct repetition against persisted
accepted receipts. Incorrect quiz responses do not satisfy requirements. Activity retries
use `(run_id, request_id)`; different evidence with the same key returns 409.

The completion transaction sets first completion/version, inserts the uniquely keyed
EXP grant and enqueues the curated word together. Defaults are NEW_WORD=10 and REVIEW=15;
the immutable version's configurable reward values are recorded in the grant. SKIP and
replay award zero. Retries report zero newly awarded EXP; the aggregate comes from the
audit ledger. Unique constraints provide duplicate protection in addition to locking.

`CuratedCatalog.enqueue_lesson_word` participates in the caller's transaction and uses
the existing catalog visibility policy/insert guard. A new save has mastery zero and
`learning_activated=false`; it enters existing pending intake. DailyReview reserves work
within its durable 1,200-second plan; existing approved review policies determine grading
eligibility. The roadmap never creates an FSRS attempt or memory card. Only the existing
two-stage graded engine activates/schedules memory. The current product already exposes
pending saves as due; this phase preserves that behavior and controls practice through
the planner rather than introducing a second intake policy.

Existing saves use ON CONFLICT DO NOTHING: identity, active/inactive choice, mastery,
memory, due dates, counters and schedules remain intact. A manually removed word is not
silently reactivated. Skip adds no save and changes no mastery. REVIEW completion and
replay never touch collection/FSRS state. Learned provenance is the independent durable
node completion; collection membership alone does not prove mastery.

## Authenticated API

All routes are under `/api/v1`, use existing Bearer sessions, derive ownership from the
session, and return private `Cache-Control: no-store` responses. OpenAPI documents typed
request/response schemas. No public HTTP content-writing endpoints were added.

| Method | Path | Behavior |
| --- | --- | --- |
| GET | /roadmaps?limit=20&offset=0 | Active roadmap summaries, bounded limit ≤100, next_offset |
| GET | /roadmaps/{id}/nodes?after=-1&limit=50&version_id=... | Position cursor, version-pinned compact statuses/availability, next_position |
| GET | /roadmap-nodes/{node_version_id} | Available node detail, exact lesson version, pinned vocabulary; quiz keys removed |
| POST | /roadmap-nodes/{node_version_id}/start | `{}` resumes first run; `{replay:true,request_id:UUID}` creates/resumes practice |
| POST | /roadmap-runs/{run_id}/activities | Evidence receipt and server acceptance |
| POST | /roadmap-runs/{run_id}/complete | Verify evidence, atomic completion, exp_awarded for this transaction |
| POST | /roadmap-nodes/{node_version_id}/skip | Deliberate idempotent skip, no completion evidence/reward |
| GET | /me/roadmap-progress | total_exp, completed_nodes, skipped_nodes |

NEW_WORD and REVIEW use the same start/activity/complete paths. A submission has UUID
request_id/activity_id, kind ACKNOWLEDGE / CHOICE / FREEHAND / SPEAKING, repetition (zero
based), optional choice index, original strokes and duration_ms. Send only the applicable
fields; every required repetition must have an accepted receipt. Start returns run identity,
completion timestamp and accepted activity identities; activity retry preserves evidence.

401 is missing/expired authentication; 404 hides unowned/missing runs and unpublished
content; 403 NODE_LOCKED blocks progression. 409 codes include IDEMPOTENCY_CONFLICT,
ACTIVITIES_INCOMPLETE, VERSION_UNAVAILABLE, REVIEW_GATE_REQUIRED and RUN_COMPLETED.
Malformed requests return the existing generic 422. Quizzes never return correct_option
or the publication bundle through learner routes; operator preview is intentionally private.

Node pages use indexed `(roadmap_version_id, position)` ordering and indexed
`(user_id, node_id)` lookups. Availability uses a set query; the page performs no per-node
vocabulary query. Only requested detail loads vocabulary revisions, in one batch. Roadmap
summaries defer the full release definition. Immutable publication bundles use the existing
content-addressed object cache/storage; private progress is never cached as shared content.

## Local workflow and sample

Run from `backend/` after an authorized schema deployment. These commands are provided
for operators; import/publish/activate have **not** been run against development.

```powershell
.venv/Scripts/python -m scripts.roadmap validate content/roadmaps/hsk-0.example.json
.venv/Scripts/python -m scripts.roadmap import content/roadmaps/hsk-0.example.json
.venv/Scripts/python -m scripts.roadmap preview <version-uuid-returned-by-import>
.venv/Scripts/python -m scripts.roadmap publish <version-uuid> --reviewed-by 'Operator identity and review ticket'
.venv/Scripts/python -m scripts.roadmap depublish <roadmap-uuid>
.venv/Scripts/python -m scripts.roadmap activate <roadmap-uuid> <previous-published-version-uuid>
```

The HSK 0 example contains 我/你/好 → REVIEW → 学/中/文 → REVIEW. Catalog UUIDs derive
from the existing curated lexical namespace; version 1 is an explicit sample assumption,
not a claim about installed catalog revisions. Preview checks exact current approved
references; operators must author a new corrected draft if their catalog differs.
The sample has introduction acknowledgements only, and explicitly unavailable optional
media. It demonstrates contracts, not a complete pedagogy, assessment or reviewed course.
Publication requires a real operator review attestation, never fabricated AI approval.
Existing configured development-only catalog review visibility remains honored.

The original preview publisher cannot publish executable lessons; use the dedicated
roadmap command, which still reuses the same lesson versions/assets/storage. Filesystem
objects may remain unreferenced after rolled-back transactions, as in the existing workflow.

## Validation, limitations and Phase 6.2

See [the operator deployment and verification report](runbooks/roadmap-phase-6.1.md) for
executed results, isolated databases and exact preflight/deployment commands.

No Android roadmap UI, handwriting-shape grading, audio recording/evaluation or AI grading
is implemented. Participation evidence is client-attested; only exact-choice quizzes are
objectively scored here. Product authors must choose required activities accordingly.
The server does not claim physical practice occurred based on submitted durations.
Availability is linear, not a branching curriculum; artwork metadata is deliberately small.
User-row serialization favors integrity; measure lock contention before large-scale rollout.
Future assessment/rate-limit/retention work is separate from this backend foundation.

Phase 6.2 should add framework-free roadmap DTO mapping/repository contracts, a lifecycle
StateFlow ViewModel, paged Compose nodes from server availability, explicit skip confirmation,
resume and replay UUID persistence, the six activity renderers and EXP summary. Preserve
identity-scoped state, cancellation, original ink, server quiz grading and the separate daily
FSRS planner. Start with read-only roadmap browsing plus one complete introduction/quiz
flow before adding speaking or handwriting feedback. Validate on an isolated emulator or
test device; backend tests do not establish Android device behavior.
