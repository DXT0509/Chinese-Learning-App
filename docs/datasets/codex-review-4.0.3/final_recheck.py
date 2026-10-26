"""Four explicitly inspected findings from final reconciliation, not a review generator.

Preserve superseded evidence and increase even an already revised draft's version.
Run once from backend. Never accesses a database or AI provider.
"""
import json
from datetime import UTC, datetime
from shutil import copy2

from checkpoint import ROOT, SOURCE, read
from app.schemas.curated_vocabulary import CuratedRecord
from app.services.curated_import import digest, load_records, record_checksum

findings = [
    ("L5-B002", 19, "liùyù", "liúyù", None,
     "Final recheck caught initially missed 流域: liúyù, not liùyù. Full 黄河流域 conservation example and Vietnamese re-read; all other fields retained."),
    ("L5-B009", 47, "kuàliùyù", "kuàliúyù", None,
     "Final recheck caught initially missed 跨流域: kuàliúyù, not kuàliùyù. Full nearly-four-year water-transfer example and translation re-read."),
    ("L5-B019", 10, "húbō", "húpō", None,
     "Final recheck caught initially missed 湖泊: húpō, not húbō. Earlier 宛若 repair retained. Full crater-lake/Jade-Pool example and Vietnamese re-read."),
    ("L5-B023", 23, None, None, "thán tiêm duy",
     "Final dictionary recheck caught initially missed 碳 thán, not than, in Sino-Vietnamese. Earlier 模量 móliàng and modulus translation repairs retained; complete carbon-fiber example re-read."),
]

for batch, index, old, new, sino, note in findings:
    directory = ROOT / batch
    path = directory / "review-notes.json"
    notes = read(path)
    previous_hash = digest(path.read_bytes())
    _, records = load_records(directory / "deployment.jsonl")
    original = load_records(SOURCE / notes["source_file"])[1][index - 1]
    current = records[index - 1]
    finding = notes["records"][index - 1]
    assert current.lexical_key == original.lexical_key == finding["lexical_key"]
    payload = current.model_dump()
    if sino:
        assert payload["sino_vietnamese"] == "than tiêm duy"
        payload["sino_vietnamese"] = sino
    else:
        assert old in payload["examples"][0]["pinyin"]
        payload["examples"][0]["pinyin"] = payload["examples"][0]["pinyin"].replace(old, new)
    payload["content_version"] += 1
    revised = CuratedRecord.model_validate(payload)
    assert revised.lexical_key == current.lexical_key
    archive = ROOT / "superseded" / (batch + "-before-final-recheck")
    archive.mkdir(exist_ok=False)
    for filename in ("review-notes.json", "deployment.jsonl"):
        copy2(directory / filename, archive / filename)
    records[index - 1] = revised
    target = directory / "deployment.jsonl"
    target.write_text("\n".join(r.model_dump_json() for r in records) + "\n", encoding="utf-8")
    checksum, validated = load_records(target)
    assert validated[index - 1] == revised
    old_correction = finding["correction"]
    reason = (old_correction["reason"] + " " if old_correction else "") + note
    # Retain a complete source-to-final content diff, plus separate recheck history.
    changed = {k: v for k, v in revised.model_dump().items()
               if k != "content_version" and v != original.model_dump()[k]}
    finding.update(
        note=finding["note"] + " " + note,
        correction={"changes": changed, "reason": reason},
        linguistic_outcome="CORRECTED_PASS",
        reviewed_content_version=revised.content_version,
        reviewed_checksum=record_checksum(revised),
    )
    notes["deployment_sha256"] = checksum
    notes["checkpoint_written_at"] = datetime.now(UTC).isoformat()
    notes["supersedes_notes_sha256"] = previous_hash
    notes["recheck_note"] = note
    if sino:
        notes["supporting_sources"].append("https://hvdic.thivien.net/whv/%E7%A2%B3")
    path.write_text(json.dumps(notes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(batch, revised.lexical_key, "version", revised.content_version)
