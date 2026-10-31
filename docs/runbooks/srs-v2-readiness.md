# Phase 5.0 readiness — 31 October 2026

Historical implementation preview. Superseded by the later authorized
[FSRS-only local deployment](srs-fsrs-only-deployment.md), including updated
verification results, minimal backup and removal of the v1 runtime scheduler.

**Code and isolated verification complete; development deployment is NO-GO pending
backup approval/verification and a separate deployment authorization.**

## Deliverables

| Requirement | Result |
| --- | --- |
| FSRS implementation | Upstream py-fsrs 6.3.2 pinned; installed API inspected; parameters/version persisted |
| Architecture | Transaction-owning SrsService remains sole scheduling boundary; additive FSRS memory and durable daily plans |
| Grading | New gradeable attempts pin HANZI/PINYIN only; first valid answers sealed; binary server grading |
| Handwriting | Graded keyboard removed; bounded strokes, candidate membership and exact answer transcription required; client attestation limitation documented |
| Daily target | 1,200 seconds, historical duration estimate, risk selection then stored random order, recovery, deferral and explicit continuation |
| Rating behavior | FAIL=Again; PASS=Good; upstream learning/relearning and long-term intervals, 36,500-day bound |
| Mastery | Existing 0–5 progress semantics separated into a function with no interval calculation |
| History | No payload rewrites; existing schedules unchanged until next eligible review; recorded-only replay |
| Policies | Format 2 projection with source version/hash; 2,804/2,804 validated; zero installations |
| Android | Two compact selectors, mandatory canvas, independent Pinyin drafts, budget/backlog/pending display, prefetch retained |
| Reliability | Unit/DB tests cover first-result sealing, concurrent attempts, duplicate finalization, draft/ink recovery, time receipts and nonempty migration preservation |
| Simulation | 500/2,000/5,000-word synthetic cohorts and uncapped comparators; assumptions/limitations explicit |
| Database | Prepared immutable 0013: one Boolean column, three empty tables, constraints/index; zero schedule/mastery/history/policy edits |
| Operations | Read-only before/after preflight, prepared backup/restore script, exact write counts, containment/rollback and separate approval gate |

Implementation details: [SRS v2](../srs-v2.md).
Deployment procedure: [approval checkpoint](srs-v2-deployment.md).

## Executed checks

From `backend/`:

```powershell
.venv/Scripts/python -m scripts.srs_v2_isolated_checks
```

Final full run: **415 passed, 10 skipped**, 141.89 seconds. Five fresh migrated
test/concurrency databases and one fresh empty migration database were created,
with unique `chinese_srs_v2_*_20261030171157` names. No tables/databases/volumes
were reset or dropped; fixtures remain. New v2 tests opt in through test-local
configuration; the legacy suite exercises compatibility with the rollout disabled.
The populated 0012→0013 rehearsal preserved every pre-existing selected column and
policy/journal row, verified existing activation=true and empty new tables.
`alembic check`: **passed** on both the rehearsed schema and normal isolated schema.
The ten skips are separately gated older migration/operator/reset rehearsals whose
dedicated URLs were not supplied; they are not v2 coverage claims.

A final focused follow-up after moving the rollback guard behind creation-key replay
and enforcing exact replay of optional ink evidence: **34 passed, 3 skipped** in
11.51 seconds. It covered v2 persistence/timing, legacy creation/submission replay,
FSRS pure behavior and rollback containment. The three skips require independent
concurrency URLs; their full-run counterparts had already passed against separate
databases. Retrying a key while removing its original ink evidence is rejected.

Changed Python files: Ruff lint and format checks **passed**. `pip check` **passed**.
The lock was refreshed after installing fsrs. Existing warnings remain: FastAPI's
httpx TestClient deprecation and SQLAlchemy reflection of an older dialect option.

From `android/`:

```powershell
.\gradlew.bat testDebugUnitTest assembleDebug lintDebug compileDebugAndroidTestKotlin --console=plain
```

**132 unit tests passed**, zero failed/skipped. Debug APK built; lint completed
with **0 errors, 78 warnings**; instrumentation sources compiled. Existing
dictionary/grammar resource labels remain for metadata and historical coverage;
unused resources contribute warnings. No lint suppression was introduced.
The final APK is `android/app/build/outputs/apk/debug/app-debug.apk`.
It was **not installed** on a learner device.

Performance regression assertions retain one plan selection, no per-word catalog
reload/progress fetch, reuse of ready prefetch, no duplicate attempt creation,
stable recovery order and unchanged first-answer results. Timing uses a separate
receipt and excludes windows crossing review network operations. Ink remains in
its own ViewModel; pending retries reference the existing serialized ink draft
instead of storing a second large copy in saved state. These are deterministic
regression checks, not emulator throughput or production latency measurements.

## Development preservation and preview

Both snapshots used database-enforced READ ONLY transactions:

* [Before](../srs-v2-preflight.json), captured 30 October 2026 17:00:57 UTC
  (31 October 00:00:57 Bangkok/Vietnam).
* [After](../srs-v2-preflight-after-checks.json), captured after implementation checks.

Revision remained **0012_srs_review_engine**. Counts and all six reported table
fingerprints match exactly: 3 users, 27 curated saves, 20 attempts, 2,804 policies,
zero personal vocabulary entries and zero legacy curated review submissions.
No real learner grading or new policy installation was performed.

The [policy preview bundle](../datasets/srs-v2-two-stage-policies.json) was generated
in a READ ONLY transaction: **2,804 valid, 0 unavailable, 0 writes**.
The [synthetic workload simulation](../srs-v2-simulation.json) was executed entirely
in memory. It makes no observed retention claim; fixed success rates under long
deferral are optimistic and transition backlogs can be substantial.

## Remaining gates and limits

* Backup restore verification has **not run**. Automatic approval review rejected
  exporting the development database and retaining an isolated restored copy without
  explicit permission. The script is prepared and linted; no backup success is claimed.
* User authorization to run that rehearsal is separate from authorization to apply 0013.
  Development deployment requires verified backup, refreshed preflight/write counts,
  maintenance coordination and explicit approval of the exact target database.
* Real device/emulator validation remains pending: ML Kit model download/native
  inference, stylus/finger interaction, frame pacing, background recovery and timing.
  Instrumentation compilation is not device execution.
* Client-provided ink is structurally validated, not hardware-attested. Five-second
  timing is approximate and can lose partial/unacknowledged windows. Vietnam local
  day is the current explicit product default; a timezone settings UI is deferred.
* Do not restart the development API with this model source before approved 0013.
  Do not downgrade schema or restore over newer learner history as a casual rollback.
