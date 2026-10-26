"""Prepare a NEW local deployment snapshot; never connects to a DB or AI provider.

Run from backend with its virtualenv. Historical source files are never modified.
"""

import argparse
import json
import shutil
from collections import Counter
from pathlib import Path

from app.services.curated_audit import scan_dataset
from app.services.curated_batch001 import convert_batch001
from app.services.curated_import import digest, load_records, record_checksum

KEY = "\u5395\u6240|ce4 suo3"
OLD_CHECKSUM = "8c34ca8ead7e0c31373c408222690ef5c49d9aefae83bb493870fad09cee71f6"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_rows(path, rows):
    path.write_text("\n".join(r.model_dump_json() for r in rows) + "\n", encoding="utf-8")


def prepare(source, destination):
    audit, _ = scan_dataset(source)
    if audit["structural_integrity"] != "PASSED":
        raise ValueError("Source integrity must pass")
    old = next(
        r
        for r in load_records(source / "level-0-batch-001.converted.jsonl")[1]
        if r.lexical_key == KEY
    )
    if record_checksum(old) != OLD_CHECKSUM:
        raise ValueError("Source conflict has changed; inspect a fresh database plan")
    source, destination = source.resolve(), destination.resolve()
    if (
        destination.exists()
        or destination.is_relative_to(source)
        or source.is_relative_to(destination)
    ):
        raise ValueError("Choose a new, separate snapshot directory")
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    slug = "level-0-batch-001"
    staging = destination / f"{slug}.jsonl"
    raw_rows = [
        json.loads(line)
        for line in staging.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    changed = 0
    for row in raw_rows:
        if any(f["text"] == old.simplified and f["script"] == "SIMPLIFIED" for f in row["forms"]):
            row["revision"] = 2
            row["supersedes_revision"] = 1
            row["review_status"] = "NEEDS_REVIEW"
            changed += 1
    if changed != 1:
        raise ValueError("Expected one historical source entry")
    staging.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in raw_rows)
        + "\n",
        encoding="utf-8",
    )
    converted, provenance = convert_batch001(staging)
    revised = next(r for r in converted if r.lexical_key == KEY)
    assert revised == old.model_copy(update={"content_version": 2, "review_status": "NEEDS_REVIEW"})
    write_rows(destination / f"{slug}.converted.jsonl", converted)
    write(destination / f"{slug}.provenance.json", provenance)
    manifest_path = destination / f"{slug}.manifest.json"
    manifest = read(manifest_path)
    manifest.update(
        artifact_sha256=digest(staging.read_bytes()),
        artifact_bytes=staging.stat().st_size,
        review_status_counts=dict(Counter(r["review_status"] for r in raw_rows)),
    )
    write(manifest_path, manifest)
    registry_path = destination / "lexical-key-registry.json"
    registry = read(registry_path)
    for entry in registry["entries"]:
        if entry["lexical_key"] == KEY:
            entry.update(content_version=2, checksum=record_checksum(revised))
    write(registry_path, registry)
    coverage_path = destination / "coverage-manifest.json"
    coverage = read(coverage_path)
    for batch in coverage["batches"]:
        if batch["batch_key"] == "L0-B001":
            batch["sha256"] = digest((destination / batch["artifact_file"]).read_bytes())
    write(coverage_path, coverage)
    request_path = destination / f"{slug}.review-input.jsonl"
    requests = [
        read_line
        for line in request_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
        for read_line in [json.loads(line)]
    ]
    by_key = {r.lexical_key: r for r in converted}
    for request in requests:
        r = by_key[request["content"]["lexical_key"]]
        if r.lexical_key == KEY:
            from app.services.curated_review import mechanical

            request.update(
                content=r.model_dump(),
                content_checksum=record_checksum(r),
                automated_validation=mechanical(r).model_dump(),
            )
    request_path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in requests) + "\n", encoding="utf-8"
    )
    write(
        destination / "deployment-amendment.json",
        {
            "operation": "Preserve existing editorial hold in a versioned local deployment snapshot",
            "lexical_key": KEY,
            "from_version": 1,
            "to_version": 2,
            "old_checksum": record_checksum(old),
            "new_checksum": record_checksum(revised),
            "new_status": "NEEDS_REVIEW",
            "linguistic_content_changed": False,
            "hold_resolved": False,
            "generator_claims_verified": False,
            "original_files": audit["files"],
        },
    )
    final, _ = scan_dataset(destination)
    write(destination / "deployment-audit.json", final)
    if final["structural_integrity"] != "PASSED":
        raise ValueError("Snapshot failed integrity; do not import it")
    print(
        json.dumps(
            {
                "integrity": "PASSED",
                "records": final["generated_records"],
                "holds": len(final["editorial_holds"]),
                "destination": str(destination),
            }
        )
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.source, args.destination)


if __name__ == "__main__":
    main()
