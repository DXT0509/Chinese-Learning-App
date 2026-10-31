# Newly saved vocabulary is immediately due

31 October 2026 (Vietnam/Bangkok time).

New saves were excluded from due counts until their first completed review, and
the daily planner admitted only five new identities per day. Android also retained
an empty plan's request key: subsequent starts replayed the empty response even
after more words were saved. HTTP 200 therefore did not imply a usable session.

Due dashboard counts, daily backlog metrics and the due endpoint now include all
visible active unreviewed saves. The planner no longer caps new identities per day;
existing review priority, session capacity and the daily time target remain.
`learning_activated` still records first eligible completion. Existing mastery,
history and schedules are preserved. No application migration is required.

Android clears empty plan keys, refreshes counts and explains an empty selection.
Dashboard refresh clears an old key when no queue or attempt needs recovery.
Ambiguous request failures retain their keys. The pending label explicitly says
these words are a subset of the due total. Two existing due words plus four new
saves therefore produce six due words, of which four have never been reviewed.

Verification:

- Backend full suite: 396 passed, 15 skipped, one existing Starlette warning.
  Used the retained synthetic PostgreSQL cluster on port 55444, database
  `chinese_phase44_regular`, upgraded from 0012 to 0014 for these tests only.
  Temporary test files used a workspace directory to avoid Windows temp permission
  errors. Separate migration/concurrency database checks were not enabled.
- Regression covers 26 previous saves/reservations, an empty plan, four additional
  saves, matching due counts/identities and initialization of all four new reviews.
  Another regression verifies more than five new saves can enter a plan.
- Android: 134 unit tests passed; `testDebugUnitTest assembleDebug lintDebug`
  succeeded. Lint: zero errors, 78 warnings. Regression covers empty-response
  recovery and refresh of a restored empty plan key.
- Ruff checks passed for affected Python files. Isolated `alembic check` reported
  no new upgrade operations, with an existing SQLAlchemy warning.
- Debug APK installed over the connected phone with `adb install -r` successfully.
  Backend reload mode was verified. No learner review was submitted and no device
  UI or instrumentation validation is claimed. Development data was not migrated.

Evidence logs (ignored): `srs-new-saves-backend-final.log`,
`srs-new-saves-android-final.log`, `srs-new-saves-alembic.log`.
