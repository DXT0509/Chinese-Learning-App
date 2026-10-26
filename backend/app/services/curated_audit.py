"""Read-only global audit. Manifest claims are compared with source bytes, never trusted."""

import json
from collections import Counter, defaultdict
from pathlib import Path
from uuid import uuid5

from app.schemas.curated_review import ReviewInput
from app.services.curated_batch001 import convert_batch001
from app.services.curated_import import NAMESPACE, digest, load_records, record_checksum
from app.services.curated_review import load_exchange, mechanical


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def local_file(root, name):
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Artifact must stay inside dataset directory")
    return path


def scan_dataset(root: Path):
    coverage = read_json(root / "coverage-manifest.json")
    registry = read_json(root / "lexical-key-registry.json")
    errors, batches, all_records, actual_registry = [], [], [], []
    provenance = []
    expected_names = {
        f"level-{level}-batch-{number:03d}.manifest.json"
        for level, count in enumerate((2, 2, 3, 6, 12, 25))
        for number in range(1, count + 1)
    }
    if {p.name for p in root.glob("*.manifest.json")} != expected_names:
        errors.append("Expected exactly the 50 level/batch manifests")
    listed = coverage["batches"]
    if len(listed) != 50 or len({b["batch_key"] for b in listed}) != 50:
        errors.append("Coverage must list 50 distinct batches")
    for batch in listed:
        slug = f"level-{batch['level']}-batch-{batch['batch_number']:03d}"
        try:
            manifest = read_json(root / f"{slug}.manifest.json")
            path = local_file(root, batch["artifact_file"])
            sha, records = load_records(path)  # The actual repository validator.
            source = local_file(root, manifest["artifact_file"])
            if digest(source.read_bytes()) != manifest["artifact_sha256"]:
                raise ValueError("Manifest source hash mismatch")
            if source.stat().st_size != manifest["artifact_bytes"]:
                raise ValueError("Manifest source size mismatch")
            if batch.get("sha256") and batch["sha256"] != sha:
                raise ValueError("Coverage hash mismatch")
            if manifest["batch_key"] != batch["batch_key"]:
                raise ValueError("Batch identity mismatch")
            if batch["records_count"] != len(records):
                raise ValueError("Coverage record count mismatch")
            if batch["unique_words"] != len({r.simplified for r in records}):
                raise ValueError("Coverage unique word count mismatch")
            if any(r.learning_level != batch["level"] for r in records):
                raise ValueError("Wrong learning level")
            if batch["batch_key"] == "L0-B001":
                converted, mapping = convert_batch001(source)
                if [r.model_dump() for r in converted] != [r.model_dump() for r in records]:
                    raise ValueError("Historical Batch 001 conversion mismatch")
                if mapping != read_json(root / f"{slug}.provenance.json"):
                    raise ValueError("Historical conversion mappings mismatch")
                original_keys = [m["source_key"] for m in mapping["mappings"]]
                if set(original_keys) != set(manifest["lexical_keys"]):
                    raise ValueError("Historical identifiers mismatch")
            for r in records:
                actual_registry.append(
                    {
                        "id": str(uuid5(NAMESPACE, r.lexical_key)),
                        "lexical_key": r.lexical_key,
                        "simplified": r.simplified,
                        "pinyin_numbered": r.pinyin_numbered,
                        "learning_level": r.learning_level,
                        "batch_key": batch["batch_key"],
                        "content_version": r.content_version,
                        "checksum": record_checksum(r),
                    }
                )
            if "records" in manifest:
                for expected, actual in zip(
                    manifest["records"], actual_registry[-len(records) :], strict=True
                ):
                    if any(actual.get(k) != v for k, v in expected.items()):
                        raise ValueError("Per-record manifest mismatch")
            requests = load_exchange(root / f"{slug}.review-input.jsonl", ReviewInput)
            if len(requests) != len(records):
                raise ValueError("Review input count mismatch")
            for request, record in zip(requests, records, strict=True):
                if (
                    request.content != record
                    or request.content_checksum != record_checksum(record)
                    or request.automated_validation != mechanical(record)
                ):
                    raise ValueError("Review input does not match source")
            provenance.append(
                {
                    "batch": batch["batch_key"],
                    "claimed_generator": requests[0].generator.model_dump(),
                    "status": "UNVERIFIED_MANIFEST_ASSERTION",
                    "reason": "No provider generation receipt is established by manifests or review inputs",
                }
            )
            batches.append(
                {
                    "batch": batch["batch_key"],
                    "file": path.name,
                    "sha256": sha,
                    "source_sha256": manifest["artifact_sha256"],
                    "records": len(records),
                    "structurally_valid": True,
                }
            )
            all_records.extend(records)
        except (ValueError, KeyError, OSError, TypeError) as exc:
            errors.append(
                {
                    "batch": batch["batch_key"],
                    "error": type(exc).__name__,
                    "reason": str(exc) if type(exc) is ValueError else "Invalid artifact",
                }
            )
    if registry["entries"] != actual_registry:
        expected = {e["lexical_key"]: e for e in registry["entries"]}
        actual = {e["lexical_key"]: e for e in actual_registry}
        errors.append(
            {
                "registry_mismatch": sorted(
                    k for k in expected.keys() | actual.keys() if expected.get(k) != actual.get(k)
                )
            }
        )
    keys = Counter(r.lexical_key for r in all_records)
    identities = Counter((r.simplified, r.pinyin_numbered) for r in all_records)
    duplicate_keys = [k for k, n in keys.items() if n > 1]
    duplicate_identities = [list(k) for k, n in identities.items() if n > 1]
    if duplicate_keys or duplicate_identities:
        errors.append("Duplicate global lexical identity")
    levels = {
        str(i): len({r.simplified for r in all_records if r.learning_level == i}) for i in range(6)
    }
    if levels != coverage["target_distribution"] or levels != coverage["current_distribution"]:
        errors.append("Learning level distribution mismatch")
    unique = len({r.simplified for r in all_records})
    if (
        unique != coverage["current_total_unique_items"]
        or unique != 2500
        or len(all_records) != 2501
        or registry["total_records"] != len(all_records)
        or registry["total_unique_lexical_words"] != unique
        or registry["namespace_uuid"] != str(NAMESPACE)
    ):
        errors.append("Global counts or namespace mismatch")
    groups = defaultdict(set)
    for r in all_records:
        groups[("form", r.simplified)].add(r.lexical_key)
        for meaning in r.vietnamese_meanings:
            groups[("exact_vi_gloss", meaning.casefold())].add(r.lexical_key)
    candidates = [
        {"kind": k[0], "value": k[1], "lexical_keys": sorted(v)}
        for k, v in groups.items()
        if len(v) > 1
    ]
    report = {
        "schema_version": 1,
        "structural_integrity": "FAILED" if errors else "PASSED",
        "errors": errors,
        "files": batches,
        "generated_records": len(all_records),
        "unique_learning_items": unique,
        "by_learning_level": levels,
        "records_by_level": dict(
            sorted(Counter(str(r.learning_level) for r in all_records).items())
        ),
        "duplicate_keys": duplicate_keys,
        "duplicate_identities": duplicate_identities,
        "duplicate_candidates": candidates,
        "duplicate_candidate_scope": "Exact form and Vietnamese gloss heuristics; semantic review pending",
        "missing_content": [r.lexical_key for r in all_records if not r.examples],
        "editorial_holds": [
            r.lexical_key for r in all_records if r.review_status == "NEEDS_REVIEW"
        ],
        "generator_provenance": provenance,
        "provenance_evidence": {
            "generator_helper": "generator_core.py",
            "generator_helper_sha256": digest((root / "generator_core.py").read_bytes())
            if (root / "generator_core.py").exists()
            else None,
            "finding": "Repository generator accepts supplied content and has default provider/model/version strings; this does not prove a provider invocation",
            "review_execution": "BLOCKED_UNTIL_BYTE_BOUND_GENERATOR_PROVENANCE_IS_VERIFIED",
        },
        "stages": {
            "GENERATED": len(all_records),
            "STRUCTURALLY_VALIDATED": len(all_records),
            "IMPORTED": None,
            "AI_REVIEWED": None,
            "AI_APPROVED": None,
            "PUBLISHED": None,
        },
    }
    return report, all_records
