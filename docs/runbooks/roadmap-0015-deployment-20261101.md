# Authorized local roadmap deployment — 1 November 2026

`0015_roadmap_engine` was successfully applied to the actual local development database
after the user's explicit authorization and a successful final preflight. Content import,
publication and activation remain unauthorized and were not performed.

The verified target was `chinese_learning` on `127.0.0.1:5432`, PostgreSQL 18.3, role
`postgres`, environment `development`. Its actual starting revision was
`0014_fsrs_only`; its verified final revision is `0015_roadmap_engine`.

Machine-readable results: [deployment report](../roadmap-0015-deployment-20261101.json).

## Preflight, backup and migration

The migration file SHA-256 was
`74c417eb744015fb8e97d5544e2972f5d0ac44da84db72d3ba21b719981ce4fd`.
Review confirmed one nullable JSONB column, nine new tables, three explicit indexes,
foreign keys/checks, new guards and an extension of the existing lesson-publication
function. The original preview publication branch remains. There were no table drops,
learner updates, backfills, catalog deletion or automatic content publication.

The identified development Uvicorn process group was stopped. Preflight confirmed no
other database clients and no pre-existing roadmap tables. Original-column row fingerprints
were captured for all 38 existing application tables. The same baseline was checked
again after backup and immediately before migration; the migration file and backup
hashes were checked again before execution.

A compressed custom-format full database backup was created and its archive list
successfully inspected with `pg_restore --list` (both PostgreSQL tools exited 0):

```text
backend/.vocabulary-backups/roadmap-0015-20261101T090326Z/before-migration.dump
3,582,158 bytes
SHA-256 fbcfd2f9bdd51eff72a426b9266695c9c6f1e06240236379164c840b7028de70
```

The private, Git-ignored directory also retains before/after/final fingerprints, schema
inspection, API probes and focused-test output. No credential or actual row content was
printed in verification output. This deployment inspected the backup archive but did
not restore it over any database.

The exact command `python -m alembic upgrade 0015_roadmap_engine` completed successfully
with bounded lock/statement timeouts. No reset, downgrade or volume deletion occurred.

## Actual development preservation and schema

All original rows and every original column matched before/after fingerprints across
all 38 original tables. Verification was repeated after backend restart, read-only
development probes and isolated regressions. Existing source-of-truth counts include:

| Data | Preserved rows |
| --- | ---: |
| Accounts / password credentials | 3 / 3 |
| Curated vocabulary / revision history | 2,810 / 2,810 |
| Installed grading policies | 2,804 |
| Saved curated words, including mastery/schedules/activation flags | 52 |
| FSRS memory cards, configurations and state | 33 |
| Review attempts and their complete evidence/history | 85 |
| Durable daily plans / active-time records | 10 / 56 |
| Existing authentication sessions / refresh credentials | 15 / 51 |

Every other original table also matched, including preview runs/checkpoints, legacy
vocabulary/progress and optional personal vocabulary tables. No real graded attempt,
EXP grant, lesson progress or FSRS schedule was created or modified.

All nine new tables exist and remain empty: `roadmaps`, `roadmap_versions`,
`roadmap_node_identities`, `roadmap_nodes`, `roadmap_vocabulary`, `roadmap_progress`,
`roadmap_runs`, `roadmap_activity_receipts`, `roadmap_exp_grants`.

Their 41 primary/unique/check/foreign-key constraints and 40 NOT NULL constraints were
verified against the model definitions. PostgreSQL 18 exposes NOT NULL constraints
separately; identifier checking also accounted for SQLAlchemy's long-name truncation.
All ten new guard triggers are enabled. The first-run partial unique index, existing
lesson-publication trigger, original preview branch and executable branch were verified.
`lesson_versions.engine_definition` is nullable JSONB, has no default and is NULL on the
existing lesson. Actual development `alembic check` reports no upgrade operations.

## API and regression results

The backend was restarted using the project venv and current source, with reload,
safe JSON logging, access logs disabled and the psycopg-compatible event loop.
There is one development listener at `http://127.0.0.1:8000`; startup completed cleanly.

Live checks returned health 200, all eight roadmap routes in OpenAPI, and 401/no-store
for every roadmap route without authentication. An invalid Bearer token also returned
401. No real credentials were used and no session was created, rotated or revoked.

Read-only transactions against the actual development database exercised roadmap
listing/summary and the existing FSRS dashboard for all three accounts. Roadmap listing
is empty, each account has zero roadmap EXP/completion/skip counts, and existing FSRS
dashboards retain the FSRS 6.3.2 scheduler and 1,200-second daily target. Fingerprints
confirmed these probes caused no writes.

Live authenticated HTTP success was not exercised without user credentials. Authenticated
request/response flows, ownership isolation and completion semantics were instead tested
with synthetic accounts in isolated PostgreSQL databases; they did not touch development.

Focused verification: **58 passed, 0 skipped**, 27.43 seconds. Modules:

```text
test_roadmap.py
test_roadmap_postgres.py
test_roadmap_migration.py
test_fsrs_only.py
test_fsrs_v2.py
test_srs_v2_postgres.py
test_sessions.py
```

This includes concurrent completion, repeated replay, authenticated HTTP execution,
preservation of existing saves/FSRS state and a nonempty 0014→0015 rehearsal that also
exercises the operator preflight. Isolated Alembic schema checking passed. Source-scoped
Ruff checks and formatting passed (178 files). The two warnings are existing
Starlette/httpx deprecation and SQLAlchemy/PostgreSQL reflection warnings.

Fresh isolated fixtures were retained in
`chinese_roadmap_deploy_{test,concurrent,v2,upgrade}_20261101090710`.

## Phase 6.2 readiness

There is no identified schema/runtime blocker to Android contract integration and
authenticated empty-state roadmap browsing. No roadmap is available to play because
no content has been imported, published or activated. A reviewed roadmap requires
separate operator authorization before a real learning flow can be exercised.

Handwriting and pronunciation remain participation contracts, not quality evaluation.
Android implementation/device validation remains Phase 6.2 work. The remaining live
authenticated HTTP smoke check can use the user's ordinary sign-in when convenient;
this deployment deliberately left all existing sessions untouched.
