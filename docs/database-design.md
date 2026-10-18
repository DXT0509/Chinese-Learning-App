# Proposed database and learning architecture

Status: **target design; Slices 1 and 2 implemented separately**. Reviewed 2026-10-18. This proposal
supersedes the vocabulary-only ten-table proposal. It authorizes no implementation,
migration, database connection, or data change by itself. The authorized Slice 1 scope,
compatibility schema and deviations are specified in [content authoring](content-authoring.md).
That document overrides target table definitions for the current implementation. In particular,
POS/HSK/components/radicals and scene overrides are deferred, and legacy columns remain.

Slice 2 identity/run definitions override the future identity assumptions below: MVP
uses email/password, nullable Google subjects and five additive tables described in
[authentication](authentication.md) and [Slice 2 contracts](slice2-verification.md).
Google Sign-In is deferred until pre-release. Existing progress tables are unchanged;
preview bookmarks are not completion evidence. The remaining 45-table proposal is future work.

Read with [Learning Engine](learning-engine-design.md), [examples](lesson-examples.md),
[SRS](srs-design.md), [implementation slices](mvp-implementation-plan.md), and
[complete relationship diagrams](database-erd.md).

## 1. Evidence, scope, and decisions

Inspected `backend/app/models/learning.py`, model registration, database metadata,
`backend/alembic/env.py`, and the full sole revision `0001_initial` (including downgrade).
The nine declared tables are users, characters, vocabulary, vocabulary_characters,
lessons, lesson_vocabulary, user_lesson_progress, user_vocabulary, and srs_states.
Models and migration agree on their structural definitions. UUID generation is Python
behavior; User.updated_at has an ORM onupdate, not a database update trigger.
Also read architecture, development, authentication, offline-sync, API conventions,
README, and PostgreSQL constraint tests. The tests permit a NULL Google subject and
use `unimplemented-v0`; they do not establish implemented authentication or scheduling.
Only infrastructure and health connectivity work today. No live database was inspected;
neither data emptiness nor applied migration state is assumed. This checkout has no
usable Git repository metadata, so source comparison uses inspected files, not Git history.

Proposed decisions:

- One curriculum, Vietnamese teaching text, simplified Chinese initially. No course
  hierarchy, generic content supertable, separate engine per lesson type, or generic repository.
- Each VOCABULARY lesson teaches exactly one stable vocabulary entry. Other lesson types
  can reference many entries, without implying they have all been learned.
- Stable lesson identity, immutable published lesson/template versions, separately
  published roadmap ordering, and a pinned execution run preserve accomplishments.
- A catalog lexical entry represents spelling, citation reading, and a Vietnamese sense.
  Whole phrases such as 你好 are allowed; knowing the phrase does not grant its substrings.
- Completion, library membership, app-learned provenance, EXP, and mastery are distinct.
- One SRS state per personal entry initially. Separate handwriting/listening cards are
  deferred; do not present this aggregate mastery as a measurement of every skill.
- Protected operations require real email/password authentication and revocable application sessions
  as described in authentication.md. This design does not implement session storage.

The target schema has **45 tables** listed below. This is the complete requested product
design, not a recommendation to create all tables in the next migration. A labels the
vocabulary/engine foundation and speech evaluation group, B mixed content, and C SRS.
These are schema groups, not migration batches; the eight slices in the implementation
plan define the minimum tables/columns needed at each step. The three new target tables
are evaluation_policies, assessment_attempts and review_tasks. Full sync receipts/tombstones,
session/token storage and private durable media remain separately scoped extensions.
Authentication/session design is a launch prerequisite for any personal API.

Finalized MVP decisions supersede the previous proposal: required speaking uses
STT_CONTENT_MATCH (content PASS/FAIL only); PRONUNCIATION_ASSESSMENT is a future mode
with an initial configurable threshold of 70/100. A due SRS attempt pins all required
tasks, passes only if all pass, and changes mastery by exactly +1/-1 with 0..5 bounds.
Technical blockers never count as task FAIL or a mastery decrement. The default minimum
eligible sentence count is 1, configurable per lesson; completed in-app TEACHES provenance
remains mandatory. These are requirements, not unresolved product choices.

## 2. Schema notation and enforcement

Every column is specified below. `?` means nullable; all others are NOT NULL. `id` is
an application-generated UUID PK unless another PK is stated. `FK x` means REFERENCES
`x.id` unless explicit composite columns follow. `UQ` means UNIQUE. `I` means additional
B-tree index. `created_at` and `updated_at` are timestamptz with initial default now();
services must explicitly maintain updated_at. No implicit timestamp, status, or JSON
columns exist beyond those listed. Types `text`, `int`, `smallint`, `boolean`, `uuid`,
`timestamptz`, `jsonb`, `numeric` are PostgreSQL types; bounded codes may use text plus CHECK.

Common rules apply to every table:

- Required text is trimmed nonblank; optional text is NULL or nonblank. NFC normalization
  happens before storage; never automatically merge Hanzi using compatibility normalization.
- All timestamp values are aware UTC instants. updated_at >= created_at wherever both exist.
- All `position` values are int >= 0; all `version`, `contract_version`, `schema_version`
  and `revision` values are int >= 1. Counts are int >= 0. Hashes are 64 lowercase hex
  SHA-256 characters. JSONB configuration/state/condition objects have SQL object-type
  checks and strict versioned Pydantic validation, size/depth bounds, and unknown-field rejection.
- IDs are immutable; FK ON UPDATE NO ACTION. FK deletion is RESTRICT except the explicit
  owned-child cascades in section 6. No cascade deletes a shared learning target.
- PK/UQ indexes are not duplicated. For **each FK**, add an index on its referencing
  columns unless a listed PK/UQ/index has those columns as its leading prefix. This
  is an explicit part of every table's index specification; reverse association lookups
  therefore remain indexed even where only PK/UQ is shown below. No JSONB GIN index by default.
- Row CHECKs enforce local bounds/discriminators; FK/UQ enforce identities. Publication
  cardinality, graph acyclicity, text alignment, and JSON reference validation are named
  service invariants, not imaginary cross-table CHECKs. PostgreSQL documents this limit
  in [constraints](https://www.postgresql.org/docs/17/ddl-constraints.html). The repository
  currently pins PostgreSQL 17.9; NULLS NOT DISTINCT below is supported by that target.
- Use existing pk_/fk_/uq_/ck_/ix_ naming conventions with unambiguous column suffixes.

### Shared catalog publication rule

Catalog rows have `revision` for cache/change detection. They are not a full temporal
database. At lesson publication, compile a content-addressed immutable **lesson bundle**
asset containing the resolved scenes and referenced catalog projections. This is a
delivery artifact outside PostgreSQL, not duplicate vocabulary JSONB in lesson rows.
The lesson version's bundle FK/hash is the authoritative historical rendering contract.
Assets remain available for supported pinned runs. Correcting catalog prose increments
its revision and affects only newly compiled versions; old bundles do not re-fetch mutable
display facts. Structural facts used for eligibility (lesson associations, sentence token
coverage/grammar, prerequisite edges) are immutable once used by a publication. Correct
them through a new sentence/lesson version, preserving old rows; no relabeling a lexical
identity to a different word/sense. This avoids a revision table for every dictionary entity.
An editorial write service and restricted DB writer role enforce these write boundaries;
SQL FKs alone do not enforce publication immutability. Mutable current catalogs and
immutable bundles must never be silently mixed in one run.

## 3. Public learning content (stages A/B)

Each row below is a complete table definition; semicolons separate columns.

| Table / stage | Columns | Keys, checks, additional indexes |
| --- | --- | --- |
| `assets` A | id uuid; storage_key text; media_type text; sha256 text; byte_length bigint; metadata jsonb; created_at timestamptz | UQ(storage_key); byte_length > 0; metadata object. Immutable object key, media type and hash; metadata only dimensions/duration/format. No binary or signed URLs. |
| `components` A | id uuid; glyph text; character_id uuid? FK characters; vietnamese_meaning text?; explanation text?; visual_asset_id uuid? FK assets; revision int | UQ(glyph). May refer to an independent character; non-character forms remain standalone glyph records. Avoid copying that character's dictionary facts. |
| `radicals` A | id uuid; component_id uuid FK components; dictionary_system text; radical_number int?; teaching_name text?; notes text?; revision int | UQ(dictionary_system,component_id); UQ(dictionary_system,radical_number), ordinary NULL-distinct; radical_number > 0 when present. Number is system-specific, not globally fixed. |
| `characters` A | id uuid; hanzi varchar(8); radical_id uuid? FK radicals; stroke_count int?; stroke_order_asset_id uuid? FK assets; classification text?; classification_explanation text?; classification_source text?; structure_explanation text?; revision int; created_at timestamptz | UQ(hanzi); stroke_count > 0 when known; classification in PICTOGRAPHIC, IDEOGRAPHIC, COMPOUND_IDEOGRAPHIC, PHONO_SEMANTIC, OTHER when present. Classification requires explanation/source; NULL means not reviewed, not an invented origin. |
| `character_components` A | character_id uuid FK characters; position int; component_id uuid FK components; location text; role text; explanation text? | PK(character_id,position); location in LEFT, RIGHT, TOP, BOTTOM, ENCLOSING, ENCLOSED, OVERLAY, OTHER; role in SEMANTIC, PHONETIC, BOTH, STRUCTURAL, UNKNOWN. A repeated component at distinct positions is valid. |
| `vocabulary` A | id uuid; simplified varchar(255); pinyin varchar(500); sino_vietnamese varchar(500)?; vietnamese_meaning varchar(1000); notes text?; audio_asset_id uuid? FK assets; revision int; created_at timestamptz | UQ(simplified,pinyin,vietnamese_meaning); pinyin is citation pronunciation, never overwritten by sandhi examples. |
| `vocabulary_characters` A | vocabulary_id uuid FK vocabulary; position int; character_id uuid FK characters | PK(vocabulary_id,position). Repeated characters allowed. Position is source NFC Unicode-scalar offset; a variation selector stays with its preceding base. Validate exact spelling alignment and complete supported Hanzi coverage. |
| `parts_of_speech` A | id uuid; code text; vietnamese_label text | UQ(code); reviewed tags, not a permanent DB enum of all possible grammatical categories. |
| `vocabulary_parts_of_speech` A | vocabulary_id uuid FK vocabulary; part_of_speech_id uuid FK parts_of_speech | PK(vocabulary_id,part_of_speech_id). Multiple tags allowed when appropriate to this lexical entry. |
| `hsk_standards` A | id uuid; code text; title text; source_reference text | UQ(code); code identifies a specific edition/version, not just HSK. |
| `hsk_levels` A | id uuid; standard_id uuid FK hsk_standards; code text; rank int; label text | UQ(standard_id,code); UQ(standard_id,rank); rank > 0. No universal maximum or official HSK0 assumption. |
| `vocabulary_hsk` A | vocabulary_id uuid FK vocabulary; level_id uuid FK hsk_levels | PK(vocabulary_id,level_id). Publication validation allows at most one assigned level per standard for an entry. Absence means unclassified; can be assigned under different standards. |
| `pronunciation_rules` B | id uuid; code text; title text; explanation text; revision int | UQ(code); Vietnamese teaching explanation. One rule reused by many lessons/examples. |
| `pronunciation_examples` B | id uuid; rule_id uuid FK pronunciation_rules; vocabulary_id uuid? FK vocabulary; chinese_text text; citation_pinyin text; spoken_pinyin text; explanation text; audio_asset_id uuid? FK assets; revision int | Optional lexical link because contextual examples can be phrases not catalog entries. Publish practice only with audio. Citation and spoken fields are independent. |
| `grammar_rules` B | id uuid; code text; title text; structure text; explanation text; revision int | UQ(code); structure is display notation, not executable parser code. |
| `sentences` B | id uuid; vietnamese_prompt text; chinese_text text; audio_asset_id uuid? FK assets; accepted_variants jsonb; validation_version text; status text; revision int | status DRAFT, PUBLISHED, ARCHIVED; variants is a bounded JSON array of exact texts, not full lexical records. I(status,id). Every published variant has full token/grammar annotations before use. |
| `sentence_tokens` B | sentence_id uuid FK sentences; variant_index int; position int; surface text; vocabulary_id uuid? FK vocabulary; nonlexical_kind text? | PK(sentence_id,variant_index,position); variant_index >= 0 (0 canonical, 1..N variants); position is scalar offset. Exactly one of vocabulary_id or nonlexical_kind present; nonlexical_kind is PUNCTUATION or WHITESPACE. No catch-all unknown token category. Validate contiguous surface coverage including particles, numerals, names and classifiers. |
| `sentence_grammar` B | sentence_id uuid FK sentences; grammar_rule_id uuid FK grammar_rules | PK(sentence_id,grammar_rule_id). Conservative union of required grammar across accepted variants. |
| `grammar_examples` B | grammar_rule_id uuid FK grammar_rules; sentence_id uuid FK sentences; position int; explanation text? | PK(grammar_rule_id,sentence_id); UQ(grammar_rule_id,position). An example sentence may illustrate several rules. |
| `learning_topics` B | id uuid; code text; title text; explanation text?; revision int | UQ(code). Weekdays/dates/family are rows, never dedicated tables. |

Characters, radicals and components are distinct roles. `radicals.component_id` reuses
a glyph record; `characters.radical_id` selects a dictionary classification. A component
can be a variant glyph such as 亻 with no standalone character FK, while its semantic
explanation can reference 人 in reviewed prose. A character's structural decomposition
does not automatically supply its dictionary radical. The characters/components FK cycle
is optional and insertable in phases; it is not a recursive decomposition engine. Do not
infer etymology from visual similarity or assign one classification to an entire word.

Unknown stroke counts are NULL rather than zero; required animations/counts are checked
when a scene is published. A character glyph validator checks a supported Hanzi grapheme
sequence rather than assuming varchar(8) enforces one character. POS/HSK join tables add
small catalog maintenance costs but avoid hardcoded level limits and comma-separated tags.
The HSK per-standard rule is a controlled-write service invariant in this compact design;
a later constraint trigger is appropriate if multiple independent import writers are allowed.

## 4. Lessons, templates, and roadmap (A unless B indicated)

| Table / stage | Columns | Keys, checks, additional indexes |
| --- | --- | --- |
| `lessons` A | id uuid; code text; lesson_type text; status text; created_at timestamptz | UQ(code); type VOCABULARY, PRONUNCIATION, GRAMMAR, TOPIC, REVIEW; status DRAFT, PUBLISHED, ARCHIVED. Type/identity fixed after publication. No global is_finished or roadmap position. |
| `lesson_versions` A | id uuid; lesson_id uuid FK lessons; version int; title text; template_version_id uuid FK lesson_template_versions; status text; exp_reward int; bundle_asset_id uuid? FK assets; published_at timestamptz?; created_at timestamptz | UQ(lesson_id,version); UQ(id,lesson_id) for composite FK; exp_reward >= 0; status DRAFT, PUBLISHED, ARCHIVED; published_at/bundle required for PUBLISHED and ARCHIVED. I(lesson_id,status,version). Published content frozen, archival only changes availability. |
| `lesson_vocabulary` A | lesson_version_id uuid FK lesson_versions; vocabulary_id uuid FK vocabulary; position int; role text | PK(lesson_version_id,vocabulary_id); UQ(lesson_version_id,position); role TEACHES, CONTEXT, REVIEWS. Publication: VOCABULARY exactly one row, TEACHES; other types may reference many. Only TEACHES creates vocabulary learning evidence on completion. |
| `lesson_grammar_rules` B | lesson_version_id uuid FK lesson_versions; grammar_rule_id uuid FK grammar_rules; role text | PK(lesson_version_id,grammar_rule_id); role TEACHES, CONTEXT, REVIEWS. Only TEACHES grants grammar knowledge on completion. |
| `lesson_pronunciation_rules` B | lesson_version_id uuid FK lesson_versions; pronunciation_rule_id uuid FK pronunciation_rules | PK(lesson_version_id,pronunciation_rule_id). |
| `lesson_topics` B | lesson_version_id uuid FK lesson_versions; topic_id uuid FK learning_topics | PK(lesson_version_id,topic_id). |
| `lesson_templates` A | id uuid; code text; description text | UQ(code); stable reusable authoring identity. |
| `lesson_template_versions` A | id uuid; template_id uuid FK lesson_templates; version int; status text; published_at timestamptz? | UQ(template_id,version); status DRAFT, PUBLISHED, ARCHIVED; timestamp required after publication. Immutable published definition. |
| `lesson_template_scenes` A | template_version_id uuid FK lesson_template_versions; scene_key uuid; position int; scene_type text; contract_version int; required boolean; config jsonb; condition jsonb? | PK(template_version_id,scene_key); UQ(template_version_id,position). Stable scene_key retained across template versions for the same conceptual scene. scene_type CHECK whitelist in Engine registry. |
| `lesson_scenes` A | lesson_version_id uuid FK lesson_versions; scene_key uuid; operation text; position int?; scene_type text?; contract_version int?; required boolean?; config jsonb?; condition jsonb? | PK(lesson_version_id,scene_key). operation ADD, REPLACE, REMOVE. ADD/REPLACE require all definition fields except nullable condition; REMOVE has only identity/operation and all other fields NULL. Position collisions checked on resolved sequence. ADD key must not exist; REPLACE/REMOVE must address inherited key. |
| `lesson_prerequisites` B | id uuid; lesson_version_id uuid FK lesson_versions; scope text; scene_key uuid?; required_lesson_id uuid? FK lessons; required_vocabulary_id uuid? FK vocabulary; required_grammar_rule_id uuid? FK grammar_rules | scope UNLOCK, RECOMMENDED, SCENE; exactly one required_* FK present. scene_key present iff SCENE. UQ NULLS NOT DISTINCT across (lesson_version_id,scope,scene_key,required_lesson_id,required_vocabulary_id,required_grammar_rule_id). Validate resolved scene existence. |
| `roadmap_releases` A | id uuid; version int; status text; review_every_n_vocabulary int; published_at timestamptz?; created_at timestamptz | UQ(version); status DRAFT, PUBLISHED, ARCHIVED; review_every_n_vocabulary > 0; timestamp required after publication. Partial UQ(status) WHERE status='PUBLISHED' gives one current release. |
| `roadmap_entries` A | release_id uuid FK roadmap_releases; lesson_id uuid FK lessons; lesson_version_id uuid; position int | PK(release_id,lesson_id); UQ(release_id,position); composite FK(lesson_version_id,lesson_id) to lesson_versions(id,lesson_id). Pin exact published versions, not a mutable latest pointer. |

These five template/scene tables all have different responsibilities. Template scenes
are defaults; lesson_scenes contains only complete replacement/addition definitions or
removals. It is never a second copy of every inherited scene. Full replacement rather
than JSON merge makes null/removal behavior predictable. Reordering inherited scenes
uses an explicit REPLACE; the small local duplication is intentional, reviewed and bounded.
Bindings to the single TEACHES vocabulary resolve references, not copies of its fields.
See Engine for stable scene instances when one definition expands by character/component.

Prerequisite rows are a conjunction per scope; alternatives are a future product need,
not executable expressions. UNLOCK and RECOMMENDED edges reference stable completed
lesson identities; vocabulary/grammar requirements derive from accepted completions.
Only SCENE edges affect scene inclusion. Proposed publication transaction locks a single
curriculum advisory key, validates the effective required dependency graph, and rejects
self-edges, cycles, dangling scene keys, and required knowledge with no viable producer.
Run cycle detection on required lesson edges; additionally compute reachability to a fixed
point from unlockable introductory lessons using their TEACHES outputs. Reject a required
knowledge loop with no reachable producer. Several producers are alternatives, so do not
mistakenly add every producer as a mandatory dependency. RECOMMENDED edges may cross the
roadmap but editors are warned about cycles. Revalidate all active published dependencies
when a release changes; do not assume roadmap order proves acyclicity. Legacy archived
versions remain valid for existing runs. Concurrent publication must use the same lock.

The review frequency is an authoring recommendation stored on a release: default proposal
5, configurable to 4 or another positive value. Editors insert stable REVIEW lessons;
the publisher counts only new TEACHES vocabulary nodes since the last review and warns
about spacing. It does not generate user progress or dynamically change node IDs. Non-vocabulary
lessons can occur between them. Atomic release activation archives the old active release
and publishes the new one. Reordering changes no lesson IDs or completion records.

## 5. Personal learning and review state

| Table / stage | Columns | Keys, checks, additional indexes |
| --- | --- | --- |
| `users` A | id uuid; google_sub varchar(255); display_name varchar(200); email varchar(320)?; created_at timestamptz; updated_at timestamptz | UQ(google_sub), verified nonblank stable Google subject. Email is nonunique profile data, never identity. No tokens/passwords. |
| `lesson_runs` A | id uuid; user_id uuid FK users; lesson_version_id uuid FK lesson_versions; operation_id uuid; request_hash text; status text; resolution jsonb; resolution_hash text; started_at timestamptz; completed_at timestamptz?; revision int | UQ(user_id,operation_id); UQ(id,user_id); status IN_PROGRESS, COMPLETED, ABANDONED; completed_at present iff COMPLETED; completed_at >= started_at. Partial UQ(user_id,lesson_version_id) WHERE status='IN_PROGRESS'. I(user_id,started_at,id). resolution is bounded execution decisions/instance IDs/evidence, not copied vocabulary. |
| `lesson_scene_progress` A | run_id uuid FK lesson_runs; scene_key uuid; instance_key text; status text; checkpoint jsonb; updated_at timestamptz | PK(run_id,scene_key,instance_key); status PENDING, BLOCKED, COMPLETED, SKIPPED; checkpoint object. BLOCKED retains permission/input/service recovery reason and prior work; never implies FAIL. Contains selected text/attempt summaries and optional private asset IDs, not raw large media. Validate every instance against run manifest. |
| `user_lesson_progress` A | user_id uuid FK users; lesson_id uuid FK lessons; status text; completed_at timestamptz?; completion_run_id uuid?; exp_awarded int; updated_at timestamptz | PK(user_id,lesson_id); composite FK(completion_run_id,user_id) to lesson_runs(id,user_id); UQ(completion_run_id); status not_started, in_progress, completed. completed iff completed_at and completion_run_id both present; exp_awarded >= 0 and =0 before completion. First completion fields immutable. |
| `user_vocabulary` A | id uuid; user_id uuid FK users; vocabulary_id uuid? FK vocabulary; source text; custom_simplified varchar(255)?; custom_pinyin varchar(500)?; custom_meaning text?; learned_at timestamptz?; created_at timestamptz; updated_at timestamptz | UQ(user_id,vocabulary_id) with ordinary NULL-distinct semantics; UQ(id,user_id) for review ownership. source catalog/custom with exhaustive checked union below. learned_at is first accepted study, not eligibility proof. |
| `srs_policies` C | id uuid; algorithm_version text; parameters jsonb; created_at timestamptz | UQ(algorithm_version); immutable validated full algorithm+parameter identity. Changing any grading/interval factor creates new version. No mutable global constants. |
| `srs_states` C | id uuid; user_vocabulary_id uuid FK user_vocabulary; mastery_level smallint; next_review_at timestamptz; last_reviewed_at timestamptz?; review_count int; consecutive_successes int; policy_id uuid FK srs_policies; algorithm_state jsonb; revision int; updated_at timestamptz | UQ(user_vocabulary_id); mastery_level BETWEEN 0 AND 5; 0 <= consecutive_successes <= review_count; review_count=0 iff last_reviewed_at IS NULL; next_review_at >= last_reviewed_at when present. I(next_review_at,id). |
| `review_attempts` C | id uuid; user_id uuid FK users; user_vocabulary_id uuid; run_id uuid?; scene_key uuid?; instance_key text?; operation_id uuid; request_hash text; expected_srs_revision int; policy_id uuid FK srs_policies; status text; aggregate_result text?; started_at timestamptz; submitted_at timestamptz?; evidence jsonb | UQ(user_id,operation_id); UQ(id,user_id,user_vocabulary_id); UQ(id,user_id) for task ownership; composite FK(user_vocabulary_id,user_id) to user_vocabulary(id,user_id); composite FK(run_id,user_id) to lesson_runs(id,user_id); composite FK(run_id,scene_key,instance_key) to lesson_scene_progress(run_id,scene_key,instance_key). status OPEN, BLOCKED, SUBMITTED, PRACTICE, STALE, ABANDONED; aggregate_result NULL, PASS or FAIL, required iff SUBMITTED; run/scene/instance all NULL or all present. Policy and required task set pinned at creation; retries share this identity. |
| `review_history` C | id uuid; user_id uuid FK users; user_vocabulary_id uuid; attempt_id uuid; operation_id uuid; request_hash text; outcome text; mastery_before smallint; mastery_after smallint; reviewed_at timestamptz; previous_due_at timestamptz; next_due_at timestamptz; policy_id uuid FK srs_policies; difficulty_factor numeric; revision_before int; revision_after int | UQ(user_id,operation_id); UQ(attempt_id); UQ(user_vocabulary_id,revision_after); composite FK(attempt_id,user_id,user_vocabulary_id) to review_attempts(id,user_id,user_vocabulary_id); composite FK(user_vocabulary_id,user_id) to user_vocabulary(id,user_id). outcome PASS or FAIL; mastery fields 0..5; PASS implies after=least(5,before+1), FAIL implies after=greatest(0,before-1); factor >0; next_due_at > reviewed_at; revision_after=revision_before+1. I(user_vocabulary_id,reviewed_at,id). |


| `evaluation_policies` A | id uuid; code text; version int; evaluation_mode text; locale text; evaluator_version text; parameters jsonb; created_at timestamptz | UQ(code,version); UQ(id,evaluation_mode); mode STT_CONTENT_MATCH, PRONUNCIATION_ASSESSMENT, TEXT_CONTENT_MATCH, HANDWRITING_ASSESSMENT; last mode reserved until a valid evaluator exists. Immutable policy binds comparison/threshold, adapter contract and provider capability requirements. Speech locale initially zh-CN. |
| `review_tasks` C | review_attempt_id uuid; task_key text; user_id uuid FK users; task_type text; evaluation_policy_id uuid FK evaluation_policies; required boolean; result text; finalized_at timestamptz?; evidence jsonb | PK(review_attempt_id,task_key); UQ(review_attempt_id,task_key,user_id); composite FK(review_attempt_id,user_id) to review_attempts(id,user_id). task_type MEANING_RECALL, PINYIN_RECALL, HANDWRITING_RECALL, SPEAKING, LISTENING_RECALL; result PENDING, BLOCKED, PASS, FAIL; finalized_at present iff PASS/FAIL. Nonempty pinned required set; no silent removal when blocked. Evidence records finalization rules and bounded retry/hint counts. |
| `assessment_attempts` A | id uuid; user_id uuid FK users; run_id uuid?; scene_key uuid?; instance_key text?; review_attempt_id uuid?; task_key text?; operation_id uuid; request_hash text; input_revision int; evaluation_policy_id uuid; evaluation_mode text; provider text?; provider_version text?; status text; recognized_text text?; score numeric?; metrics jsonb; error_code text?; started_at timestamptz; finished_at timestamptz? | UQ(user_id,operation_id); composite FK(run_id,user_id) to lesson_runs(id,user_id); composite FK(run_id,scene_key,instance_key) to lesson_scene_progress(run_id,scene_key,instance_key); composite FK(review_attempt_id,task_key,user_id) to review_tasks(review_attempt_id,task_key,user_id); composite FK(evaluation_policy_id,evaluation_mode) to evaluation_policies(id,evaluation_mode). At least one run or review-task context; each context tuple all NULL or all present. status PENDING, PASS, FAIL, ERROR, CANCELLED; terminal status iff finished_at present, finished_at >= started_at. ERROR requires error_code; PASS/FAIL require no error_code. STT_CONTENT_MATCH always score NULL and metrics empty; scores only for supported assessment metrics, 0..100 when present. I(user_id,started_at,id). No audio bytes or durable recording key stored; request_hash is idempotency metadata under the derived-data retention policy. |

Evaluation mode is repeated on assessment_attempts only as a constrained discriminator:
the composite FK makes it agree with its immutable policy. Policy FK plus provider/version
captures evaluation provenance; STT confidence is never stored/displayed as pronunciation
accuracy. Every valid per-input evaluation retry gets a new assessment_attempt ID and
operation UUID, while its parent review_attempt and task_key remain unchanged. Transport
retry of the same input reuses its operation UUID/hash. assessment input_revision must be
positive. review_tasks use the pinned policy; the service rejects assessment attempts
whose policy/target differs from that task or whose run context differs from the review.

A PASS/FAIL assessment is evidence for a task, not itself a review_history event. A task
can stay PENDING while the published retry allowance remains; its finalized PASS/FAIL
is stable. All required tasks must have a valid finalized result before aggregate grading;
a BLOCKED task keeps the aggregate NULL even if another task failed. Policy IDs, task set,
per-task results, mode/version, review timestamps and idempotent identities are thus retained
without putting a whole review inside a loose JSON document. Technical errors and permission
problems are recoverable, consume no scored retry, and do not change SRS state.

Additional personal timestamp checks: user_vocabulary.learned_at, when present, lies
between created_at and updated_at; user_lesson_progress.completed_at <= updated_at;
review_attempts.submitted_at >= started_at when present, and SUBMITTED requires submitted_at.
Aggregate outcome must equal the immutable history outcome in the same grading transaction;
policy_id on history must equal the pinned attempt policy. These are service invariants.
Other non-OPEN attempt statuses can retain a submission timestamp or have none if abandoned
before submission. All expected/state history revisions are positive integers.

`user_vocabulary` source CHECK uses explicit NULL tests: catalog requires a vocabulary
FK and all custom fields NULL; custom requires vocabulary_id NULL, non-NULL nonblank
custom_simplified/custom_meaning, optional nonblank custom_pinyin. Owner/source/target
are immutable. Saving does not set learned_at; custom study can set it but cannot grant
app vocabulary eligibility. No custom-to-catalog auto-merge. Multiple NULL catalog IDs
are valid for different custom entries. Do not impose migration-time creation timestamps
later than historical study times; timestamp backfill uncertainty is an explicit audit item.

`user_lesson_progress` is an accomplishment, not a replay session. Its completion run must
be COMPLETED, belong to this user and have the same lesson identity: composite ownership
FK covers the user; transaction validation covers lesson/version matching. A deferred
constraint trigger for that cross-table invariant should be considered during implementation
if writes are exposed outside the service. Total EXP is SUM(exp_awarded) over completed
rows; **no user_progress table/cache or EXP ledger is needed for first-completion-only EXP**.
Later non-lesson EXP/refunds would require a separate ledger design. Do not independently
store a writable total. First completion uses the reward in the pinned version.

App-eligible vocabulary is derived by joining completed user_lesson_progress to its
completion_run, the pinned lesson version, and lesson_vocabulary(role=TEACHES).
Grammar knowledge is derived analogously from lesson_grammar_rules(role=TEACHES).
No redundant learned-vocabulary/grammar flag tables are required initially. Removing a
library entry does not erase a lesson accomplishment; restoring it can retain provenance.
Mastery is always personal; no mastery column belongs on public vocabulary.

review_count/consecutive_successes are deliberate current-state aggregates of accepted
events, transactionally maintained and auditable against review_history. failed_attempts
is per review evidence, not a lifetime state column. policy_id is the normalized version
reference; do not duplicate algorithm_version in srs_states/history. algorithm_state holds
only version-specific residual data, never duplicate mastery, timestamps or count fields.
See SRS for transaction/idempotency rules and handling of legacy states without history.

## 6. Ownership, deletion, and integrity

Public content can be cached without authentication. Personal queries always constrain
the authenticated internal user ID; never accept an owner from request JSON. Composite
FKs explicitly prevent cross-user run/attempt/card links. Room partitions personal runs,
progress, strokes and outbox by verified identity; public cache is separate.

Explicit cascades: users -> lesson_runs, user_lesson_progress, user_vocabulary,
review_attempts, review_history, assessment_attempts, review_tasks; lesson_runs -> lesson_scene_progress;
user_vocabulary -> srs_states, review_attempts, review_history;
review_attempts -> review_history and review_tasks; review_tasks -> assessment_attempts;
lesson_scene_progress -> assessment_attempts. All owned composite context FKs use CASCADE
for deliberate account erasure, including assessment_attempts run/scene/task FKs. Within account erasure, composite user/card/run
references use matching CASCADE actions to avoid RESTRICT blocking erasure; this includes
user_lesson_progress.completion_run and review_attempts.run/scene FKs. Ordinary run/card
deletion is not exposed: use ABANDONED or suspend a future card instead. In particular,
deleting a run must never be used to revoke an accomplishment indirectly.

Unpublished owned associations may cascade on parent deletion: vocabulary_characters,
vocabulary_parts_of_speech, vocabulary_hsk; character_components; sentence_tokens,
sentence_grammar, grammar_examples from their owning sentence; lesson version membership,
lesson_scenes and lesson_prerequisites; template version scenes; roadmap release entries.
All other FKs RESTRICT, including learning targets, assets, policies and published versions.
Published content/associations may not be physically deleted; use archive. Catalog source
edit/delete service checks publication dependencies and historical bundle retention first.

Assets above are public catalog media/bundles only. Handwriting streams stay local in
the initial slice. Speech evaluation may stream a valid recording over authenticated HTTPS
to the backend/provider; do not insert it into public assets, JSONB, logs or backups. Default
processing is ephemeral: delete temporary recordings on success, error, cancellation and
capture replacement. Use a short maximum processing TTL with a cleanup sweep for crashes;
its exact bound and provider no-retention settings must be verified before provider launch.
Retain only bounded derived transcript/result/version metadata for progress/audit, account-
scoped with an explicit retention policy. Do not promise a provider deletes audio unless its
configured service/region contract supports that. Re-evaluation after deletion may require
fresh capture; technical trouble must not force indefinite retention. Durable voice uploads,
training reuse or diagnostic retention require a separate explicit consent/storage design.

## 7. Target compatibility and migration plan

| Area | Existing nine-table schema / previous ten-table proposal | Proposed change |
| --- | --- | --- |
| Lessons | Mutable title/type/order; many vocabulary rows; unversioned progress. | Stable identity, five bounded types, published versions, single vocabulary target, separate release ordering. |
| Execution | No scenes/templates/runs. | Versioned defaults, sparse overrides, immutable bundles and per-run resolved scene checkpoints. |
| Chinese data | Free-text radical_info; previous proposal adds radical catalog only. | Component glyph reuse, radical classification FK, ordered component occurrences, reviewed per-character classification, POS and versioned HSK. |
| Rule content | None. | Shared pronunciation/grammar/topic entities and fully annotated sentence bank. |
| Identity | Nullable unique google_sub. | Required verified subject for new authenticated accounts; no invented subjects during backfill. |
| Learning provenance | learned_at alone, lesson membership without teaching role. | First valid completion references exact run/version and TEACHES relations; saved/custom/external knowledge excluded. |
| EXP | Absent. | Immutable exp_awarded in unique first-completion row, summed per user. |
| SRS | due_at, count, algorithm_version, JSONB; no mastery/history. | next_review_at, all-required-task PASS/FAIL grading, bounded mastery, immutable policies, revision-controlled attempts and history. |
| Evaluation | No evaluator contract/storage; previous proposal treated recording as optional and scoring as future. | Required speaking, STT content match, versioned policies/assessment attempts, recoverable blockers; future detailed assessment remains distinct. |
| Assets | Free-text audio/stroke keys. | Stable public asset catalog with hashes; never expiring URLs or DB binaries. |
| Synchronization | Plan only. | Pinned offline bundles and provisional operations described; full sync remains gated. |

Future implementation should use expand/backfill/validate/contract in separately reviewed
new revisions. Keep `0001_initial.py` unchanged. Do not reset, downgrade, or drop volumes.

1. Audit an approved environment/read replica: applied Alembic versions, row counts,
   NULL identities, duplicate/blank normalized text, zero stroke counts, unknown lesson
   types, invalid JSON/state versions, existing progress/learned_at and asset keys. Back up
   and rehearse on an isolated restored PostgreSQL database; never assume empty tables.
2. Add new tables and nullable transition FKs first. Keep old columns/relationships readable.
   Populate stable IDs/mappings, import reviewed components/radicals/HSK/POS, and map asset
   keys only after object existence/hash verification. Preserve unmatched radical_info prose
   and zero/unknown stroke observations in an export/legacy column until reviewed.
3. Existing lessons containing multiple taught words cannot silently become single-target
   lessons. Preserve them as archived legacy versions/bundles under their original identities;
   introduce new single-target lessons with new IDs. Decide legacy type mapping explicitly;
   use a migration-only compatibility reader or reviewed TOPIC mapping, never invent a sixth
   runtime type. Retain old links until archival content is verifiably represented.
4. Preserve every existing accomplishment. A deterministic migration run may anchor a legacy
   completion, clearly labeled as imported in its resolution evidence, not as newly validated
   learning. Legacy completions get zero EXP unless an explicit audited retroactive grant is
   approved. Do not infer vocabulary eligibility from a legacy membership or learned_at;
   keep uncertain records ineligible until provenance is reviewed. Keep the original times;
   estimated timestamps must be documented, never described as measured history.
5. Quarantine unresolved NULL google_sub accounts for reviewed account recovery, retaining
   their data. No email merging, invented verified subjects, fake login, or silent deletion.
   Enforce required subjects only after reconciliation. Existing test fixtures will need
   separate future updates when the actual constraint changes.
6. Preserve existing SRS UUIDs/due instants/counts/state; do not guess historical grades or
   mastery. Map known algorithms explicitly; unknown `unimplemented-v0` schedules remain
   inactive/read-only until an enrollment/migration policy is approved. A future migration
   needs a recorded baseline (old count/mastery uncertainty) before history-based audits;
   do not fabricate missing review_history. Rename due_at only after compatibility readers
   exist; backfill policy FKs and revisions without recomputing due times silently.
7. Validate backfills, ownership/cardinality/DAG constraints and complete immutable bundles;
   switch readers/writers, monitor reconciliation, then separately approve removal of old
   columns/links. Strong constraints can use staged validation where PostgreSQL permits it.
   Old columns, lexical merges, multiword-lesson splitting, NULL-subject enforcement,
   irreversible normalization and schedule resets are **potentially destructive changes**.
   No such contract/drop step is included in this documentation change.
8. Later tests must cover migration upgrade with nonempty fixtures, downgrade limitations,
   no reference loss, `alembic check` on an isolated database, duplicate completion/review,
   account isolation, and client bundle compatibility. No migration or database tests are
   run for this design-only task.

## 8. Review decisions still open

Approve interval durations/difficulty factors, permitted SRS task profiles and retry/hint
limits, custom-card enrollment, accessible alternative task equivalence, EXP values and
legacy grants, HSK edition/licensing, etymology reviewers, provider choice/region/processing
TTL and derived-data retention, offline validity, account deletion/recovery, and historical
renderer support. Speaking is required by default; STT is content-only; future assessment
starts at threshold 70/100; aggregate SRS PASS/FAIL changes mastery by +1/-1; and sentence
minimum defaults to 1. These finalized requirements are no longer listed as open decisions.

## 9. Changes from the preceding design

The 42-table target gains three narrowly scoped evaluation/task tables (45 total).
review_history.outcome replaces the previous four-rating proposal, review_attempts pins
its scheduling policy/aggregate result, and scene progress gains recoverable BLOCKED state.
Required speech must pass STT content matching or an explicitly recorded accessible
alternative; mere capture no longer completes speaking. No scientific pronunciation score
is inferred from recognition. Future specialized assessment uses its own mode/version and
configurable 70/100 starting threshold. A blocked evaluator can defer completion, never
create a false FAIL. Default translation eligibility needs one available validated sentence,
with per-lesson overrides. Incremental delivery is specified in the implementation plan.

The target remains a proposal beyond Slice 1. The immutable initial migration remains
unchanged; the new foundation revision follows the expansion described in content-authoring.md.
