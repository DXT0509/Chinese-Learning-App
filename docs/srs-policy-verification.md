# Phase 4.1C verification — 2026-10-27

| Executed check | Result |
| --- | --- |
| Final complete backend suite with isolated PostgreSQL | **318 passed, 7 skipped**, 78.92 seconds |
| New preparation/import tests within that suite | 25 passed |
| `python -m ruff check .` | Passed |
| `python -m ruff format --check .` | Passed, 137 Python files |
| `git diff --check` | Passed; preexisting CRLF notices only |
| Policy schema validation and SHA-256 against audit | All 2,148 policies valid; hash matches |
| OpenAPI generation and authenticated review-target security declaration | Passed |
| Nonempty legacy → head migration rehearsal | Passed, original columns/references preserved |
| Nonempty 0010 → head SRS rehearsal | Passed, fingerprints and `alembic check` |
| Nonempty 0011 → 0012 review-history rehearsal | Passed, pending/completed history preserved and `alembic check` |
| Independent-connection scheduler and review-engine races | Passed |
| Independent regular-test database `alembic check` | Passed |
| Real-catalog bundle rehearsal in fresh isolated database | 2,148 validated, inserted, then resolved at runtime |
| Real-catalog reimport | Zero inserts, 2,148 unchanged |
| Real-catalog isolated `alembic check` | Passed |
| Repeat read-only development preview | Identical bundle SHA-256 and counts |
| Development preservation during bulk rehearsal | All 34 preexisting tables unchanged; still 0011 |

Machine-readable real-catalog rehearsal evidence is in
[srs-policy-bulk-verification.json](srs-policy-bulk-verification.json).
Only catalog batches, words, meanings and publication evidence were copied into
the isolated database. No real learner answers were submitted. The rehearsal
used the actual prepared bundle, exercised dry-run before import, checked that
dry-run left the policy table empty, committed one installation in the isolated
database, then reimported and resolved every catalog target. This is test evidence,
not operator authorization or a development installation.

The final suite used these newly created isolated databases:

| Variable | Database |
| --- | --- |
| `TEST_DATABASE_URL` | `chinese_p41c_regular_65467151fc` |
| `SRS_CONCURRENCY_TEST_DATABASE_URL` | `chinese_p41c_srs_race_0b91114df2` |
| `REVIEW_CONCURRENCY_TEST_DATABASE_URL` | `chinese_p41c_review_race_1e1ee001e4` |
| `MIGRATION_TEST_DATABASE_URL` | `chinese_p41c_legacy_upgrade_2b723b45f0` |
| `SRS_MIGRATION_TEST_DATABASE_URL` | `chinese_p41c_srs_upgrade_a2cf68b623` |
| `REVIEW_MIGRATION_TEST_DATABASE_URL` | `chinese_p41c_review_upgrade_687eb2172f` |

Regular/concurrency databases were migrated to exactly 0012 before the suite.
The three migration rehearsal databases started fresh and empty and their tests
performed the upgrades themselves. Rehearsals refuse existing tables and retain
fixtures. No database was reset, downgraded or dropped. Global publication opt-ins
were disabled for the suite; individual publication tests set their required flags.
The separate real-catalog rehearsal used development's existing publication rules
against its isolated catalog copy.

The seven skipped optional checks were unrelated dedicated rehearsals for
dictionary, enrichment, personal wordbook, AI-review and curated migrations,
the destructive-reset/backup workflow, and the specially isolated local-Codex
operator workflow. Their required URLs/port were not provided; none is claimed
as successful. Existing authentication, publication, dictionary, saved vocabulary,
review engine and SRS regressions ran on the regular isolated test database.
Warnings were the preexisting Starlette TestClient/httpx deprecation and SQLAlchemy
reflection `dialect_options` warnings in the three migration rehearsals.

New tests cover deterministic ordering, repeated generation, multiple meanings
retained in full, shared glosses with explicit distinct cues, Unicode-equivalent
cue collisions, held competing readings, missing/ambiguous POS and cues, measure
words, missing/unusable Vietnamese prompts, duplicate identities and policies,
outdated checksums, preserved manual policies, reassessed generated policies,
dry-run, atomic rollback after a later batch failure, idempotent imports,
publication rejection, generated-prompt tampering and runtime exclusion after
a new held cue collision or changed checksum. Exclusion creates no failure,
review count or schedule change. Existing HTTP tests cover authentication,
ownership, ungradable submissions and no false learner penalties.

To reproduce, provision new empty migration-rehearsal databases and isolated
regular/concurrency databases, set the six URLs above to those new resources,
migrate only regular/concurrency databases to 0012, and run from `backend/`:

```powershell
$env:ENVIRONMENT = 'test'
$env:ALLOW_AI_APPROVED_VOCABULARY = 'false'
$env:ALLOW_LOCAL_CODEX_REVIEWED_VOCABULARY = 'false'
.venv\Scripts\python -m pytest -q --tb=short
.venv\Scripts\python -m ruff check .
.venv\Scripts\python -m ruff format --check .
# Set DATABASE_URL to the isolated regular-test database before schema validation.
.venv\Scripts\python -m alembic check
```

No dependency or migration changes were required for Phase 4.1C. Android files
were unchanged; no Android build, emulator or physical-device validation is claimed.
Review UI implementation remains Phase 4.2 work.
