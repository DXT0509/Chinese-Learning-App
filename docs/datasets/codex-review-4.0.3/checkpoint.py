"""Persist explicitly authored session notes, never synthesize ReviewResult approval.

Run from backend via the local virtualenv. No database or provider calls are made.
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid5

from app.schemas.curated_vocabulary import CuratedRecord
from app.services.curated_audit import scan_dataset
from app.services.curated_import import NAMESPACE, digest, load_records, record_checksum

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "original-zhvi"
ASPECTS = [
    "simplified_spelling",
    "mandarin_pinyin_tones",
    "vietnamese_meanings",
    "sino_vietnamese",
    "part_of_speech",
    "example_grammar_naturalness",
    "example_pinyin_translation",
    "learning_level",
    "duplicates_readings_ambiguity",
]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_new(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def save(batch_key, notes, *, corrections=None, pending=None, sources=None):
    """Every row needs an explicit note written AFTER the session reads its content."""
    corrections, pending = corrections or {}, pending or {}
    coverage = read(SOURCE / "coverage-manifest.json")
    batch = next(b for b in coverage["batches"] if b["batch_key"] == batch_key)
    sha, records = load_records(SOURCE / batch["artifact_file"])
    if set(notes) != set(range(1, len(records) + 1)):
        raise ValueError("Explicit per-record linguistic notes required; no default passing rows")
    if any(not isinstance(n, str) or not n.strip() for n in notes.values()):
        raise ValueError("Empty review note")
    directory = ROOT / batch_key
    directory.mkdir(exist_ok=False)
    output, findings = [], []
    for index, original in enumerate(records, 1):
        change = corrections.get(index)
        held = original.review_status == "NEEDS_REVIEW" or index in pending
        payload = original.model_dump()
        if change:
            payload.update(change["changes"])
            payload["content_version"] = original.content_version + 1
        if index in pending and original.review_status != "NEEDS_REVIEW":
            payload["review_status"] = "NEEDS_REVIEW"
            payload["content_version"] = original.content_version + 1
        revised = CuratedRecord.model_validate(payload)
        if revised.lexical_key != original.lexical_key:
            raise ValueError("Stable identities must be retained")
        output.append(revised)
        findings.append(
            {
                "lexical_key": original.lexical_key,
                "id": str(uuid5(NAMESPACE, original.lexical_key)),
                "source_content_version": original.content_version,
                "source_checksum": record_checksum(original),
                "reviewed_content_version": revised.content_version,
                "reviewed_checksum": record_checksum(revised),
                "linguistic_outcome": "UNCERTAIN"
                if pending.get(index, {}).get("linguistic_uncertainty")
                else "CORRECTED_PASS"
                if change
                else "PASS",
                "checked_aspects": ASPECTS,
                "note": notes[index],
                "correction": change,
                "pending_reason": pending.get(index, {}).get("reason")
                or ("Existing source editorial hold retained" if held else None),
                "local_development_candidate": not held,
                "eligible_for_AI_APPROVED": False,
                "approval_contract_blockers": [
                    "Exact session reviewer model snapshot/version not exposed",
                    "No numeric confidence supplied; threshold cannot be truthfully asserted",
                    "Generator identity remains an unverified historical claim",
                ],
                "evidence_limitations": [
                    "Session notes have no separate provider response receipt; the offline schema does not itself require such a receipt"
                ],
            }
        )
    target = directory / "deployment.jsonl"
    with target.open("x", encoding="utf-8") as stream:
        stream.write("\n".join(r.model_dump_json() for r in output) + "\n")
    target_sha, validated = load_records(target)
    assert len(validated) == len(records)
    write_new(
        directory / "review-notes.json",
        {
            "artifact_kind": "CODEX_SESSION_LINGUISTIC_NOTES_NOT_REVIEWRESULT",
            "batch": batch_key,
            "source_file": batch["artifact_file"],
            "source_sha256": sha,
            "deployment_sha256": target_sha,
            "checkpoint_written_at": datetime.now(UTC).isoformat(),
            "reviewer_label": "Codex session",
            "reviewer_model": None,
            "reviewer_version": None,
            "confidence": None,
            "paid_api_calls": 0,
            "strict_review_results_created": 0,
            "scope": "All record fields and complete examples read in the active session",
            "correction_review": "Corrected records re-read and assessed by this same session; no claim of a second independent model",
            "supporting_sources": sources or [],
            "records": findings,
        },
    )
    refresh()


def refresh():
    coverage = read(SOURCE / "coverage-manifest.json")
    complete = {p.parent.name: read(p) for p in ROOT.glob("L*-B*/review-notes.json")}
    rows = [r for v in complete.values() for r in v["records"]]
    completed = [b["batch_key"] for b in coverage["batches"] if b["batch_key"] in complete]
    next_batch = next(
        (b["batch_key"] for b in coverage["batches"] if b["batch_key"] not in complete), None
    )
    result = {
        "status": "LINGUISTIC_REVIEW_COMPLETE_WITH_RETAINED_HOLDS"
        if next_batch is None
        else "IN_PROGRESS",
        "total_source_records": 2501,
        "reviewed_records": len(rows),
        "passing_linguistic_review": sum(r["linguistic_outcome"] != "UNCERTAIN" for r in rows),
        "corrected_linguistic_records": sum(r["correction"] is not None for r in rows),
        "pending_editorial_or_linguistic": sum(r["pending_reason"] is not None for r in rows),
        "linguistically_uncertain": sum(r["linguistic_outcome"] == "UNCERTAIN" for r in rows),
        "local_development_candidates": sum(r["local_development_candidate"] for r in rows),
        "eligible_for_AI_APPROVED": 0,
        "blocked_by_approval_contract": len(rows),
        "approval_contract_scope": "Production zhvi-semantic-v1 only; not a local acceptance blocker",
        "local_approval_policy": "local-codex-session-v1",
        "local_confidence_threshold": None,
        "local_identity_evidence": "Recorded Codex session label; unknown exact model/version retained as null",
        "strict_review_results_created": 0,
        "rejected_records": 0,
        "paid_api_calls": 0,
        "database_writes": 0,
        "final_dataset_ready": next_batch is None,
        "completed_batches": completed,
        "next_unfinished_batch": next_batch,
        "unreviewed_records": 2501 - len(rows),
    }
    (ROOT / "progress.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    corrections = [
        {"batch": name, **r}
        for name, notes in complete.items()
        for r in notes["records"]
        if r["correction"] is not None
    ]
    pending = [
        {"batch": name, **r}
        for name, notes in complete.items()
        for r in notes["records"]
        if r["pending_reason"] is not None
    ]
    for name, values in (("corrections.json", corrections), ("pending.json", pending)):
        (ROOT / name).write_text(
            json.dumps(values, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(json.dumps(result))


def verify():
    """Validate a provisional complete catalog; unreviewed rows remain explicitly so."""
    audit, originals = scan_dataset(SOURCE)
    if audit["structural_integrity"] != "PASSED":
        raise ValueError("Source integrity failed")
    source_by_key = {r.lexical_key: r for r in originals}
    overlay = {}
    reviewed = {}
    files = []
    for notes_path in sorted(ROOT.glob("L*-B*/review-notes.json")):
        notes = read(notes_path)
        source = SOURCE / notes["source_file"]
        if digest(source.read_bytes()) != notes["source_sha256"]:
            raise ValueError("Source changed since semantic review")
        target = notes_path.parent / "deployment.jsonl"
        sha, rows = load_records(target)
        if sha != notes["deployment_sha256"]:
            raise ValueError("Reviewed deployment bytes changed")
        findings = {r["lexical_key"]: r for r in notes["records"]}
        if len(rows) != len(findings):
            raise ValueError("Incomplete checkpoint")
        for row in rows:
            finding = findings[row.lexical_key]
            if (
                record_checksum(row) != finding["reviewed_checksum"]
                or record_checksum(source_by_key[row.lexical_key]) != finding["source_checksum"]
            ):
                raise ValueError("Stale session review notes")
            if row.lexical_key in overlay:
                raise ValueError("Duplicate reviewed identity")
            overlay[row.lexical_key] = row
            reviewed[row.lexical_key] = finding
        files.append(
            {
                "batch": notes["batch"],
                "source_sha256": notes["source_sha256"],
                "deployment_sha256": sha,
                "records": len(rows),
            }
        )
    combined = [overlay.get(r.lexical_key, r) for r in originals]
    if (
        len({r.lexical_key for r in combined}) != 2501
        or len({r.simplified for r in combined}) != 2500
    ):
        raise ValueError("Global identity count changed")
    if len({(r.simplified, r.pinyin_numbered) for r in combined}) != 2501:
        raise ValueError("Global pronunciation identity duplicates")
    target = ROOT / "provisional-deployment.jsonl"
    with target.open("w", encoding="utf-8") as stream:
        stream.write("\n".join(r.model_dump_json() for r in combined) + "\n")
    sha, rows = load_records(target)
    result = {
        "status": "PROVISIONAL_NOT_FULLY_REVIEWED" if len(reviewed) != len(rows)
        else "REVIEW_COMPLETE_WITH_RETAINED_HOLDS",
        "structural_integrity": "PASSED",
        "records": len(rows),
        "unique_learning_items": len({r.simplified for r in rows}),
        "duplicate_keys": [],
        "duplicate_simplified_pinyin_identities": [],
        "reviewed_records": len(reviewed),
        "unreviewed_records": len(rows) - len(reviewed),
        "deployment_file": target.name,
        "deployment_sha256": sha,
        "source_audit": audit,
        "reviewed_batches": files,
        "missing_examples": [r.lexical_key for r in combined if not r.examples],
        "hold_keys": [r.lexical_key for r in combined if r.review_status == "NEEDS_REVIEW"],
        "versions_changed": [
            r.lexical_key
            for r in combined
            if r.content_version != source_by_key[r.lexical_key].content_version
        ],
        "publication": "NONE; held records remain in the complete catalog"
        if len(reviewed) == len(rows)
        else "NONE; this file contains unreviewed and held records",
    }
    (ROOT / "validation.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                k: v
                for k, v in result.items()
                if k not in {"source_audit", "reviewed_batches", "versions_changed"}
            }
        )
    )
    return audit, combined


if __name__ == "__main__":
    refresh()
    verify()
