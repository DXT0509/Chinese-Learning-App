# Phase 4.1D additive installation — not executed on development

Historical 414-policy candidate. For the complete 656-addition candidate, use the
[final deployment procedure](srs-phase41d-complete-installation.md). This older
procedure remains below for provenance; neither procedure authorizes deployment.

Candidate: [srs-phase41d-policies.json](../datasets/srs-phase41d-policies.json).
SHA-256: `55220d14c466a3b9ac7c1b12624a48647bd4e4e9b263d8c8fdfe8b475aa1d159`.
Target: `chinese_learning`, `127.0.0.1:5432`, role `postgres`, revision 0012.
Preview: **414 INSERT, zero UPDATE, 2,148 unchanged, zero personal-data writes**.
Expected resulting coverage: **2,562 / 2,804**, not 100%.

## Preparation and approval

1. Finish operator review of the precise candidate and its linguistic limitations
   in [the checkpoint report](../srs-phase41d-coverage.md). Do not treat an automatic
   generation label as human approval. Record the desired deployment scope.
2. Stop the API for the maintenance interval. Read database identity and revision;
   do not rely on an environment filename. Ensure no catalog publication runs.
3. From `backend/`, run read-only validation:

   ```powershell
   .venv\Scripts\python -m scripts.review_policies --file ..\docs\datasets\srs-phase41d-policies.json
   if ($LASTEXITCODE -ne 0) { throw 'Stop: policy validation failed' }
   ```

   Expected: validated 2,562, unchanged 2,148, would_insert 414,
   would_update zero, inserted zero. Changed counts or any conflict require a new
   audit. Never overwrite an installed policy to repair a conflict.
4. Regenerate to **new** output paths and compare exact bundle SHA-256:

   ```powershell
   .venv\Scripts\python -m scripts.prepare_review_policies --complete-coverage --dry-run --preserve-file ..\docs\datasets\srs-phase41d-reviewed-contexts.json --output .vocabulary-backups\phase41d-next-preview.json --audit .vocabulary-backups\phase41d-next-audit.json
   if ($LASTEXITCODE -ne 0) { throw 'Stop: preparation failed' }
   Get-FileHash .vocabulary-backups\phase41d-next-preview.json -Algorithm SHA256
   ```

   Inspect `database_target`, current published denominator, stale/unknown bindings,
   per-level counts and all unresolved rows. Existing paths are deliberately refused.
5. Create a **fresh** custom-format `pg_dump` of that exact database using existing
   secure local credentials. Record its size and SHA-256. Verify the archive can
   be read with `pg_restore --list` and restore it to a newly named isolated database;
   never restore over development. Rehearse the candidate there, including an
   idempotent reimport. No database reset, downgrade or volume deletion.
6. Fingerprint every non-policy table in UTC with full `to_jsonb(row)` canonical
   sorting; include users, sessions, saved vocabulary, mastery/schedule state,
   attempts and their submissions, review results, publication receipts and
   revision history. Compare original policy payloads verbatim as well. Save
   private evidence under ignored `.vocabulary-backups/`.
7. Present the exact target, candidate hash, INSERT/UPDATE counts, fresh backup
   verification and preservation plan, then request **explicit operator
   authorization**. The user specifically requires this before development writes.
   Authorization to implement or run isolated tests is not installation approval.

## Authorized action only

Only after the preceding approval:

```powershell
.venv\Scripts\python -m scripts.review_policies --file ..\docs\datasets\srs-phase41d-policies.json --install
if ($LASTEXITCODE -ne 0) { throw 'Stop: installation failed; inspect without retrying blindly' }
```

The importer owns one caller-wrapped transaction and catalog/publication locks;
it inserts missing policies only. No migration or vocabulary publication belongs
to this installation. Failures roll back the batch. Never manually change saved
word mastery, attempt targets or scheduling state.

## Post-deployment verification

1. Keep the API stopped until all pre/post non-policy fingerprints match. Confirm
   all 2,148 original policy JSON payloads are identical, no duplicates/stale rows,
   and exactly 414 additional rows exist.
2. Re-run the command without `--install`: expect 2,562 unchanged, zero proposed
   inserts/updates. Compare full-table fingerprints again.
3. Resolve every **published** identity through `ReviewedTargets` read-only.
   Expected coverage and per-level counts are in the checkpoint report. List the
   remaining 242 by exact lexical identity; retain all six unpublished holds.
4. Restart the updated API source. Check liveness, OpenAPI and unauthenticated 401s
   using GET only. Authenticated queue/dashboard GET checks may use an existing
   authorized session. Do not create real graded attempts for deployment testing.
5. On an isolated synthetic account/database, verify complete prompt rendering,
   one-/multi-select POS, handwriting counts, tone rejection, wrong-stage FAIL,
   assistance/first-answer rules, idempotence and unchanged SRS transitions.
   Device checks must be recorded separately from unit/build verification.
6. Publish a deployment receipt with actual target, hashes, counts and preserved
   fingerprints. Keep the 242-entry editorial continuation checkpoint open until
   versioned reviewed corrections and their policies are genuinely completed.
