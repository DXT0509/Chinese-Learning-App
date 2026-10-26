# Actual Codex review checkpoint — complete with retained holds

Deployment update, 2026-10-26: migration 0010 and the separately confirmed local
import have completed as operator **dxt**. All 2,482 candidates have matching local
receipts; six holds remain in the database and thirteen unresolved drafts are excluded.
See the [current deployment report](../../runbooks/phase403-deployment-session.md).
The review-time snapshots and statements below describe the earlier review activity.

All **2,501 pronunciation records / 2,500 written items / 50 batches**, Levels 0–5,
have actual individual linguistic notes. No unfinished batch remains.

**2,482 candidates** pass `local-codex-session-v1`; **640 records** have corrected
linguistic content (634 candidates and six still-held drafts). **19 are excluded**:
six protected editorial holds and thirteen pronunciation/sense/identity findings.
Candidates are ready for explicitly confirmed local acceptance; none has been
imported or published by this review. No numerical confidence is required, exact
model/version remain null, and the production AI_APPROVED contract is unchanged.

- [Final audit](final-audit.json): per-level counts, strict validation and hashes.
- [Progress](progress.json), [all corrections](corrections.json), [pending reasons](pending.json).
- [Complete catalog](provisional-deployment.jsonl): 2,501 reviewed records, including holds;
  historical filename retained. It is not an accepted import list.
- [Accepted subset](accepted-deployment.jsonl): 2,482 reviewed candidates; still drafts.
- [Validated local evidence](local-acceptance-validation.json).
- [Read-only development plan](local-plan.json): 2,437 inserts + 45 local acceptances.
- [Read-only DB snapshot](database-inspection-read-only.json): 0009 applied, 0010 unapplied.
- [Operator runbook](../../runbooks/local-codex-vocabulary.md): exact PowerShell order,
  explicit migration/import confirmation, automatic local receipts, recovery and Android.
- [Final report](../../phase4.0.3-codex-review.md).

Each batch's `review-notes.json` binds genuine notes to source/deployment bytes and
per-record checksums/versions. Corrections were re-read by the same session, without
claiming another independent model. First-pass evidence for targeted rechecks remains
in `superseded/`; later corrections increase versions and bind the replacement notes.

Do not rerun `batch_notes_01.py`–`45.py` or `final_recheck.py`: they preserve already
authored findings and refuse replacement of existing evidence. They do not perform
unattended linguistic review. `checkpoint.py` and `final_audit.py` safely rebuild and
validate aggregate artifacts without accessing the database or paid providers.

Original Gemini files and historical migrations are unchanged. No development
database writes or paid API calls were made.
