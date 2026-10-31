# Phase 4.1A verification — 2026-10-26

No development migration, backfill, reset, truncation or catalog edit was executed.
No Android code changed; no emulator/device or Android build validation is claimed.
No dependencies changed.

## Executed checks

| Check | Result |
| --- | --- |
| Initial pure state-machine/contract tests | 19 passed |
| Initial focused SRS run with PostgreSQL, concurrency and fresh migration rehearsal | 24 passed |
| Full backend suite with isolated PostgreSQL and fresh legacy migration rehearsal | 242 passed, nine optional database checks skipped |
| Final full backend suite, including updated typed target/prefix-failure contract, fresh SRS rehearsal and real connection concurrency | **244 passed, eight optional database checks skipped**, 55.03 seconds |
| `ruff check .` | Passed |
| `ruff format --check .` | Passed (123 files) |
| `git diff --check` | Passed |
| `alembic check` during SRS and legacy rehearsals | Passed; no metadata drift |
| Historical migration diff | No changes to 0001–0010 |
| Post-implementation read-only development audit | Revision/count/hold/personal-data-count comparison passed; still 0010 |

The final suite used `TEST_DATABASE_URL`, `SRS_MIGRATION_TEST_DATABASE_URL` and
`SRS_CONCURRENCY_TEST_DATABASE_URL`. The earlier full run used the separate
`MIGRATION_TEST_DATABASE_URL` and passed the original nonempty legacy preservation
test. Other optional dedicated migration database variables were not provided;
those eight checks were skipped, not represented as completed rehearsals.

Two warnings remain from the existing dependency/reflection stack: Starlette's
TestClient/httpx deprecation and SQLAlchemy's reflection `dialect_options` warning.
They did not prevent the PostgreSQL preservation tests or metadata checks.

An exploratory full run initially found an old fixture that set mastery 4 while
leaving phase LEARNING, plus a publication test that inherited the development
local-review opt-in. The fixtures now set consistent REVIEW state when seeding
existing mastery. Verified full-suite runs explicitly disabled publication opt-ins
globally, with tests opting in individually. No application publication policy was
changed to accommodate tests.

## Isolated databases actually used

All are fresh PostgreSQL databases on the local server, separately created for this
task; credentials were not written into the repository. Fixtures remain for inspection.

* `chinese_srs_test_20261026a`: regular tests, migrated to 0011; fixture transactions roll back.
* `chinese_srs_migration_20261026a`: first nonempty 0010 → 0011 rehearsal.
* `chinese_srs_concurrency_20261026a`: first independent-connection concurrency check.
* `chinese_srs_legacy_upgrade_20261026a`: original 0001 nonempty legacy → head rehearsal.
* `chinese_srs_migration_20261026b`: final nonempty SRS rehearsal after contract review.
* `chinese_srs_concurrency_20261026b`: final concurrent completion/idempotency check.

The SRS rehearsal refuses a database containing any public table. It installs 0010,
seeds one user and six curated saved identities at mastery 0–5, an inactive row,
a held catalog entry, non-null historical times and one null due time, plus a
legacy custom word and legacy algorithm state with review count 17. It snapshots
**every original column of every existing table**, upgrades to head, and compares
all original rows. The only permitted original-column change is a null curated due
time becoming that row's save time; the old null remains in the legacy JSON snapshot.
It checks initial phases/counters and runs `alembic check`. Both runs passed.

The separate original legacy rehearsal seeds representative original content/user
data and verifies old values/references survive upgrade to 0011. It passed as well.
This is synthetic preservation evidence, not a restore of the actual development
database and not a production backup validation.

Concurrency uses separate committed database connections, concurrently completing
two different attempts and replaying one of them. Exactly one due advancement and
one practice result survive; replay adds no third result or counter increment.

Rollback injects an invalid attempt mutation during flush, after in-memory progress
advancement. The transaction rejects it; persisted phase, counters and completion
remain unchanged, and a subsequent valid completion succeeds. PostgreSQL also
rejects mutation and deletion of completed attempt history.

## Behavior coverage

Deterministic UTC tests cover all learning steps and failures, waiting intervals,
two-pass promotion at mastery 1–4, resulting-mastery intervals, mastery 5 maintenance,
failure demotion, relearning passes/failures, return to zero, early practice (including
completion after the deadline), and missed reviews scheduled from completion time.

PostgreSQL and API checks cover identity uniqueness, duplicate saves, removal/re-save,
stale generation handling, replay conflicts, atomic rollback, immutable history,
ownership/401/404, bounded due queue, publication suspension, unavailable grading,
strict request rejection of client correctness fields, and absence of a result writer.
The existing catalog suites also exercise local/AI evidence opt-ins and stale revisions.

Typed contract checks require all applicable stages for PASS; reject clean incomplete
or out-of-order evidence; support immediate FAIL from a proven failing ordered prefix;
disqualify hints; and require explicit skipped-POS reasons and reviewed sense/answer
policies before a target is considered gradeable. Synthetic policies exist only in tests.

The live read-only comparison retained 2,810 catalog entries, 2,804 local approvals,
six holds, three users, one curated saved word and one lesson run at revision 0010.
Legacy personal wordbook, user-vocabulary, SRS, lesson progress and curated learner
review counts remained zero. Count checks do not prove byte-for-byte live data equality;
all-column comparisons were performed on the isolated migration fixtures. No backup
was taken or restored from development during implementation.

Deployment instructions and the exact backup/migration commands are in
[the operator runbook](runbooks/srs-local-deployment.md). Applying 0011 to development
remains an explicit operator action.
