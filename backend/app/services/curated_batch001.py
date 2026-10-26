"""Explicit Batch 001 adapter. Originals and editorial holds are never rewritten."""

import json

from app.core.pinyin import tone_marks
from app.schemas.curated_vocabulary import CuratedRecord
from app.services.curated_import import digest


def convert_batch001(path):
    payload = path.read_bytes()
    rows = [json.loads(line) for line in payload.decode("utf-8").splitlines() if line.strip()]
    converted, provenance = [], []
    for row in rows:
        forms = [f for f in row["forms"] if f["script"] == "SIMPLIFIED" and f["primary"]]
        if len(forms) != 1 or row["review_status"] not in {"GENERATED_UNREVIEWED", "NEEDS_REVIEW"}:
            raise ValueError("Unsupported staging entry")
        for reading in row["readings"]:
            canonical_pinyin = tone_marks(reading["pinyin_numbered"])
            if (
                canonical_pinyin.replace(" ", "").casefold()
                != reading["pinyin"].replace(" ", "").casefold()
            ):
                raise ValueError("Staging Pinyin forms disagree")
            senses = [s for s in row["senses"] if reading["key"] in s["reading_keys"]]
            if not senses:
                raise ValueError("Reading without senses")
            record = CuratedRecord(
                schema_version=1,
                lexical_key=f"{forms[0]['text']}|{reading['pinyin_numbered']}",
                simplified=forms[0]["text"],
                pinyin=canonical_pinyin,
                pinyin_numbered=reading["pinyin_numbered"],
                sino_vietnamese=reading["sino_vietnamese"],
                part_of_speech=senses[0]["part_of_speech"],
                learning_level=row["classification"]["learning_level"],
                review_status="NEEDS_REVIEW" if row["review_issues"] else row["review_status"],
                content_version=row["revision"],
                vietnamese_meanings=list(
                    dict.fromkeys(m for s in senses for m in s["meanings_vi"])
                ),
                english_meanings=list(dict.fromkeys(m for s in senses for m in s["meanings_en"])),
                examples=[
                    {
                        "simplified": e["chinese"],
                        "pinyin": e["pinyin"],
                        "vietnamese": e["vietnamese"],
                    }
                    for e in row["examples"]
                    if e["reading_key"] == reading["key"]
                ],
            )
            converted.append(record)
            provenance.append(
                {
                    "source_key": row["key"],
                    "source_reading": reading["key"],
                    "lexical_key": record.lexical_key,
                    "source_record": row,
                }
            )
    if len({r.lexical_key for r in converted}) != len(converted):
        raise ValueError("Duplicate converted identities")
    return converted, {"source_sha256": digest(payload), "mappings": provenance}
