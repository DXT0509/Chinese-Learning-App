# Phase 6.3A preparation verification

Date: 1 November 2026. See [the design and operator guide](../roadmap-phase-6.3a.md).

## Safety boundary

Development content import, publication and activation were not executed. No development
catalog, learner progress, EXP grants, memory cards or schedules were modified. There is
no new migration or dependency. The existing isolated runner creates fresh dedicated
databases and retains fixtures; it never resets, drops or downgrades development.
Synthetic test review attestations exist only in test fixtures and do not approve any
actual educational content. No external asset/provider was downloaded, paid for or invoked.

## Executed commands

From `backend/`:

```powershell
.venv/Scripts/python -m ruff check app scripts tests
.venv/Scripts/python -m ruff format --check app/schemas/roadmap_preparation.py app/services/roadmap_preparation.py app/services/content_files.py scripts/roadmap.py scripts/_content_cli.py tests/test_roadmap_preparation.py tests/test_roadmap_preparation_postgres.py
.venv/Scripts/python -m scripts.roadmap_isolated_checks
```

Ruff checks passed across `app`, `scripts` and `tests`; all seven changed Python files
passed formatting checks. The isolated runner executes the full backend suite, including
roadmap engine/Android backend contracts, concurrent completion and EXP protection,
nonempty legacy/FSRS/roadmap migration rehearsals, and `alembic check` against its isolated
test database. It does not migrate the configured development database.

The first full isolated run (`20261101143050`) passed **450 tests, 9 skipped** in
113.81 seconds; `alembic check` exit 0. Subsequent asset-import compatibility testing
found the old loader's mandatory lesson requirement. An explicit assets-only mode now
refuses mixed content while retaining the default loader behavior. A fresh final full
run verifies that additive path along with the additional tests; see final results below.

Earlier focused runs caught and corrected missing pytest temporary-parent setup and a
manifest validation gap (removed catalog bindings). Their failures are not reported as
passing results. Preparation validation now compares the complete expected manifest,
asset registrations, per-lesson files and CAS bytes rather than trusting a partial list.

The following filesystem commands were also executed for the checked-in HSK 0 plan:
`generate-drafts`, `check-content`, `prepare-bundle`, `roadmap --help`, and
`scripts.validate_content --assets-only` against the generated asset library. The library
is correctly empty because no real reviewed assets are supplied. Generation was repeated
successfully; unit tests verify unchanged files retain timestamps and missing checkpoint
files are restored on resume. CLI preview is tested to omit answer keys, and all offline
commands are tested with database session creation replaced by a failure sentinel.

## Draft inventory and release blockers

The generated three-word NEW_WORD group and its exact REVIEW are schema-compatible.
There are 31 activities: 4 introductions, 3 original-ink freehand and 24 exact-choice quizzes.
The current reports contain **0 ERROR, 2 WARNING and 15 OPTIONAL_MISSING**.

Each word (我, 你, 好) has no newly supplied reviewed audio, stroke-order asset, component
analysis, examples or notes. Source catalog examples are not automatically reclassified
as human-reviewed enrichment. Neither silent audio nor synthetic stroke illustrations
are shipped; tiny transport fixtures in tests are explicitly noneducational.

Publication is **not ready**. Individual educational review, current approved database
revision reconciliation and separate operator authorization remain prerequisites. Real
asset source/licensing verification, playback and stroke-order correctness require a
qualified reviewer when assets are supplied. Structured centerlines remain preparation
only pending an Android renderer. Per-example audio and matching need explicit contract
extensions. Device/emulator testing and Android Gradle checks were not run because this
phase changes no Android activity/wire contract; backend tests do not establish device
behavior.

## Final isolated results

Final fresh databases use suffix `20261101143628`; all eight are intentionally retained.
The full final run passed **454 tests, 9 skipped, 4 warnings** in **110.83 seconds**.
Isolated `alembic check` exited **0**. The 31 added tests comprise 29 preparation tests
and two rollback-only PostgreSQL compatibility tests. They verify draft import/preview
idempotence, refusal of unapproved revisions, inactive DRAFT state, unchanged learner
table counts, and registration through the existing asset importer without creating
legacy vocabulary. Existing backend Android contracts also passed in the full run.

The nine skips require dedicated historical migration/operator/reset environment variables:
AI_REVIEW, ENRICHMENT, DICTIONARY, LOCAL_CODEX_OPERATOR, WORDBOOK, REVIEW, SRS, CURATED and
VOCABULARY_RESET test URLs. They are not counted as successful migration checks. The
runner did execute its nonempty legacy, FSRS v2 and roadmap rehearsals on fresh databases.
Warnings are the existing Starlette/httpx deprecation and SQLAlchemy reflection warnings.
