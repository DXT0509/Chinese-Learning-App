# ChineseLearning SRS v2 — implementation and deployment preview

Updated 31 October 2026 (Vietnam/Bangkok time). **Deployed to local development**
at 0014 with FSRS 6.3.2 as the sole scheduler. The rollout flag and v1 interval
algorithm have been removed. See the [deployment report](runbooks/srs-fsrs-only-deployment.md).

The [inspection plan](srs-v2-plan.md) was recorded before scheduler changes.

## Scheduler and mastery

The backend pins [`fsrs==6.3.2`](https://pypi.org/project/fsrs/6.3.2/), maintained by
[Open Spaced Repetition](https://github.com/open-spaced-repetition/py-fsrs).
The installed signatures and dictionary round trips were inspected. Python 3.14
is the tested local environment; the package supports the project's Python >=3.12
constraint. Dependencies are constrained in pyproject and captured in the lock.

The adapter uses upstream FSRS, with desired retention 0.90, upstream weights,
learning steps 1/10 minutes, relearning 10 minutes and the upstream 36,500-day
maximum interval. Fuzzing is disabled for reproducible replay; session presentation
is randomized independently. PASS maps only to Good (3), FAIL only to Again (1).
No Hard/Easy ratings are inferred. `configuration(retention)` permits a different
retention; each memory row and applied attempt pins the complete configuration.
No optimizer is enabled: binary history contains no Hard/Easy examples and does
not support claims of calibrated personal parameters. Future optimization needs
enough representative history, held-out evaluation and separately reviewed rollout.

`srs_memory` stores the upstream card's difficulty, stability, FSRS state/step,
last_review and due, plus scheduler version and parameters. Retrievability is
calculated by the library at selection time, never persisted as a stale constant.
Saved-word `next_review_at` is the authoritative query index and receives the
same due value on eligible completion, in the same transaction.

`review_mastery.advance_mastery` owns progress only and never calculates a due
timestamp. Existing levels 0–5 and their learning/relearning/two-success promotion
rules remain; a failure subtracts one with floor zero. The old phase fields remain
valid progress bookkeeping. FSRS Learning/Review/Relearning are a separate upstream
memory state and may differ from the progress phase. The v1 scheduling function
has been deleted; historical records remain readable without executing that algorithm.

Migration 0014 initializes every existing save's memory using only completed,
scheduling-applied recorded outcomes, ordered by timestamp then UUID, and retains
the existing due timestamp. No recorded history means an unreviewed FSRS card,
regardless of mastery. No missing reviews are invented. New saved words initialize
their memory on the first eligible completion. Subsequent reviews use stored memory.
Early/stale practice attempts remain
audited but cannot advance memory or mastery. State-after includes previous/next
FSRS cards, upstream review log, scheduler version and full parameters.

## Two stages and physical handwriting

Every new gradeable v2 attempt projects a validated editorial policy into
`handwriting-pinyin-v2`, format 2, exactly HANZI then PINYIN. The source version and
snapshot SHA-256 retain provenance. The obsolete POS instruction is removed from
the prompt. The [generated bundle](datasets/srs-v2-two-stage-policies.json) contains
2,804 validated projections, zero unavailable identities, and was **not installed**.
Existing policy rows and dictionary POS metadata are untouched.

Hanzi submission requires `handwriting` containing recognizer
`MLKIT_DIGITAL_INK_ZH_HANS_V1` and one character record per server-defined slot.
Each record supplies bounded moving strokes with finite coordinates and monotonic
timestamps, recognition candidates, and an explicitly selected candidate. The
answer must equal the concatenation of those selections. Limits: 64 slots,
64 strokes/slot, 128 points/stroke, 6,000 total points and 20 candidates/slot.
Empty, stationary, malformed or mismatching evidence is rejected without grading.

Android uses the existing independent ink ViewModel and ML Kit adapter, with no
Hanzi keyboard input or Pinyin-to-Hanzi conversion. Candidates are requested only
after strokes, no hidden target enters recognition, and selection never submits
automatically. Undo/rewrite invalidate the affected transcription. Re-recognition
retains a prior explicit selection from the same unchanged strokes. Missing slot
metadata blocks submission. Model/download/recognition failures offer retry and
do not create a FAIL. Stroke order and confidence are not grading signals.

**Trust limit:** server shape/geometry/membership validation rejects a mere
`handwriting=true` assertion, but cannot attest that arbitrary client-supplied
coordinates and candidate lists originated on physical hardware or in ML Kit.
Defending against a modified client requires a trusted recognition/attestation
service; this implementation must not be described as tamper-proof handwriting.

The first valid answer to each stage is definitive. Both correct and unaided is
PASS; either incorrect or assisted is FAIL; missing answers cannot finalize.
Retries retain keys and sealed results. Before both answers are submitted, no
solution Hanzi or pronunciation appears in questions, draft questions, feedback,
or reveal responses. Learners can continue after an incorrect Hanzi answer.
After both answers, selectors expose corrective feedback before finalization.

Legacy attempts and POS submissions retain their original pinned JSON. Completed
attempts remain readable. Unfinished legacy attempts are read-only;
Android identifies the wire version, offers abandonment/restart, and never turns
an old draft into a new PASS. No historical payload is rewritten.

## Daily planner, intake and timing

Authenticated `POST /api/v1/me/srs/daily-plans` takes a UUID request key and optional
`continue_beyond_target`. User-row locking serializes reservations across devices.
Plans persist selected identities and randomized order, completed identities,
deferred identities, intake reservations, day/timezone and the 1,200-second target.
An unfinished plan is recovered before creating another. Repeated requests and
duplicate word completion never consume additional slots. Deferral preserves the
saved word, original due date, history and mastery.

Selection sorts overdue review words by increasing upstream retrievability,
then due review words, due Learning/Relearning, then pending saves. Unknown memory
uses conservative priority zero within its group. Ties use due/saved timestamp,
then UUID. Only the selected set is shuffled; the stored shuffle survives recovery.
Capacity is floor(remaining seconds / estimated seconds per word), at most 50.
The cold-start estimate is 45 seconds; after five completed timed attempts, use
the latest 100 completed samples' mean, bounded to 10–180 seconds. Backlog estimates
use all visible due words and unreviewed saves, including words lacking a currently gradeable
policy; they are not silently treated as completed.

Existing saves receive `learning_activated=true` through the additive default.
Future saves default false: saved and available in the dictionary, mastery zero,
and immediately due for their first review. Due counts and the due endpoint include
these saves; pending counts are the unreviewed subset of due work, not an additional
queue. There is no daily cap on new-word admission. Existing due work retains its
selection priority and plans retain their time budget and 50-word size limit.
Prefetch/initialization does not activate saves or change a schedule. Activation
occurs on the first eligible completed attempt.

Android retains a plan request key only while recovering a request or working
through its queue. An empty response clears the key, refreshes counts and displays
an explanation; a subsequent start uses a fresh key so newly saved words can enter.
Dashboard refresh also clears a restored empty/completed key without discarding an
unfinished attempt. Server replay of the same plan key remains idempotent.

The UI shows two selectors, daily minutes, due backlog, estimated minutes and
pending saves. Reaching the target never interrupts the current word; completing
it offers `Tiếp tục ôn`. The budget is a target, not guaranteed full coverage.

`POST .../sessions/{attempt_id}/active-time` accepts absolute cumulative milliseconds.
Saved/attempt locks and monotonic receipts make retries idempotent. Server wall-clock
windows cap receipts; per-date JSON buckets preserve midnight accounting even when
a previous day's plan is resumed. Client timing runs only while RESUMED, excludes
review network windows and measured model/download/recognition waits, and stops
after 30 seconds without interaction. Five-second sampling can undercount partial
windows; it is an estimate, not an exact stopwatch. Process death can lose the final
unacknowledged window. Timing errors do not grade an answer or change a schedule.

## Verification and simulations

See [readiness](runbooks/srs-v2-readiness.md) for final commands/results and limitations.
The planner sorts the owner's eligible population once per plan (O(N log N));
it does not page/reload the catalog at each word. Existing prefetch, first-answer,
creation replay, cancellation and saved-state regression checks are retained.
No emulator/device execution or production latency benchmark is claimed.

[Simulation artifact](srs-v2-simulation.json): synthetic 365-day mature cohorts,
three invented prior Good reviews explicitly labeled as synthetic, 90% fixed
binary success, due dates spread over 21 days, 45 seconds/word, one opportunity
per word per day, no new arrivals. These histories never enter a learner database.

| Saved words | v1 mean minutes/day, final 90 days | FSRS 20-minute planner | Peak deferred words |
| --- | ---: | ---: | ---: |
| 500 | 26.41 | 2.65 | 27 |
| 2,000 | 109.05 | 10.13 | 1,548 |
| 5,000 | 272.94 | 18.84 | 4,547 |

These are modeled workload figures, **not measured learning or retention outcomes**.
Fixed success despite deferral is optimistic; it does not model additional forgetting,
real handwriting duration, ongoing intake or the full within-day short-term queue.
The uncapped FSRS comparator is included in the artifact. Large transition backlogs
remain possible even without moving any due date. Do not promise 90% observed recall
or completion of all due work within 20 minutes from these simulations.
