# Phase 4.1A: ChineseLearning SRS v1

Migration `0011_srs_foundation` was applied to local development following explicit
operator authorization. Preservation and schema checks passed; see the
[deployment record](runbooks/srs-0011-deployment-20261026.md). Historical 0010 audit
observations below describe the pre-deployment baseline. No Android screens, answer
grader, handwriting recognizer or result-submission endpoint are added. The backend
requires 0011 for the new SRS endpoints and updated wordbook save implementation.

## Vocabulary compatibility audit

The first operation before SRS implementation was a repeatable-read, read-only audit
of the configured development database. The reproducible inventory and individual
affected UUIDs, lexical keys, POS labels and Vietnamese glosses are in
[srs-data-audit.json](srs-data-audit.json). Run from `backend/`:

```powershell
.venv\Scripts\python -m scripts.audit_srs --output ..\docs\srs-data-audit.json
```

The observed database is `chinese_learning`, PostgreSQL at `127.0.0.1:5432`, role
`postgres`, revision `0010_local_codex_review`. It has **2,810**, rather than the
request's earlier 2,488 entries: 2,804 LOCAL_CODEX_REVIEWED and six NEEDS_REVIEW
editorial holds. The configured development opt-in makes 2,804 visible. No hold,
review evidence, content version, gloss or pronunciation was changed.

| Audit observation | Compatibility decision |
| --- | --- |
| UUID identity plus unique `(simplified, pinyin_numbered)` and `lexical_key` | Schedule by existing saved UUID / catalog UUID, never by Chinese form alone. |
| `谁|shei2` and `谁|shui2` are separate held identities | Preserve both. Never merge progress or infer that one reading passes the other's target. |
| Zero structural identity, Simplified-form, syllable-count or Pinyin-pair defects detected | Existing strict authoring validation is compatible; it does not prove every lexical reading is linguistically correct. |
| All entries have Vietnamese meanings and nonempty POS labels | No missing-field exclusions are needed for this snapshot. Null POS remains legal in the model and must be handled safely. |
| 2,181 entries have multiple Vietnamese glosses | Gloss position is not a verified semantic sense ID. Require editorial sense selection and supported answer sets. Multiple glosses may also be synonyms, not distinct senses. |
| 816 entries share an exact normalized Vietnamese gloss with another identity | Bare Vietnamese-to-Hanzi grading can reject valid synonyms. Disable that unqualified exercise until context or a reviewed acceptance set disambiguates it. |
| 214 entries have compound POS labels | Do not compare against the entire raw label as one correct answer; map supported sense to accepted POS labels or skip POS with an explicit reason. |
| POS labels include `word element`, `locality`, `time`, `idiom` and `phrase` | These are not one consistent beginner POS taxonomy. Even a single label needs reviewed UI/category mapping. |

For example, `口|kou3` has `noun; classifier` and glosses for a mouth and a family
member classifier. A mouth prompt must not require the classifier POS. `中|zhong1`
has `noun; locality`: do not infer sense/POS from the order of those labels.
`什么|shen2 me5` has two Vietnamese glosses but remains held; availability must be
checked independently of linguistic completeness.

The audit flags structural ambiguity candidates; it is not a semantic review of
every translation. Shared gloss detection is deliberately conservative and includes
held records. A missing flag does not authorize grading. No linguistic data was
invented, rewritten or automatically approved.

Existing storage and integration points:

* `curated_user_vocabulary` already owns the unique user/catalog identity, mastery,
  nullable due time, last-review time, save time and soft removal flag. This is the
  canonical progress record, extended in place; learning level remains catalog metadata.
* `curated_vocabulary_reviews` is reserved, currently empty, and requires final
  submitted answers. It cannot represent an initialized attempt without fabricated
  answers. It is retained unchanged; the new attempt lifecycle uses one new table.
  Phase 4.1B should use the new lifecycle rather than introduce a second scheduler.
* Legacy `user_vocabulary` / `srs_states` use different catalog identities and an
  unspecified algorithm JSON. `personal_vocabulary_entries` uses dictionary identities.
  These are preserved without guessing identity or migrating algorithm state.
* `LessonVocabulary` and published CONTENT_PREVIEW bundles reference the legacy
  content namespace. Preview checkpoints are not proof of learning or TEACHES
  provenance. No roadmap completion can change SRS in this phase. A future roadmap
  needs an explicit catalog UUID mapping and the same save/attempt services.
* `visible()` is reused unchanged: HUMAN_APPROVED, or matching AI evidence with its
  opt-in, or matching LOCAL_CODEX_REVIEWED evidence in development with its opt-in,
  always with Vietnamese text. Six holds remain unavailable for new sessions.

Every valid saved word remains in the collection and due counts even if exercise
policy is incomplete. Held/unpublished active words are counted separately as
suspended. All initialized sessions currently report grading unavailable, so none
can penalize a learner while answer policies are unresolved.

## Formal state machine

`phase_step` is zero-based: LEARNING A/B/C = 0/1/2; RELEARNING 1/2 = 0/1.
REVIEW always uses step 0. `level_progress` is 0 or 1 only in REVIEW at mastery
1–4; it is zero elsewhere. The pure implementation is
`app/services/srs_state.py`; the database enforces valid state combinations.

All rows below assume one server-authorized, due attempt. Intervals start at the
actual server completion time, with UTC-aware injectable time.

| Before | Outcome | After | Next interval |
| --- | --- | --- | --- |
| New save | — | mastery 0, LEARNING A, progress 0 | Immediately due |
| LEARNING A | PASS | LEARNING B, mastery 0 | 10 minutes |
| LEARNING B | PASS | LEARNING C, mastery 0 | 1 day |
| LEARNING C | PASS | REVIEW, mastery 1, progress 0 | 1 day |
| Any LEARNING step | FAIL | LEARNING A, mastery 0, progress 0 | 10 minutes |
| REVIEW mastery 1–4, progress 0 | PASS | Same mastery, progress 1 | Current mastery interval |
| REVIEW mastery 1–4, progress 1 | PASS | Mastery +1, progress 0 | Resulting mastery interval |
| REVIEW mastery 5 | PASS | Mastery 5, progress 0 | 21 days |
| REVIEW or RELEARNING | FAIL | Mastery −1; RELEARNING 1 if >0, else LEARNING A; progress 0 | 10 minutes |
| RELEARNING 1 | PASS | RELEARNING 2, same mastery | 1 day |
| RELEARNING 2 | PASS | REVIEW, same mastery, progress 0 | Current mastery interval |
| Early or stale attempt | Either | Scheduling state unchanged; practice counter only | Unchanged |
| Missed deadline without an attempt | — | Unchanged, still due | Unchanged |

Intervals for mastery 1/2/3/4/5 are exactly 1/2/4/7/21 days. No ease, fuzz,
difficulty multiplier or automatic lapse job exists. Relearning successes never
count toward promotion.

## Atomicity, history and lifecycle

Initialization locks the saved row, checks publication, pins the target policy and
records DUE or PRACTICE from server time. A practice attempt never becomes eligible
merely because it finishes after the deadline. Multiple attempts can exist, but
there is only one schedule, in the existing unique saved record.

Completion is an internal service boundary accepting `ValidatedReview`, never an
HTTP boolean. It locks saved progress then the attempt, verifies ownership and the
current publication/version/checksum, derives PASS from complete ordered first-stage
evidence, and commits history and progress together. First errors, hints or reveals
produce FAIL, including an ordered prefix that already proves failure. A clean
incomplete prefix or stage disorder is rejected without a scheduling penalty.

The pinned `schedule_version` permits at most one advancement of each due generation.
A second concurrent attempt is retained as practice, including a failed stale attempt.
Replay of an identical completed attempt returns its original result; conflicting
evidence receives 409. Due counters and failures count only applied schedules.
Practice does not update mastery, level progress, due time or last due-review time.

Duplicate active saves preserve all progress. Removal is soft and increments the
schedule generation; re-save reactivates the same UUID and schedule, also invalidating
old eligibility. An old unfinished attempt after re-save can only count as practice.
Inactive/held words cannot initialize or complete new exercises. Historical completed
attempts remain readable internally and replayable even if publication changes.

`srs_review_attempts` stores pinned target, initialized state, final state, outcome,
ordered typed stage evidence, evaluator version, whether scheduling applied and UTC
timestamps. Completed records and pinned initialization fields are immutable through
a PostgreSQL trigger; deletion is refused. This also prevents hard account deletion
through saved records with history until an explicit retention/erasure policy exists.
No new stage-result table is needed for immutable final evidence in this phase.

## API contracts

Bearer authorization is required for every endpoint; ownership comes from the
authenticated session. Responses use `Cache-Control: no-store`.

| Method | `/api/v1` path | Response |
| --- | --- | --- |
| GET | `/me/srs/dashboard` | `as_of`, available/due/suspended counts, `grading_available: false` |
| GET | `/me/srs/due?limit=50` | At most 100 progress items ordered by due time then saved UUID |
| GET | `/me/srs/progress/{saved_id}` | Owned progress, counters, schedule generation, active/available flags; inactive history remains accessible |
| POST | `/me/srs/sessions` | `{ "saved_id": "<owned-saved-uuid>" }`; 201 pinned initialization contract |

Foreign or unknown saved UUIDs return 404. A held target at initialization returns
409. Extra request fields, including `correct`, `user_id` or `result`, return 422.
There is no graded submission endpoint. Due queries are bounded queue snapshots,
not a paginated export: after successful future reviews, query the first batch again.
Until grading exists, subsequent queue requests may return the same due words.

Example progress item:

```json
{
  "saved_id": "00000000-0000-0000-0000-000000000001",
  "vocabulary_id": "00000000-0000-0000-0000-000000000002",
  "mastery_level": 0, "phase": "LEARNING", "phase_step": 0,
  "level_progress": 0, "next_review_at": "2026-10-26T00:00:00Z",
  "last_reviewed_at": null, "is_active": true, "schedule_version": 0,
  "due_review_count": 0, "failure_count": 0, "practice_count": 0
}
```

Example initialized session (illustrative UUIDs/time):

```json
{
  "attempt_id": "00000000-0000-0000-0000-000000000003",
  "saved_id": "00000000-0000-0000-0000-000000000001",
  "mode": "DUE", "started_at": "2026-10-26T00:00:00Z",
  "grading_available": false, "applicable_stages": ["HANZI", "PINYIN"],
  "disabled_stages": {"POS": "POS_REQUIRES_REVIEWED_SENSE_POLICY"},
  "reason": "SERVER_GRADING_NOT_IMPLEMENTED", "content_version": 1
}
```

Accepted answers and editorial policy internals are not exposed in this response.

## Migration and preservation

`0011_srs_foundation` adds phase, step, promotion progress, generation and three
counters to the existing curated saved table, plus a nullable JSONB legacy snapshot.
It makes due time non-null with a server `now()` default for new saves and adds
state/counter checks. The one new attempt table has a history index and immutability
trigger/function. Existing identity uniqueness and owner/due index are reused.
Historical migration files are unchanged. Downgrade deliberately refuses history loss.

For every existing curated saved row, the original mastery, due time (including null)
and last-review time are captured in `legacy_srs_snapshot`. Non-null due and last-review
times and mastery are unchanged. Mastery 0 starts LEARNING A; mastery >0 starts REVIEW
with promotion progress 0. Unknown historical successes are never inferred. Only a
null due time becomes `saved_at`, making an unscheduled saved word due without adding
another schedule. Active status and every other original value are preserved.

The development audit projects **one** backfilled row: mastery 0, null due time;
three users and one lesson run remain. Legacy personal wordbook, user-vocabulary,
legacy SRS and review-history counts are zero, and their tables are not changed.
See [verification](srs-verification.md) for executed isolated rehearsals and limitations.

## Phase 4.1B integration and remaining decisions

1. Implement `TargetResolver` using reviewed sense-specific `ReviewTarget` policies:
   catalog UUID, lexical key, version/checksum, policy version, version-scoped sense
   key, Vietnamese prompt, accepted Simplified/Pinyin/POS sets and explicit skipped
   stage reasons. No policy is synthesized from raw POS delimiters or gloss order.
2. Persist and authorize stage submissions in HANZI → PINYIN → optional POS order.
   First submission correctness is permanent. An ordered failing prefix can finalize
   FAIL immediately; subsequent stages may continue as separate practice evidence
   without modifying the immutable scheduling outcome. A clean abandoned prefix has
   no completed outcome. Record hints/reveals at the time they occur. Do not let clients set verdicts,
   eligibility, completion time, policy, or schedule generation.
3. Implement `ReviewEvaluator` against those persisted submissions and pinned answer
   policy. Construct `ValidatedReview` internally and call `complete_validated` with
   no existing transaction. A crash before commit must leave both history and schedule
   unchanged. Re-evaluation/replay must use the same evaluator policy and evidence.
4. Specify normalization: Chinese whitespace/punctuation, Pinyin tone numbers versus
   marks, ü/u:/v, neutral tones, apostrophes, citation versus sandhi, and POS synonyms.
   Do not add alternative lexical readings without explicit editorial evidence.
5. Missing trustworthy POS means an explicitly skipped stage, never FAIL. Ambiguous
   Hanzi prompts need a sense/context-qualified prompt and reviewed acceptance set;
   otherwise suspend that exercise while retaining the saved vocabulary/progress.
6. Before enabling grading, define session expiry/abandonment and stage-submission
   idempotency/rate limits. Current initialized sessions cannot be graded and may be
   retained for inspection. There is no automatic cleanup or hidden expiration rule.

The approved scheduling rules are consistent. They leave phase-step numbering,
historical partial success, removal/re-save and stale concurrent attempts unspecified.
This implementation uses the conservative rules documented above: zero-based steps,
no invented partial success, resume saved progress, and stale attempts as practice.
Semantic sense IDs and a consistent POS taxonomy remain editorial decisions for 4.1B.
The suggested minimal solution is version-scoped reviewed policies, without changing
catalog identities or requiring a new global linguistic schema in 4.1A.
