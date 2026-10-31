# Phase 4.2 Android integration handoff — 2026-10-28

For the current handwriting experience and full-population randomized session selection,
see [Phase 4.3](srs-phase-4.3-experience.md). Deploy its compatible source backend before
the current Android build; no new migration is required.

Local development is deployed at revision `0012_srs_review_engine` with 2,148
installed policies. See the [deployment receipt](runbooks/srs-policy-deployment-20261028.md).
The Phase 4.2 Android review UI is implemented. Integration stabilization adds the optional
creation request key, dashboard distribution and final mastery fields described below.
Restart/reload the API with this source before installing the updated Android build; the
earlier deployment receipt does not establish that these new contracts are running.

Base URL: `http://127.0.0.1:8000/api/v1` locally. Android device transport follows
the existing [USB development setup](android-usb-development.md). Release continues
to require HTTPS. All SRS routes require the existing Bearer session and return
`Cache-Control: no-store`. Use the existing authenticated repository and session
storage; do not put tokens in DataStore or plain preferences.

## Counts, queue and target selection

| Method | Path relative to `/api/v1/me/srs` | Contract |
| --- | --- | --- |
| GET | `/dashboard` | `as_of`, `available_count`, `due_count`, `suspended_count`, `grading_available`, `mastery_distribution` |
| GET | `/due?limit=50` | `as_of`, `items` of owned due progress; limit 1–100 |
| GET | `/review-targets?limit=50&offset=0` | `items:[{saved_id,due}]`, `excluded:[{saved_id,reason,editorial_flags}]`, `offset`, `limit`; limit 1–100 |
| GET | `/progress/{saved_id}` | Owned progress plus `available` |

Progress contains `saved_id`, `vocabulary_id`, `mastery_level`, `phase`, `phase_step`,
`level_progress`, `next_review_at`, `last_reviewed_at`, `is_active`,
`schedule_version`, `due_review_count`, `failure_count`, `practice_count`.

Dashboard and `/due` are publication/collection/schedule counts and can include
records without grading policies. `grading_available` means this user has at least
one gradable saved word. Generate exercises from `/review-targets`; use its `due`
flag to distinguish due targets from practice. Pagination covers the collection
before filtering; advance offset by limit even when `items` is empty. Exclusions
are editorial/content states and must not be submitted as learner failures.
`progress.available` is publication/active availability, not policy approval.

`mastery_distribution` always contains six objects ordered 0?5:
`{"mastery_level":0,"count":12}`. Counts use the same active, published/available
saved-word population and SQL snapshot as `available_count` and `due_count`, including
words without grading policies. Their sum equals `available_count`. Empty buckets
are explicit zeros; suspended and removed records and other owners are excluded.

## Start and resume

`POST /me/srs/sessions` with an owned saved-word identity:

```json
{"saved_id":"<owned-saved-uuid>","request_id":"<new-v4-uuid>"}
```

Persist the entire body before sending. `request_id` is optional for legacy clients;
updated Android always supplies it. It is stored as the existing attempt UUID, whose
primary key and saved-row locking enforce uniqueness without a schema migration.
Repeating the same owned saved ID/key returns the original 201 initialization response,
even after completion or expiry. It never starts a replacement or resets the TTL.
GET question then resolves current state/expiry. A rolled-back creation can be retried
with the same key. Reusing a key for another saved identity or owner returns generic
409, with no foreign attempt contents. Ownership is checked before any replay lookup.
Legacy requests without a key retain their historical new-attempt behavior.

The 201 response contains `attempt_id`, `saved_id`, `mode` (`DUE` or `PRACTICE`),
`started_at`, `content_version`, `grading_available`, `applicable_stages`,
`disabled_stages`, `skipped_stages` and nullable `reason`. An ungradable legacy
initialization returns `grading_available:false`; it cannot be answered or finalized
for grading. Do not treat that as a learner error.

`GET /me/srs/sessions/{attempt_id}/question` starts or resumes rendering. Its response
has `attempt_id`, nullable `stage`, `expires_at`, `status`, `disabled_stages`,
`skipped_stages`, `feedback`, optional `question`, `submission_correct`, `hint_vi`.
Nullable fields can be omitted. Status is `IN_PROGRESS`, `READY_TO_FINALIZE` or
`COMPLETED`. `question` has `input_mode` (`TEXT`, `SINGLE_SELECT`, `MULTI_SELECT`)
and applicable `prompt_vi`, `simplified`, `options`.

For HANZI, render **the complete `question.prompt_vi`**. Automatic questions include
the required Hán-Việt cue, character count and Vietnamese meanings. Do not truncate,
paraphrase or remove any of them. These cues are part of the question from the start
and do not count as requested hints. Do not derive a shorter question from dictionary
glosses. This is cued lexical recall, not unrestricted translation.

## Submit the three stages

All answer actions use `POST /me/srs/sessions/{attempt_id}/submissions`.
Generate a new UUID `submission_key` for each deliberate action; preserve the exact
body/key for network retries. The examples below show request shapes only.

```json
{"submission_key":"<new-uuid>","stage":"HANZI","answer":"学"}
```

```json
{"submission_key":"<new-uuid>","stage":"PINYIN","answer":"xue2"}
```

```json
{"submission_key":"<new-uuid>","stage":"POS","answer":["verb"]}
```

`action` defaults to `ANSWER`. HANZI/PINYIN require strings; POS always requires an
array, including single selection. Render `input_mode` and all supplied options.
Stable POS codes are `noun`, `verb`, `adjective`, `adverb`, `pronoun`, `classifier`,
`numeral`, `conjunction`, `preposition`, `particle`, `interjection`; map these to
Vietnamese Android string resources. The server determines the correct categories.

Order is HANZI → PINYIN → applicable POS. PINYIN shows Hanzi only after HANZI was
answered. Accept numbered Pinyin with every syllable numbered 1–5, or tone-marked
syllables separated by spaces/apostrophes. Neutral tone is 5 (or an unmarked syllable
in marked format); missing tones are not wildcards. See the
[normalization contract](srs-review-engine.md#normalization).

Submission returns the same stage-response shape, including `submission_correct`,
feedback and the next question. Feedback entries contain `stage`, `first_correct`,
`assisted` and, only after an actual answer for that stage, `correct_answer`.
Retries never overwrite first-answer correctness. Continue remaining stages after
an error; an individual stage error does not immediately reschedule the word.

A hint uses the current stage/key with `"action":"HINT"` and no `answer`.
Explicit reveal uses `"action":"REVEAL"` and no answer, only after that stage's
first actual answer. Requested assistance disqualifies PASS. Normal feedback after
an answer is not a hint request. Explicit skipped POS is `NOT_APPLICABLE`, with its
reason in `skipped_stages`; do not manufacture a POS answer for it.

## Complete and display the resulting schedule

When the server returns `READY_TO_FINALIZE` with no current stage, send:

`POST /me/srs/sessions/{attempt_id}/finalize` with body `{}`.

Response fields are `attempt_id`, `outcome` (`PASS`/`FAIL`), `mode`,
`scheduling_applied`, `state_after`, `previous_mastery_level`,
`resulting_mastery_level`, `completed_at`, `feedback`. `state_after`
includes `mastery_level`, `phase`, `phase_step`, `level_progress`,
`next_review_at`, `last_reviewed_at`. Render the server result and refresh dashboard,
targets and progress. Do not calculate correctness, mastery, deadlines or intervals
on Android. `scheduling_applied:false` means no progression, even for a PASS/DUE
attempt. Finalization is atomic and replay returns its original result. Previous mastery is
from immutable `attempt.state_before`, pinned at initialization, and resulting mastery
is from immutable `attempt.state_after`. Neither comes from a separate progress read.
For a stale/practice attempt, `scheduling_applied:false` still means no progression
was applied by this attempt; another attempt may have changed shared progress since
initialization. Replaying finalization never substitutes newer shared progress.

## Recovery and ownership

Attempts expire after 30 minutes. Abandonment/expiry does not create failure or
change schedules. Keep the creation request body/key, attempt ID and pending submission body/key using existing
identity-safe storage conventions; discard user-specific navigation/state on logout.

| Status | Handling |
| --- | --- |
| 401 | Existing session refresh/login handling |
| 404 | Unknown or foreign attempt/progress; never expose another owner |
| 409 | Fetch current question to reconcile stage/key/content conflicts |
| 410 | Expired attempt; offer a new session |
| 422 | Invalid request; do not retry unchanged malformed input |
| 429 | Attempt event limit; offer a new session |

A retried submission can return its original older-stage response. Fetch `/question`
for current state after replay. Initialized attempts remain pinned; newly installed
policies require a new attempt instead of silently upgrading an old target.

Source of truth: live `/openapi.json`, `backend/app/schemas/srs.py`,
`backend/app/schemas/review_engine.py`, and the [review engine contract](srs-review-engine.md).
