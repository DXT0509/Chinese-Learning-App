"""Persist explicitly written continuation notes/edits; no automatic linguistic decisions."""

import sys

from checkpoint import SOURCE, read, save

from app.services.curated_import import load_records


def rows(batch):
    manifest = read(SOURCE / "coverage-manifest.json")
    entry = next(b for b in manifest["batches"] if b["batch_key"] == batch)
    return load_records(SOURCE / entry["artifact_file"])[1]


def record(batch, notes, edits=(), pending=None, sources=None):
    originals = rows(batch)
    notes = {i: note for i, note in enumerate(notes.strip().splitlines(), 1)}
    corrections = {}
    for index, reason, changes in edits:
        changes = dict(changes)
        if "example" in changes:
            examples = [e.model_dump() for e in originals[index - 1].examples]
            examples[0].update(changes.pop("example"))
            changes["examples"] = examples
        if index in corrections:
            raise ValueError("Combine changes for one record explicitly")
        corrections[index] = {"reason": reason, "changes": changes}
    save(batch, notes, corrections=corrections, pending=pending, sources=sources)


if __name__ == "__main__":
    for i, row in enumerate(rows(sys.argv[1]), 1):
        print(i, "|".join([
            row.lexical_key, row.sino_vietnamese or "-", row.part_of_speech or "-",
            ";".join(row.vietnamese_meanings), ";".join(row.english_meanings),
        ]), " / ".join(" ~ ".join(e.model_dump().values()) for e in row.examples))
