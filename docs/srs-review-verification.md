# Phase 4.1B verification — 2026-10-27

Final executed checks:

| Check | Result |
| --- | --- |
| Full backend suite with isolated PostgreSQL | **292 passed, 8 skipped**, 73.89 seconds |
| `python -m ruff check .` | Passed |
| `python -m ruff format --check .` | Passed, 133 Python files |
| `git diff --check` | Passed; existing line-ending notices only |
| Nonempty 0010 → head SRS preservation rehearsal | Passed, including `alembic check` |
| Nonempty 0011 → 0012 with pending/completed review history | Passed, including all original columns, fingerprints and `alembic check` |
| Independent regular-test database `alembic check` | Passed |
| Independent-connection scheduler and review-engine races | Passed |
| Prepared three-policy bundle against real catalog | Three valid source-bound, three-stage policies; read-only validation |
| Development read-only audit and preservation fingerprint | Still 0011; no writes to development |

The eight skips are optional database checks whose dedicated environment variables
were not provided. They are not represented as successful rehearsals. The suite
includes the existing dictionary, personal vocabulary, authentication, authoring,
publication and scheduler regressions. No dependency constraints or lockfile changed.
Three warnings came from two existing dependency/reflection categories: Starlette's
TestClient/httpx deprecation, and SQLAlchemy reflection `dialect_options` warnings in
the two migration rehearsals. They did not fail validation.

## Isolated databases and test selection

Final suite variables identified separately provisioned local PostgreSQL databases:

| Variable | Database |
| --- | --- |
| `TEST_DATABASE_URL` | `chinese_review_test_20261027a` |
| `SRS_MIGRATION_TEST_DATABASE_URL` | `chinese_review_upgrade_20261027c` |
| `REVIEW_MIGRATION_TEST_DATABASE_URL` | `chinese_review_preservation_20261027b` |
| `SRS_CONCURRENCY_TEST_DATABASE_URL` | `chinese_review_srs_race_20261027c` |
| `REVIEW_CONCURRENCY_TEST_DATABASE_URL` | `chinese_review_concurrency_20261027c` |

Publication opt-ins were explicitly disabled globally for the suite; individual
publication tests opt in where required. Fresh migration databases refused existing
public tables. Fixtures and exploratory databases were retained; nothing was reset,
downgraded or deleted. Credentials were inherited in memory from local configuration
and were not written to tracked files or printed.

Reproduce from `backend/`: provision fresh empty migration databases, migrate only
the regular and concurrency test databases to 0012, set the five URLs above to the
corresponding isolated databases, disable global publication opt-ins, then run:

```powershell
.venv\Scripts\python -m pytest -q --tb=short
.venv\Scripts\python -m ruff check .
.venv\Scripts\python -m ruff format --check .
# Set DATABASE_URL to the isolated regular-test database before this command.
.venv\Scripts\python -m alembic check
```

Never reuse a nonempty migration-rehearsal database. The 0011 history fixture includes
one initialized and one completed attempt and a saved identity; every original column
of every original table is compared after 0012. The fingerprint helper is also
compared before/after upgrade. The only new existing-row field is an empty journal.
This is synthetic preservation evidence, not a development backup restore rehearsal.

## Meaningful behavior coverage

Pure grading tests cover marked/numbered equivalence, numeric syllable boundaries,
explicit apostrophes, NFD/NFC forms, ü/u:/v, neutral 5/unmarked neutral syllables,
wrong/missing tones, incomplete/mixed numbered formats, alternate reading rejection,
Traditional rejection, exact lexical identity, POS set equality, duplicate categories,
measure-word sense selection, stale policy rejection and strict input shapes.

PostgreSQL/HTTP engine tests cover a clean three-stage PASS, individual and multiple
Hanzi/Pinyin/POS failures, preserved first errors after retries, hints, explicit reveals,
no premature answer-key exposure, multiple-category policy behavior, explicit skipped
POS, absent/stale/ungradable policies, shared meanings and multiple meanings reported
without penalties, authenticated ownership/401/404, stage skipping, incomplete
finalization, exact HTTP duplicate responses, conflicting-key 409, expiration, clean
restart/abandonment, early practice crossing its deadline and UTC finalization replay.

An attempt with multiple wrong stages at REVIEW mastery four demotes once to mastery
three/RELEARNING; the abandoned failing prefix produces no progression. Existing pure
scheduler tests retain all UTC learning, relearning, promotion and interval coverage.

Independent committed connections race three identical submissions per stage across
two attempts, followed by concurrent finalizations including duplicate finalization.
Each journal contains exactly three first answers, and exactly one due update plus
one practice result survives. The separate foundation race still verifies the existing
generation-based scheduler behavior. No shared-connection fake race substitutes for
these tests.

Fault injection rejects a finalization flush after in-memory progress changes. Progress
and completion both roll back, submitted evidence survives, and a subsequent valid
finalization succeeds. PostgreSQL rejects journal truncation; the existing completed
history mutation/deletion tests remain passing.

## Live boundary and remaining deployment work

[The read-only catalog audit](srs-review-data-audit.json) observes 2,810 catalog entries,
2,804 LOCAL_CODEX_REVIEWED entries, six holds, three users, one saved word at mastery
zero, no null saved due time and one lesson run at revision 0011. It reports 816 shared
Vietnamese gloss candidates, 2,181 multiple-gloss records and 214 compound POS labels
for editorial work. Structural counts do not certify semantic grading of all entries.
The source-bound initial three-policy JSON bundle was checked against the current
UUID/version/checksum, Pinyin and actual pronoun labels without writing policies.

No migration was applied to development, no real user's graded attempt was submitted,
and no policy was installed there. The pre-0012 preservation fingerprint is in the
ignored local backup directory; only counts/hashes are stored. No development backup
was restored. No Android code changed; Android build, emulator and device validation
are not claimed. Content beyond the prepared three policies still needs reviewed
disambiguating contexts before entering graded review generation.

The complete [engine/API/Android contract](srs-review-engine.md) and
[exact deployment procedure](runbooks/srs-0012-deployment.md) are ready for operator review.
