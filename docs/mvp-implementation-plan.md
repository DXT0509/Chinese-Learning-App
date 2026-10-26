# Incremental MVP implementation plan

## Phase 3.4 implemented: personal vocabulary

The authenticated dictionary-to-wordbook slice now supports exact-entry save/status,
owner-scoped search with cursor pagination, retained inactive entries and confirmed removal.
Android Learning links to the wordbook; existing detail renders saved state. Curriculum
completion, EXP, SRS and translation eligibility remain independent and unchanged.
See [design, validation and manual rollout](personal-vocabulary-design.md).


Status: **Slices 1 and 2 implemented; slices 3-8 remain planned**, 2026-10-18.
See [content authoring](content-authoring.md) for the bounded preview contracts,
legacy compatibility and local workflow. Read [schema](database-design.md),
[engine](learning-engine-design.md), [examples](lesson-examples.md), [SRS](srs-design.md),
[architecture](architecture.md), [authentication](authentication.md), and
[development guide](development-guide.md).

## Delivery rules and dependencies

Keep the existing health demo runnable after every slice. The 45-table proposal describes
the target, not the next migration. Nine tables already exist; “add/adapt” below means
reuse their stable IDs and preserve rows, introduce only needed columns/constraints, and
leave unrelated legacy data readable. A table named as a dependency is not created again.
Every schema change later needs a new reviewed Alembic revision, a nonempty-data upgrade
test on isolated PostgreSQL, and `alembic check`. Never rewrite 0001_initial or reset data.

Use small concrete services and existing module boundaries. Keep user data protected from
the first personal endpoint; an unfinished auth slice never authorizes fake login. Production
session storage must be designed before its migration. Scene capabilities are truthful:
an intermediate lesson marked “preview” or incomplete cannot award EXP, durable learned
knowledge or mastery before all required speaking/writing requirements can actually pass.

| Slice | Minimum tables added/adapted in this slice | Dependencies / runnable result |
| --- | --- | --- |
| 1. Database foundation and content authoring | Adapt vocabulary, characters, vocabulary_characters, lessons, lesson_vocabulary; add assets, lesson_versions, lesson_templates, lesson_template_versions, lesson_template_scenes. | Existing initial schema and isolated PostgreSQL. Local reviewed content authoring/validation produces one immutable bundle without user flows. |
| 2. Authentication and basic learning endpoints | Preserve users and legacy progress; add password_credentials, auth_sessions, refresh_credentials, lesson_runs and lesson_scene_progress. | Slice 1, email/password credentials and revocable application sessions. Google linking is deferred until pre-release. Authenticated learner can start/resume a versioned preview run. |
| 3. One vocabulary lesson through Scene Engine | Add components, radicals, character_components, parts_of_speech, vocabulary_parts_of_speech for its authored pages; adapt user_vocabulary for first-study/library timestamps. | Slices 1–2. End-to-end 你 lesson execution and checkpoint/EXP transaction using the same coordinator, with unsupported required activities explicitly pending. |
| 4. STT speaking integration | Add evaluation_policies and assessment_attempts in their lesson-context subset. Add BLOCKED scene status/checkpoint validation. | Slices 2–3, Mandarin-capable STT adapter, microphone permission, network/provider configuration and retention checks. Real speaking content PASS/FAIL with recovery. |
| 5. Listening transcription and handwriting foundation | No new server tables; use assets, vocabulary/characters, scene progress, evaluation policies/attempts where needed. Room stroke/checkpoint tables need explicit local schemas/migrations scoped to identity. | Slices 3–4. Listening scene plus natural Canvas strokes/corrections and final selected-text grading. Full required vocabulary flow can now pass for real. |
| 6. Additional lesson types and eligibility | Add pronunciation_rules, pronunciation_examples, grammar_rules, sentences, sentence_tokens, sentence_grammar, grammar_examples, learning_topics, lesson_grammar_rules, lesson_pronunciation_rules, lesson_topics, lesson_prerequisites, lesson_scenes, roadmap_releases, roadmap_entries. | Slices 1–5. One small runnable sub-slice per pronunciation, grammar, topic, roadmap review; restricted translation follows annotated content/knowledge prerequisites. |
| 7. SRS and aggregate mastery | Adapt srs_states; add srs_policies, review_attempts, review_tasks, review_history. Extend assessment_attempts with nullable review/task context FKs now that parents exist. Add hsk_standards, hsk_levels, vocabulary_hsk when publishing the first versioned HSK difficulty map. | Slices 2, 4–6 and approved task profiles/interval factors. One complete due review produces one aggregate PASS/FAIL event and one schedule transition. |
| 8. Offline synchronization and integration | Reuse learning tables; add only separately designed operation receipts/cursors/tombstones required by actual sync operations. Identity-scoped local outbox/checkpoints. | All preceding slices; protocol and conflict/retention decisions. Offline checkpoints/retries reconcile without duplicate EXP/grades or account leakage. |

This inventory assigns every proposed table once: slices 1–3 provide a deliberately
small foundation; later slices introduce only their own entities. HSK is not required
to render the first word: until its edition/mapping is approved, use unclassified metadata.
The final assessment_attempts review-task FKs cannot exist in slice 4 while review_tasks
is absent; add those nullable columns/constraints in slice 7, keeping lesson attempts valid.
Similarly, delay schema FKs for future grammar/topic content rather than creating empty
placeholder tables. Do not implement the entire target schema to satisfy a future reference.

## 1. First recommended slice: publish one reviewed vocabulary definition

User-visible outcome: a reproducible reviewed definition for 你 can be compiled and
inspected without launching a learning feature. Use a local content import/validation
command rather than building an admin web app or exposing unauthenticated authoring routes.
The command writes drafts, validates one vocabulary target and a minimal template, and
publishes an immutable bundle with stable asset references. The preview can show metadata
or decoded bundle content; it does not simulate completed learning or call an evaluator.

Implement only the ten table responsibilities listed for slice 1. Existing associations
need a compatibility transition from lesson_id to lesson_version_id; keep old links and
provide an explicit mapping/backfill path instead of replacing existing membership in place.
Vocabulary/character media transitions similarly preserve old keys until verified mapped.
Templates may describe later scenes, but unsupported execution is visibly unavailable;
neither provider tables nor all thirteen renderers are prerequisites for authoring validation.
An initial template can use only supported explanation/reference scenes; do not advertise
it as the complete learner vocabulary lesson until the remaining required capabilities ship.

Acceptance criteria:

1. A separately reviewed new migration upgrades an isolated database containing representative
   legacy users, multiword lessons, repeated characters, progress and SRS states without
   losing their IDs, references, original columns or values. Initial migration stays byte-for-byte
   unchanged. No assumed conversion of uncertain old learning provenance or verified identity.
2. A controlled authoring command creates one stable vocabulary lesson identity and DRAFT
   version using one exact template version and exactly one TEACHES vocabulary entry.
   Repeated execution uses explicit draft identity/version and cannot duplicate publications.
3. Invalid targets/asset keys/contracts/duplicate scene positions are rejected with generic
   safe errors; zero/multiple targets cannot publish as VOCABULARY. No SQL/payload/secrets logged.
4. Publishing produces a retrievable immutable bundle and recorded SHA-256, pins exact versions,
   and rejects in-place edits to published definitions. A correction creates a new version;
   the earlier bundle remains identical and available.
5. PostgreSQL constraints and a nonempty upgrade test pass; isolated `alembic check` reports
   no unintended drift. Backend tests pass; health remains usable independently of DB liveness.
6. No authentication shortcut, personal learning API, Android feature, EXP award, SRS grade,
   provider integration or destructive legacy-column removal is bundled into this slice.

These are Slice 1 acceptance criteria; executed checks and environment limitations are
recorded in docs/validation.md. The bundled sample imports as DRAFT; explicit publication
produces only a CONTENT_PREVIEW, with no learning or evaluator capabilities.

## 2. Email/password identity and basic learning access

Implemented: Argon2id password credentials, normalized unique login email, stable user UUIDs,
10-minute opaque access tokens and rotating/revocable 30-day refresh families. Legacy users
and progress are unchanged; matching unverified emails never merge identities. Google
Sign-In is deferred until pre-release, with future explicit linking to an existing UUID.

Android implements registration/login, validation, loading/errors, successful navigation,
Keystore-encrypted atomic session storage, refresh/expiration handling and logout. Protected
catalog/bundle/start/resume/checkpoint APIs pin immutable published versions and enforce
ownership. A per-owner request UUID deduplicates run creation. Previews require server
and caller opt-in and have no completion, EXP or SRS path. Existing user_lesson_progress
is deliberately untouched. See [authentication](authentication.md) and
[verification](slice2-verification.md) for contracts, commands and release limitations.

Acceptance tests cover registration/login/duplicates, password hashing, access expiry,
rotation/logout/replay revocation, unauthorized and foreign-owner requests, idempotent
run/checkpoint operations and restoration after newer publications. Nonempty migration
rehearsal and Slice 1 regression tests remain required. Email verification, recovery,
distributed abuse controls and Google linking remain pre-release work.

## 3. One vocabulary lesson coordinator

Build one repository/ViewModel/state-driven sequence and reusable initial renderers; use
resources for Vietnamese text, lifecycle-aware StateFlow and constructor injection. Render
the 你 introduction, information, reviewed components and stroke demonstration. Add remaining
required scene contracts to the same coordinator; unsupported recording/writing remains
pending behind explicit development capability gating, never fake PASS.

Define/test the atomic first-completion operation and once-only EXP against deterministic
supported fixtures; do not expose completion for the full lesson until speaking and
handwriting gates are live in slices 4–5. There is no intermediate product decision to
make required speech optional. Acceptance: resume preserves pages/version; duplicate and
concurrent completion cannot double-award EXP; saving/custom entries do not grant eligible
knowledge; no direct Retrofit/Room access from composables. The complete flow ships only
after later required capabilities pass, rather than claiming this foundation alone is final.

## 4. Mandarin STT speaking

Choose a provider through a small spike verifying Mandarin, recording format, timeouts,
SDK/dependency compatibility and data retention; do not assume a vendor's specialized
pronunciation metrics. Implement the provider-independent PronunciationEvaluator adapter
for STT_CONTENT_MATCH and server-authoritative text normalization/comparison. No accuracy
percentage, tone judgment or 70-point threshold in this mode.

Acceptance: valid matching/nonmatching transcripts produce content PASS/FAIL, permission
denial offers rationale/retry/settings, invalid input and technical errors preserve the
same run without a scored failure, new recordings cannot receive stale callbacks, and
temporary audio is cleaned on every terminal path plus crash TTL. All derived results
store mode/policy/adapter/provider metadata. A required speaking scene can now pass for
real or use an explicitly supported and recorded accessible alternative.

## 5. Transcription and natural handwriting

Ship keyboard LISTENING_TRANSCRIPTION first as a runnable sub-slice, then Canvas drawing,
undo/retry and manual character selection. Preserve ordered point streams and pen lifts;
do not snap strokes. Recognized/candidate/selected/final text states stay distinct. Compare
final text with reviewed accepted variants; do not call a recognition confidence a writing
quality score. Add handwriting AI only after a separately verified assessment contract.

Acceptance: one character, repeated characters and short phrase input survive correction
and lifecycle recreation; replay/hint/attempt policy works; local private data is identity
scoped. Complete the full 你 learning lesson with genuine required speech and handwriting
study activity; first completion awards EXP once and grants only its TEACHES entry.

## 6. Mixed content and eligible translation

Deliver pronunciation then grammar then topic then roadmap review as separate runnable
sub-slices, adding only each content entity/join when used. Reuse renderers. Citation and
contextual Pinyin/audio stay separate; STT can check spoken words but cannot grade sandhi.
Add the sentence bank/grammar prerequisites when conditional translation first ships.

Acceptance: all five lesson types execute through the same coordinator, published updates
preserve pinned runs and existing accomplishments, and prerequisite cycles/references are
rejected under the publication lock. Restricted translation requires completed-app TEACHES
vocabulary and grammar, excludes custom/external/saved-only knowledge, validates all sentence
variants, and defaults to one available eligible sentence. Per-lesson count overrides and
frozen skip behavior are tested. Roadmap REVIEW completion does not itself grant mastery.

## 7. Multi-task due SRS

Approve the first supported required-task profile and interval/difficulty parameters.
Use 0..5 aggregate mastery, all-required-task PASS or complete valid FAIL, +1/-1 bounds,
and shorter failed relearning. Initial tasks can use meaning/Pinyin text and STT speaking;
unsupported handwriting assessment must not be required by a launched profile. Preserve
one parent review across retries; policy IDs and relational task/evaluation evidence are
the audit chain. Specialized assessment remains future with its own initial 70/100 threshold.

Acceptance: all-pass advances once; any finalized valid fail in a complete set decreases
once; a blocked required task cannot change state; early/stale/replayed attempts cannot
advance or decrease mastery; concurrency/idempotency/history rollback checks pass. A
high-mastery failure receives a short relearning due time. Account and policy isolation,
STT score NULL, and unchanged legacy schedules are covered before rollout.

## 8. Offline sync and integration gates

Define the actual operation protocol, receipts/payload hashes, revision conflicts, leases,
cursors/tombstones and account-switch behavior before adding WorkManager. Download pinned
bundles and persist local changes/outbox atomically. Required remote speech may remain
pending offline; never count an outage as FAIL or retain voice indefinitely for an outbox.
Derived task outcomes can sync after policy/ownership/revision validation.

Acceptance: offline/resume/upload retries cannot duplicate completion EXP or aggregate
grades; stale reviews are reconciled as practice; local current-target gating cannot bypass
server accepted core work; account changes never send another user's data. Run integration
tests across FastAPI/PostgreSQL and Android repositories/ViewModels, plus real device/emulator
checks for microphone permission, capture, Canvas and lifecycle. Run the documented backend
and Android checks, migration upgrades and isolated `alembic check`; distinguish device
validation from unit tests in reports. Authentication, privacy cleanup and provider failure
paths must remain covered as the sync protocol broadens.

## Difference from the previous delivery proposal

The new plan replaces coarse A/B/C schema grouping as a delivery sequence with eight
explicit steps and smaller sub-slices. Required speech/STT and multi-task PASS/FAIL are
final requirements; optional microphone capture and four-rating mastery are superseded.
One eligible sentence is the default; a higher count requires a lesson override. The
next implementation task is Slice 3; Slices 1 and 2 are implemented with the boundaries above.

## Phase 3.1 dictionary foundation — implemented scope

The independent Custom Vocabulary sub-phase adds source research, a licensed local
CC-CEDICT v1 importer, shared indexed lookup data, authenticated search/detail contracts
and PostgreSQL tests. See [foundation and limitations](dictionary-foundation.md) and
[source selection](dictionary-source-evaluation.md). English data is labeled English;
Vietnamese/Sino-Vietnamese coverage remains absent. This sub-phase does not change the
learning delivery plan below or implement handwriting, Android dictionary UI or personal
collection persistence. Phase 3.2 can consume nullable source-grounded lookup contracts;
saving entries needs a separately authorized ownership/schema slice.
