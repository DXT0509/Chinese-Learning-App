# MVP SRS and aggregate mastery requirements

Status: **finalized product rules, design only**, 2026-10-18. No scheduling algorithm,
evaluator, endpoint, migration or Android behavior is implemented here. See
[database](database-design.md), [engine](learning-engine-design.md),
[examples](lesson-examples.md) and [implementation slices](mvp-implementation-plan.md).
This is a configurable initial interval strategy, not FSRS, SM-2 or scientifically
validated measurement of memory or pronunciation.

Slice 1 content authoring leaves users, user_vocabulary, progress and srs_states unchanged.
Unversioned legacy lesson membership is never inferred to be TEACHES evidence. A published
CONTENT_PREVIEW is an editorial artifact and cannot enroll, grade or complete learning.

## 1. Separate accomplishments, membership and mastery

| Concept | Evidence | SRS effect |
| --- | --- | --- |
| Save a catalog/custom word | user_vocabulary | None; not proof of app learning |
| First study | learned_at plus appropriate study evidence | No mastery increase |
| Complete a teaching lesson | First valid completion run/version and TEACHES relations | Once-only EXP and eligible app knowledge; proposed initial enrollment at mastery 0 |
| Complete a roadmap REVIEW lesson | Its own completion record | No automatic mastery change |
| Complete a valid due SRS review | Required task results and one accepted review_history event | One aggregate PASS/FAIL transition |
| Early practice or lesson replay | Practice/run evidence | No mastery, schedule, streak or review_count change |

The MVP keeps one personal mastery level, integer 0..5, per user_vocabulary entry.
No score belongs on shared vocabulary. At most one srs_states row exists per personal
entry; absence means not enrolled. Suggested initial enrollment is after a first accepted
TEACHES completion, level 0 with a policy-calculated initial due time. Saving alone does
not enroll. Whether custom cards enroll remains open; they never count as in-app learned
vocabulary for restricted translation. Learned phrases do not automatically grant subwords.

Future skill-specific mastery would introduce explicit listening/speaking/writing/recognition
card identities, migration and task policies. Do not average imaginary skill scores now
or duplicate state for each scene. Aggregate mastery describes the pinned assessment profile,
not competence in all skills.

## 2. A review is a pinned set of required tasks

At server-authorized start, authenticate the owner, check enrollment, pin the due instant,
state revision, immutable scheduling policy, vocabulary target and nonempty required task
set. Persist one review_attempts row and one review_tasks row per task. Examples of task
types are MEANING_RECALL, PINYIN_RECALL, HANDWRITING_RECALL, SPEAKING and LISTENING_RECALL.
Task type is distinct from scene type: several scene pages can collect evidence for one task.

The launch task profile must explicitly name its required task keys, evaluation policy
IDs, targets, retry limits and hint rules. Example runnable profile: meaning and Pinyin
recall using deterministic text policies, plus SPEAKING using STT_CONTENT_MATCH when that
integration has passed its delivery gate. A supported profile with handwriting assessment
may require that task too. Canvas drawing and manual character selection alone do not
prove handwriting shape correctness; until an appropriate evaluator or an explicitly
approved self-assessment policy exists, handwriting is practice and no profile that requires
unsupported automated handwriting assessment may launch. Do not fabricate its PASS.

Speaking is a required learning activity. A pre-approved accessible review profile can
replace a speech task with a named supported alternative before starting the attempt;
store the chosen profile/version and exact task set. It does not claim a speaking result.
The default profile cannot silently drop speaking because a provider is temporarily down.
If support is unavailable before start, defer the review or offer an already approved
alternative profile. If it fails during the review, retain the same blocked attempt.

Each task has one finalized result PASS or FAIL; PENDING and BLOCKED are ungraded states.
The aggregate is:

- PASS iff **every required task** has a valid finalized PASS.
- FAIL iff every required task has a valid finalized PASS/FAIL and at least one is FAIL.
- Otherwise not gradable: aggregate_result remains NULL and state/mastery do not change.

Even when one task already failed, do not finalize a failed aggregate while another
required task is blocked by permission/network/service problems. All required assessments
must be complete and valid. Optional task results do not affect the aggregate.

## 3. Finalized mastery transitions

| Accepted complete due review | Mastery after | Streak | Scheduling |
| --- | --- | --- | --- |
| PASS | min(5, mastery_before + 1) | consecutive_successes + 1 | Versioned success interval |
| FAIL | max(0, mastery_before - 1) | Reset 0 | Shorter relearning interval |
| Pending/technical blocker/permission denial | Unchanged | Unchanged | Unchanged; recover same attempt |
| Early practice, stale revision, lesson replay | Unchanged | Unchanged | Practice only; no graded history |

PASS/FAIL replaces the previous AGAIN/HARD/GOOD/EASY proposal. Hints and retries no longer
create intermediate mastery transitions or a HARD hold level. Instead the task's published
policy determines its final valid PASS/FAIL. Proposed teaching/review retry policy:
a correct unassisted response within the finite scored retry allowance can pass; exhausted
valid wrong responses or an answer-revealing hint finalize FAIL. Technical errors do not
consume scored retries. Non-revealing hints must be explicitly allowed; repeated incorrect
responses remain in evidence and cannot be hidden by uploading only the last answer.
Exact task retry/hint limits need product review, not a new mastery transition rule.

A task finalizes once for that review; retries within its allowance are assessment_attempts
under the same review_attempt_id/task_key. After finalization, extra practice cannot rewrite
its result or create another grade against the same state revision. At level 0, failure
stays 0; at level 5, success stays 5, but each accepted review still records an event,
increments count/revision and sets a new due time. First study/capture does not increment mastery.

## 4. Speaking modes and valid evidence

PronunciationEvaluator is provider independent; its design contract is in the engine.
Speaking requires microphone permission, a valid recording and a supported evaluation result.
STT_CONTENT_MATCH recognizes Mandarin and compares final recognized Chinese text with the
pinned expected/accepted text under an explicit normalization policy. It returns PASS/FAIL
for content recognition only. It provides no pronunciation percentage, tone accuracy, phoneme,
aspiration or retroflex assessment. A matching transcript may still conceal pronunciation
errors; a nonmatch may reflect recognition limitations and should be explained as such.

Future PRONUNCIATION_ASSESSMENT uses an immutable evaluation policy with a configurable
passing threshold, initially **70/100** on an explicitly named supported score. Score >=70
passes that threshold; below it fails only after a valid assessment. Missing required score,
unsupported Mandarin metric or provider failure is not a valid FAIL. No 70/100 threshold
applies to STT matching, and STT recognition confidence must not be substituted for it.

Store evaluation policy ID/mode/version, actual adapter/provider/model version when available,
input revision, recognized text where appropriate, valid status/error code, and timestamps
on assessment_attempts. Preserve per-task finalization evidence on review_tasks and aggregate
outcome/mastery/scheduling policy on review_attempts/history. An error result stores no
learning failure. A missing provider model version is explicitly unknown, never invented.

Microphone denial, timeout, rate limit, provider outage, corrupt/empty recording, cancellation
and unsupported evaluation are recovery reasons. Keep progress and offer retry or permission
settings. The default response is neither a failure grade nor an automatic success. A valid
recording that produces a successfully processed nonmatching transcript can be a content
FAIL; no usable speech/input is an input-retry state rather than a pronunciation judgment.

Raw voice is ephemeral by default: authenticated processing only, remove temporary audio
on completion/error/cancellation, bound orphan retention with TTL cleanup, and verify the
provider retention configuration. No raw audio in PostgreSQL, public assets, logs or backups.
Derived transcripts/results have a separate bounded, account-scoped retention policy.
Do not keep audio indefinitely to make a blocked review resumable; allow fresh capture
while retaining already accepted task results.

## 5. Configurable scheduling

srs_policies.algorithm_version identifies an immutable algorithm/parameter/task-profile
version. State, attempts and history reference its policy_id. The policy pins evaluation
policy versions for each task; task-level actual policy IDs are persisted as well. Changing
thresholds, task set, retry rules, intervals or difficulty mapping creates a new version,
never retroactively changes old attempts. Evaluation mode switches cannot silently happen
inside an open review.

Illustrative parameters, **not approved interval durations**:

```json
{
  "algorithm_version": "aggregate-pass-fail-proposal-v2",
  "parameters": {
    "schema_version": 1,
    "base_interval_seconds": [600, 86400, 259200, 604800, 1209600, 2592000],
    "difficulty_factors": {
      "INTRODUCTORY": 1.0,
      "STANDARD": 0.85,
      "CHALLENGING": 0.7,
      "UNCLASSIFIED": 0.85
    },
    "minimum_interval_seconds": 300,
    "maximum_interval_seconds": 5184000,
    "fail_relearn_seconds": 300,
    "early_reviews_change_state": false,
    "required_task_profile": "meaning-pinyin-speaking-v1"
  }
}
```

An actual policy must also resolve the profile to supported task/evaluation policies and
map `(hsk_standard_id, level_id)` to difficulty bands. Unclassified/custom uses a documented
default. HSK difficulty factors are initial heuristics, not validated individual difficulty.
Store the chosen factor on history; future HSK edits must not rewrite past results.

For PASS:

`interval = clamp(base_interval[mastery_after] * difficulty_factor, min_interval, max_interval)`

For FAIL:

`interval = max(min_interval, min(fail_relearn_seconds * difficulty_factor, success_interval_at_mastery_after / 2))`

Validate policy parameters so the failure interval is strictly shorter than the success
interval at every level/difficulty combination; the minimum clamp must not defeat this
invariant. This ensures high-mastery failures relearn promptly rather than waiting weeks.
Initial enrollment uses the level-0 success delay, not a fabricated review. Policy rules
can evolve but must preserve the finalized +1/-1 transitions unless product rules change.

`next_review_at = server_accepted_at + interval`. Server calculates the schedule; never
accept a client-selected due instant or mastery. Use timestamptz and aware UTC values.
Intervals are durations, independent of local midnight/DST. Lateness grants no extra level
advance; the next interval starts at acceptance. A floor/ceiling result is still auditable.

## 6. Transaction, idempotency and history

1. Resolve the user-scoped operation UUID and payload hash before stale checks. A transport
   retry returns its recorded result; mismatched payload reuse is a conflict. Review start,
   assessment submission and aggregate grading have separate operation identities.
2. Lock the state, parent review attempt, then task rows in stable task-key order. Every
   evaluation/task/card/run must belong to this user/target/pinned policy. External STT calls
   run outside DB transactions; their result is persisted against the exact input revision.
3. A scene retry creates another assessment_attempt in the same review/task. Replaying a
   transport response or late provider callback does not create another scored retry.
   Technical outcomes keep tasks BLOCKED/PENDING. On recovery, retained valid task results
   remain intact, subject to policy attempt expiry and unchanged state revision.
4. Grade only if all required tasks finalized, the attempt began due according to the
   server, state revision is unchanged, and policy/evidence/expiry are valid. An early
   started attempt remains PRACTICE even if submitted after the due instant. Client wall
   time cannot prove delayed recall. A stale/expired review does not become a FAIL.
5. Compute aggregate, mastery_after and schedule once. Atomically insert one review_history,
   update state/count/streak/revision, set submitted_at and aggregate_result on the parent,
   and commit. No history row or state change occurs for technical blockers or practice.
6. UQ(attempt_id), UQ(user_id,operation_id) and UQ(user_vocabulary_id,revision_after) prevent
   duplicate grading. Two device attempts against one revision can produce only one accepted
   event; the loser stays stale/practice, never replays against the newer state. Rollback
   leaves state/history/aggregate consistent. Use bounded deadlock retries with the same UUID.

History records outcome PASS/FAIL, mastery before/after, prior/new due, accepted timestamp,
policy FK, difficulty factor, revision before/after and idempotent identity. Its attempt FK
retains the required task list, per-task results and evaluation versions; no raw audio is
needed. review_count counts accepted aggregate reviews, not task responses. consecutive_successes
counts accepted aggregate passes. failed_attempts is per-task evidence, not a separate lifetime
schedule counter. Versioned algorithm_state contains no duplicate typed timestamps/mastery.

Never hold a DB lock during network evaluation or store provider exception payloads in logs.
Late results for replaced/cancelled recordings cannot change the selected task evidence.
Immutability of finalized evidence/aggregate is an authorized service-write invariant.

## 7. Roadmap, offline, upgrades and anti-farming

Roadmap review completion and SRS remain independent: one node can complete for teaching
while its due review fails, stays blocked or is practice only. Only an explicitly pinned
multi-task SRS review may change mastery. Passing one scene or all lesson pages does not
implicitly invoke SRS. Lesson replay/early practice has no state/schedule effect, even
for early wrong answers. No review-grade EXP is awarded; lesson EXP remains once per ID.

Initial graded speaking reviews can require online evaluation. Offline work is provisional;
without a supported evaluator a required speaking task remains blocked. Later reconciliation
needs identity-scoped outbox, durable receipts, payload hashes, attempt leases/expiry and
server ordering. Deduplicate first; accept only against unchanged pinned revision and
valid due/evidence semantics, or retain the event as practice with a visible reason.
A signed snapshot alone cannot prove the actual time of offline recall. Do not grade a
stale offline failure against a later successful state. Never upload another account's work.

Policy upgrades are explicit, locked transitions; proposed default preserves existing due
times until the next accepted review. Historical policies/modes remain queryable. Unknown
legacy schedules stay read-only pending reviewed mapping. Existing counts without history
need a documented migration baseline, never invented outcomes or task evidence. The earlier
four-rating proposal was never implemented; if an external deployment has such ratings,
preserve them and design a versioned import rather than relabeling them as measured PASS/FAIL.

## 8. Acceptance criteria for the SRS slice

Test +1/-1 bounds for 0..5; all-pass vs one-fail; an empty required set rejected;
a failed task plus a blocked task remains ungraded; permission/input/service errors
preserve state and retry budget; recovery preserves successful tasks; correct-after-retry
and hints follow pinned policy; assessment/aggregate idempotency; provider callback races;
one aggregate event across scene retries; due boundary/early-start-late-submit;
concurrent device winner; stale/expired review; failed high-level short relearning;
policy/mode/70-threshold versioning; STT score always NULL; rollback; owner isolation;
UTC/DST; raw-audio cleanup including crash TTL; and legacy upgrade without loss.

These are future implementation checks. This documentation update runs none of the SRS
behavior, database migration or device tests.
