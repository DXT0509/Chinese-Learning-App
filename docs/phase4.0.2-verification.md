# Phase 4.0.2 verification

Implementation is complete for auditing, configured review orchestration, bounded
correction attempts, database reconciliation, confirmed bulk import and confirmed
review submission. Genuine semantic execution and development writes are blocked.

| Executed check | Result |
| --- | --- |
| Final full backend pytest suite | 208 passed, 6 skipped; 55.70 seconds |
| Focused pipeline/review/catalog regressions before final full run | 53 passed |
| Repository-wide Ruff: app, scripts, tests, alembic | Passed |
| Ruff formatting: all six changed/new Python files | Passed |
| pip check | No broken requirements |
| Fresh isolated upgrade through 0009 | Passed |
| Nonempty 0008 → 0009 preservation rehearsal | Passed, twice on distinct fresh databases |
| Alembic check on isolated migrated regression and full-catalog databases | No new upgrade operations |
| Global source scan | 50 batches; all hashes and repository validation passed |
| Full real CLI import into isolated phase402_catalog | 2,501 records imported; 50 committed batches |
| Full real CLI import restart/repeat | All 50 batches unchanged; 2,501 identical records |
| Isolated catalog after both runs | 2,496 GENERATED_UNREVIEWED, 5 NEEDS_REVIEW; no approvals/publication |
| Development reconciliation | Read-only; 51 identities present, 50 exact matches, 1 hold conflict, 2,450 new |
| Real external AI calls / semantic reviews | None |
| Development migrations / imports / review submissions / flag changes | None |
| Live development HTTP API checks / Android / device validation | Not performed |

The final pytest run used a fresh private PostgreSQL 18 cluster on
127.0.0.1:55442, with phase402_regression and a separate fresh
phase402_review_migration_final database. Development PostgreSQL at port 5432
was never used for tests. The earlier migration rehearsal used its own fresh
phase402_review_migration database. Test fixtures and imported source records
remain intact in the isolated cluster. The six skipped tests lacked optional
environment/database configuration. Existing Starlette/httpx deprecation and
SQLAlchemy dialect_options reflection warnings were observed.

New tests cover all 50 source batches, global duplicate/registry mismatches,
hash tampering, unavailable credentials, byte-bound generator evidence, strict
response/schema/policy rejection, provider/model independence, stale input
checksums, correction versions and a distinct correction reviewer, call budgets,
unknown transport outcomes, durable receipt replay, altered result files,
post-commit interruption/recovery, idempotent import, changed source bytes,
catalog drift behind an existing batch receipt, and database-bound confirmation.
Provider fixtures are explicitly synthetic and are never submitted to development.

Existing HTTP integration tests ran through the actual ASGI application and verified
AI visibility opt-in for search/detail/save, pending/rejected exclusions, editorial
holds, stale approvals, append-only evidence, cross-user isolation and preservation
of saved mastery/schedules across revisions. This proves test application behavior;
it does not prove an independently running development backend was restarted with
publication enabled. The flag was not changed during this task.

Audit found 360 exact-form/shared-Vietnamese-gloss candidate groups. These are
linguistic review candidates, not 360 confirmed duplicate words. There are zero
duplicate lexical keys or Simplified+numbered-Pinyin identities. Historical Batch
001 identifiers, source hash, converted records and full conversion mappings match.

Remaining work requires authentic generator history, configured real reviewer
credentials/models and a deliberately selected spending budget. No model identity
was inferred from generator helper defaults. The alternate 谁 reading lacks an
example; five source holds remain. The additional existing 厕所 hold must be
preserved through a new versioned correction before any development import can
pass reconciliation. Explicit operator confirmation of the resulting database
write plan is still required. No pending content was removed or falsely published.

See [execution commands and configuration](bulk-vocabulary-pipeline.md),
[global integrity audit](datasets/phase4.0.2-integrity-audit.json), and
[development coverage snapshot](datasets/phase4.0.2-coverage-report.json).
