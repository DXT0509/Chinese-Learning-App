# Actual Codex review checkpoint — incomplete

801 of 2,501 pronunciation records are individually reviewed: all Levels 0–3 and
L4-B001–L4-B003. Next is **L4-B004**; 1,700 records remain unreviewed.

787 passing non-held records are candidates for **local-codex-session-v1** acceptance,
without numerical confidence or invented model identity. Six older editorial holds
and eight genuine linguistic uncertainties remain excluded. The production
AI_APPROVED contract is unchanged; zero strict results were invented or submitted.

Use [the operator runbook](../../runbooks/local-codex-vocabulary.md) for the new
explicit development opt-in, read-only preview, separate migration/import
confirmations, automatic local receipts/statuses and Android search checks.
See [the report](../../phase4.0.3-codex-review.md), [progress](progress.json),
[corrections](corrections.json), [pending issues](pending.json) and
[local read-only plan](local-plan.json).

Per-batch `review-notes.json` and `deployment.jsonl` bind actual notes to exact
source/current checksums and versions. `provisional-deployment.jsonl` contains ALL
2,501 records, including held/unreviewed ones; it is not an accepted import list.
`checkpoint.py` verifies the original 50-batch audit and rebuilds that provisional
copy. The local importer selects only completed passing reviews itself.

Do not rerun `batch_notes_01.py`–`11.py` over existing directories: these preserve
actual authored findings, not unattended reviewer implementations. Review the next
batch's complete fields/examples before recording its notes. Never manufacture
passing notes or model snapshots to complete coverage.

No development database writes or paid API calls were made. Alembic 0009 remains
applied there; additive 0010 is awaiting explicit operator migration.
