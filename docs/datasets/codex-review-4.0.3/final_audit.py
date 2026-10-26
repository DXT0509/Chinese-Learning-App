"""Reconcile finished review artifacts with actual evidence; no DB/provider access."""
import json
from collections import Counter
from datetime import UTC, datetime

from checkpoint import ROOT, SOURCE, ASPECTS, read
from app.services.curated_import import digest, load_records, record_checksum
from app.services.local_codex_review import load_checkpoint

accepted, evidence, coverage = load_checkpoint(ROOT)
complete_sha, complete = load_records(ROOT / "provisional-deployment.jsonl")
assert coverage["reviewed"] == 2501 and coverage["unreviewed"] == 0
assert len(coverage["receipts"]) == 50
assert len({r.simplified for r in complete}) == 2500
assert len({r.lexical_key for r in complete}) == 2501
assert len({(r.simplified, r.pinyin_numbered) for r in complete}) == 2501
by_level = {level: Counter() for level in range(6)}
actual_content_corrections = []
status_only_revisions = []
corrected_accepted = 0
for receipt in coverage["receipts"]:
    notes = read(ROOT / receipt["batch"] / "review-notes.json")
    assert notes["reviewer_model"] is None
    assert notes["reviewer_version"] is None
    assert notes["confidence"] is None
    originals = {r.lexical_key: r for r in load_records(SOURCE / notes["source_file"])[1]}
    revised = load_records(ROOT / receipt["batch"] / "deployment.jsonl")[1]
    by_level[revised[0].learning_level]["batches"] += 1
    for record, finding in zip(revised, notes["records"], strict=True):
        original = originals[record.lexical_key]
        assert record.lexical_key == finding["lexical_key"]
        assert record.learning_level == original.learning_level
        assert record.pinyin_numbered == original.pinyin_numbered
        assert record.simplified == original.simplified
        assert finding["source_checksum"] == record_checksum(original)
        assert finding["reviewed_checksum"] == record_checksum(record)
        assert set(finding["checked_aspects"]) == set(ASPECTS)
        assert finding["note"].strip() and record.examples
        changed = {k for k, v in record.model_dump().items()
                   if v != original.model_dump()[k]} - {"content_version", "review_status"}
        if changed:
            assert finding["correction"] is not None
            assert record.content_version > original.content_version
            actual_content_corrections.append(record.lexical_key)
        elif record.content_version != original.content_version:
            status_only_revisions.append(record.lexical_key)
        stats = by_level[record.learning_level]
        stats["reviewed"] += 1
        if changed:
            stats["corrected_content"] += 1
        if finding["local_development_candidate"]:
            assert finding["linguistic_outcome"] in {"PASS", "CORRECTED_PASS"}
            assert not finding["pending_reason"]
            assert record.lexical_key in evidence
            stats["accepted_candidates"] += 1
            corrected_accepted += bool(changed)
        else:
            stats["excluded"] += 1
assert len(accepted) + len(coverage["excluded"]) == len(complete)
accepted_file = ROOT / "accepted-deployment.jsonl"
accepted_file.write_text("\n".join(r.model_dump_json() for r in accepted) + "\n", encoding="utf-8")
accepted_sha, accepted_again = load_records(accepted_file)
assert len(accepted_again) == len(accepted)
(ROOT / "local-acceptance-validation.json").write_text(
    json.dumps(coverage, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
result = {
    "status": "PASSED_FULL_REVIEW_RECONCILIATION",
    "verified_at": datetime.now(UTC).isoformat(),
    "reviewed": len(complete), "batches": len(coverage["receipts"]),
    "unique_written_items": 2500, "pronunciation_identities": 2501,
    "accepted_candidates": len(accepted), "excluded": len(coverage["excluded"]),
    "actual_linguistic_content_corrections": len(actual_content_corrections),
    "corrected_accepted_candidates": corrected_accepted,
    "correction_ledger_records": len(read(ROOT / "corrections.json")),
    "status_only_versioned_records": status_only_revisions,
    "per_level": {str(k): dict(v) for k, v in by_level.items()},
    "complete_dataset": "provisional-deployment.jsonl", "complete_sha256": complete_sha,
    "accepted_dataset": accepted_file.name, "accepted_sha256": accepted_sha,
    "checks": ["strict JSONL contracts including Simplified-only and pinyin formatting",
               "all original/current byte hashes and per-record versions/checksums",
               "all 50 complete per-record note sets; all nine aspects",
               "global written and pronunciation identity counts; no duplicate keys",
               "stable keys, pronunciation identities and app levels preserved",
               "every candidate has genuine recorded PASS/CORRECTED_PASS and no pending reason",
               "unknown exact model/version/confidence remain null"],
    "publication": "NOT_IMPORTED_OR_PUBLISHED", "development_database_writes": 0,
    "paid_api_calls": 0,
}
(ROOT / "final-audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
