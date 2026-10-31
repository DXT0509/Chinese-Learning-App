# Phase 4.1B: authoritative three-stage review

The current [Phase 4.2 integration contract](srs-phase-4.2-integration.md) additionally
supports optional idempotent creation via `request_id`, mastery distribution and pinned
previous/resulting mastery. See [stabilization verification and device setup](android-srs-review.md).
These additions leave the scheduling/grading rules and migration history below unchanged.

Phase 4.1C adds [deterministic catalog policy preparation](srs-policy-preparation.md).
Its explicit Hán-Việt-cued recall rule supersedes the manual-only preparation
limitation below for eligible records. Manual sense review remains available for
unresolved entries. Migration 0012 and the 2,148-policy bundle were
[deployed on 2026-10-28](runbooks/srs-policy-deployment-20261028.md) after separate
explicit authorizations. See the [Phase 4.2 handoff](srs-phase-4.2-integration.md).

The backend grades submitted answers in HANZI → PINYIN → optional POS order.
`ReviewEngine` persists answers and assistance, then constructs `ValidatedReview`
from the first answer of each applicable stage. It calls the existing
`SrsService._complete_in_transaction` under the same transaction and lock order.
`srs_state.transition` and every approved interval/promotion rule are unchanged.
Android UI is unchanged.

## Content readiness and editorial contract

Curated dictionary approval is not approval of a Vietnamese-to-Hanzi question.
No production review policies are installed by this change. Consequently existing
catalog entries remain saved and visible, but are excluded from graded target
generation until a reviewed policy is explicitly installed. The foundation audit
identified 816 shared-gloss candidates, 2,181 multiple-gloss entries and 214 compound
POS labels; these are historical audit counts, not new semantic certifications.

An initial [three-policy bundle](datasets/srs-review-policies-v1.json) is prepared
for the actual catalog identities of the familiar singular listener and singular
male/female referents. Its Vietnamese contexts, pronunciation identities and source
`pronoun` labels were inspected locally. The reviewer attribution identifies Codex
implementation review, not an external human review or provider attestation. It is
not installed. The bundle enables concrete three-stage questions after explicit
deployment and operator policy installation; other entries remain excluded until
their own sense policies are reviewed.

`srs_target_policies` binds one operator-reviewed policy to the exact catalog UUID,
version and checksum. The policy records a version-scoped sense key, Vietnamese
context, reviewer identity and an ambiguity-resolution explanation. The reviewer
must disambiguate synonyms and alternative meanings/readings, including held
records; a unique gloss alone is insufficient evidence. If reliable context cannot
be authored, leave the record excluded. Do not install an ambiguous question and
then reject another linguistically valid word. Policies never change vocabulary,
collection membership or mastery.

The resolver derives the accepted Hanzi and pronunciation from the selected lexical
identity, never an unrelated synonym or another reading of the same written form.
It checks Simplified form, explicit syllable count, numbered/marked equivalence,
lexical key and a nonempty Vietnamese meaning. It does not invent alternate readings.
Additional genuine readings need their own curated pronunciation identity and policy.

The reviewer selects supported POS categories actually present in the source label.
Supported codes are `noun`, `verb`, `adjective`, `adverb`, `pronoun`, `classifier`,
`numeral`, `conjunction`, `preposition`, `particle`, `interjection`. Source `measure word`
maps to `classifier`. Splitting a source label establishes category support only;
the reviewer establishes sense applicability. Gloss position and delimiter position
are never treated as aligned senses. The exact selected set is required for POS:
one category uses SINGLE_SELECT; multiple use MULTI_SELECT. Missing or unreliable
annotations require `pos_skip_reason`, no accepted POS, and an explicit
`NOT_APPLICABLE` skipped-stage record. Unknown source categories are not fabricated
or silently mapped to a generic correct answer.

Operator JSON array contract (illustrative identity; replace from the actual catalog):

```json
[
  {
    "vocabulary_id": "00000000-0000-0000-0000-000000000002",
    "content_version": 1,
    "checksum": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "policy_version": "editorial-1",
    "sense_key": "reviewed-sense-key",
    "vietnamese_prompt": "A reviewed Vietnamese definition with disambiguating context",
    "reviewed_by": "Operator reviewer",
    "ambiguity_resolution": "Document why plausible synonyms and readings do not fit this context",
    "accepted_pos": [],
    "pos_skip_reason": "MISSING_OR_UNRELIABLE_POS"
  }
]
```

Run `python -m scripts.review_policies --file <file>` to validate without writing;
`--install` explicitly installs the validated array in one transaction. Unknown or
extra fields, stale identity, unsupported POS, missing meanings and conflicting
existing policies are rejected. This CLI is operator-only, with no HTTP write route.
Corrections to installed policies require a new catalog version/checksum, preserving
pinned attempts. It is a strict local authoring workflow, not an automatic linguistic
reviewer. The reviewer is responsible for semantic prompt quality.

`GET /api/v1/me/srs/review-targets?limit=50&offset=0` returns two separate lists:
`items` with eligible saved IDs and their server-derived `due` flag, and `excluded`
with saved IDs, reasons and editorial flags. It checks publication independently of
policy. Flags identify shared glosses, multiple meanings/readings, compound POS and
missing POS. Pagination covers the active collection before filtering; advance
offset by limit even if items is empty. Unreviewed targets never enter `items`.
`python -m scripts.review_policies` prints a full catalog policy-exclusion report
for operators without printing solutions or changing data.

Existing `/due` and dashboard counts remain collection/schedule counts, including
words needing editorial work. The dashboard's `grading_available` means this user
has at least one visible saved word with a valid policy. Use `/review-targets` to
generate exercises. Legacy initialization of an ungradable saved word still returns
`grading_available: false`, `reason: REVIEWED_POLICY_REQUIRED`; answer/question
operations reject it with 409. Newly installed policies require a new session;
initialized targets are pinned and never upgraded silently.

## Normalization

Hanzi uses Unicode NFC and trims surrounding whitespace only. Internal whitespace,
punctuation, Traditional forms and synonymous words remain different. There is no
Traditional-to-Simplified conversion and no compatibility-width folding.

Pinyin uses NFC, lowercase, whitespace normalization, ASCII/curly apostrophe syllable
separators and equivalent `ü`, `u:`, `v`. Numbered input must number every syllable
with 1–5, including neutral 5. Digits themselves delimit syllables, so `ni3hao3`
and `ni3 hao3` agree. Tone-marked input requires explicit spaces/apostrophes between
syllables; a syllable without a tone mark is neutral, not a wildcard for any tone.
Thus `shén me` and `shen2 me5` agree, but `shen2 me2` fails. `xī'ān` cannot match
`xiān`, and `nu3` cannot match `nü3`. Mixed numbered/marked syllables and partly
numbered strings fail. Unseparated marked multi-syllable input is conservatively
rejected; the Android input instructions must explain spaces/apostrophes. The
comparison uses vetted target syllables rather than guessing segmentation.

## Actual HTTP workflow and Phase 4.2 Android contract

All routes below are relative to `/api/v1/me/srs`, require Bearer authorization,
and return `Cache-Control: no-store`. `/docs` exposes the typed input, question,
feedback and finalization schemas. Clients cannot submit correctness, timing,
eligibility, policy, mastery or schedule fields; extra request fields yield 422.

| Method | Route | Purpose |
| --- | --- | --- |
| GET | `/review-targets?limit=50&offset=0` | Gradable collection page plus exclusions |
| POST | `/sessions` | Start a server-identified attempt using owned `saved_id` |
| GET | `/sessions/{attempt_id}/question` | Resume/current question and submitted-stage feedback |
| POST | `/sessions/{attempt_id}/submissions` | Answer, hint or explicit post-answer reveal |
| POST | `/sessions/{attempt_id}/finalize` | Atomically finalize all stages and return SRS state |

Start body: `{"saved_id":"<owned-saved-uuid>"}`. Start returns 201 with `attempt_id`,
saved ID, DUE/PRACTICE mode, UTC start time, content version, grading availability,
ordered applicable stages and skipped stages. No solution or policy details are
returned. Fetch `/question` after starting. Example initial question:

```json
{
  "attempt_id": "00000000-0000-0000-0000-000000000003",
  "stage": "HANZI",
  "expires_at": "2026-10-27T03:30:00Z",
  "status": "IN_PROGRESS",
  "disabled_stages": {"POS":"MISSING_OR_UNRELIABLE_POS"},
  "skipped_stages": [{"stage":"POS","status":"NOT_APPLICABLE","reason":"MISSING_OR_UNRELIABLE_POS"}],
  "feedback": [],
  "question": {"prompt_vi":"Reviewed Vietnamese context", "input_mode":"TEXT"}
}
```

Submit a new UUID idempotency key for each deliberate learner action. Preserve it
across network retries; resend the identical body. Answer examples:

```json
{"submission_key":"00000000-0000-0000-0000-000000000004","stage":"HANZI","answer":"学"}
```

```json
{"submission_key":"00000000-0000-0000-0000-000000000005","stage":"PINYIN","answer":"xue2"}
```

```json
{"submission_key":"00000000-0000-0000-0000-000000000006","stage":"POS","answer":["verb"]}
```

These illustrate shapes, not a deployable semantic policy. POS always submits an
array even for single selection. The question supplies all supported category
options without marking the correct ones. Android maps their stable codes to
Vietnamese resources and uses `input_mode` to choose radio buttons or checkboxes.

Submission returns the same stage response shape, `submission_correct`, first-answer
feedback and the next question. PINYIN shows Hanzi only after HANZI submission.
POS appears only after PINYIN submission. `first_correct` never changes on retries.
`correct_answer` appears only for stages with a sealed actual answer; unsubmitted
keys and future answer lists are never sent. Feedback after submission is ordinary
education and is not treated as requesting assistance.

For a hint, send `action: HINT`, the current stage and key, with no answer. It records
assistance, returns a general instruction and does not advance the stage or reveal
its key. Explicit `action: REVEAL` requests are accepted only after that stage's
first actual answer; premature reveals return 409. Hints and accepted explicit
reveals permanently disqualify PASS. Such events can also be recorded against an
answered stage before finalization. Learners may retry an answered stage with a
new key for practice without overwriting first correctness. A single wrong first
answer makes the outcome FAIL, but remaining stages stay available.

When status is `READY_TO_FINALIZE` and stage is absent, POST `{}` to `/finalize`.
Example resulting response:

```json
{
  "attempt_id":"00000000-0000-0000-0000-000000000003",
  "outcome":"PASS", "scheduling_applied":true, "mode":"DUE",
  "state_after": {
    "mastery_level":0, "phase":"LEARNING", "phase_step":1, "level_progress":0,
    "next_review_at":"2026-10-27T03:10:00+00:00",
    "last_reviewed_at":"2026-10-27T03:00:00+00:00"
  },
  "completed_at":"2026-10-27T03:00:00Z",
  "feedback":[
    {"stage":"HANZI","first_correct":true,"assisted":false,"correct_answer":["学"]},
    {"stage":"PINYIN","first_correct":true,"assisted":false,"correct_answer":["xue2"]}
  ]
}
```

Android must render server state and refresh dashboard/progress after finalization;
it must not calculate mastery, deadlines or PASS. `scheduling_applied: false` means
practice/stale generation, even if outcome is PASS. Do not treat DUE mode alone as
proof of applied progression. Persist attempt ID and pending request body/key for
network recovery using existing session-safe storage conventions; this phase adds
no Android storage or UI implementation. Do not place session credentials in plain
preferences. No future question should be preloaded from dictionary answer data.

401 means authenticate; foreign/unknown attempts return 404; 409 covers stage order,
conflicting key, unavailable/stale target, premature reveal or incomplete finalization;
410 means expired; 422 means invalid request; 429 means the 128-event attempt limit.
On 409 fetch the question to reconcile; on expiry/limit offer a new session. Duplicate
requests return their originally stored submission response, which may refer to an
earlier stage; fetch `/question` for the latest position.

## Atomicity, expiration and database changes

Every mutation locks owned saved progress then its attempt, matching the scheduler.
Answer correctness is computed on the server and the raw original answer, action,
timestamp, verdict, key and exact response are appended to a JSONB journal. A
PostgreSQL trigger rejects journal truncation/replacement; 0011's trigger still
protects pinned targets and completed history. No learner HTTP route writes policies.
Authenticated owner lookup precedes feedback, replay and finalization.

All applicable stages must have an actual first answer before finalization, including
failed attempts. The evaluator derives PASS only from all correct first answers
without assistance. One atomic finalization changes the SRS schedule at most once;
the existing generation check converts concurrent stale attempts to practice. Early
practice never becomes due merely by crossing a deadline. Finalization replay
returns the original outcome/state/time; replay after expiry also works for completed
attempts. An identical old submission replays its exact stored response, including
after completion/expiry; changed payload with its key returns 409.

Unfinished attempts expire exactly 30 minutes after initialization. No scheduler or
mastery action runs on abandonment or expiry; history stays intact. Start a fresh
session with a new server UUID to restart, with eligibility recomputed from the
current schedule. An expired/incomplete attempt cannot be finalized for progression.
There is no auto-failure job, penalty on each wrong stage or abandonment penalty.

Additive migration `0012_srs_review_engine` adds `submissions JSONB NOT NULL DEFAULT
'[]'` to existing attempts, one reviewed-policy table and one append-only trigger.
It leaves all existing columns and rows intact. Existing attempts get an empty
journal. Historical migrations 0001–0011 and `srs_state.py` are unchanged. Downgrade
refuses history loss. No development migration, real learner attempt or Android
change is part of this implementation.

See [verification](srs-review-verification.md) and the
[0012 operator deployment procedure](runbooks/srs-0012-deployment.md).
