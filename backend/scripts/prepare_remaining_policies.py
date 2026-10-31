"""Serialize recorded individual reviews against the saved checkpoint; never access a DB."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from uuid import UUID

from app.models.curated_vocabulary import CuratedVocabulary as Word
from app.schemas.curated_vocabulary import is_hanzi
from app.services.contextual_grammar import (
    EXPRESSION_OPTIONS,
    FUNCTION_OPTIONS,
    MORPHEME_OPTIONS,
    POLICY_VERSION,
    ContextualGrammar,
)
from app.services.policy_coverage import usable_cue
from app.services.policy_preparation import CatalogEntry
from app.services.review_targets import ReviewedPolicy
from scripts.phase41d_remaining_notes import NOTES
from scripts.prepare_review_policies import write_new

# These are contemporary fixed expressions/collocations. The source's broad
# idiom tag is retained in evidence, not asserted as a universally agreed 成语 label.
MODERN_EXPRESSIONS = {25, 31, 37, 40, 63, 84, 103, 106, 172, 212}
HANZI_CUES = {
    12: "Chữ thứ hai còn có nghĩa cuộc họp; ở đây nói về kỹ năng chưa biết làm.",
    13: "Cụm ba chữ chỉ việc không được phép.",
    16: "Chữ thứ hai là động từ có nghĩa là.",
    17: "Chữ thứ hai là động từ có nghĩa dùng.",
    19: "Chữ thứ hai còn xuất hiện trong từ chỉ năng lực; cụm gồm hai chữ.",
    20: "Chữ thứ hai là động từ có nghĩa muốn.",
    38: "Lời chào dùng đại từ ngôi thứ hai thông thường, không phải đại từ kính ngữ.",
    107: "Lời chào dùng đại từ ngôi thứ hai kính ngữ.",
}


def encode(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def prepare_remaining(checkpoint, previous):
    rows = checkpoint["records"]
    decisions = {}
    for line in NOTES.strip().splitlines():
        index, form, role, context, note = line.split("|", 4)
        index = int(index)
        if index in decisions or index >= len(rows):
            raise ValueError("Duplicate or unknown authored index")
        if rows[index]["source_payload"]["simplified"] != form:
            raise ValueError("Authored note does not match checkpoint identity")
        decisions[index] = (role, context, note)
    if set(decisions) != set(range(len(rows))) or len(rows) != 242:
        raise ValueError("Review must cover the complete 242-entry checkpoint")
    old = [ReviewedPolicy.model_validate(p) for p in previous]
    if [p.model_dump(mode="json") for p in old] != previous:
        raise ValueError("Existing policy payloads must remain byte-equivalent as JSON objects")
    policies, findings = [], []
    for index, row in enumerate(rows):
        source = row["source_payload"]
        role, context, note = decisions[index]
        word = Word(
            id=UUID(row["vocabulary_id"]),
            **{
                key: source[key]
                for key in (
                    "simplified",
                    "pinyin",
                    "pinyin_numbered",
                    "lexical_key",
                    "content_version",
                    "part_of_speech",
                    "sino_vietnamese",
                    "learning_level",
                )
            },
            checksum=row["checksum"],
        )
        if word.content_version != row["content_version"] or not row["published"]:
            raise ValueError("Checkpoint publication or version mismatch")
        if role in EXPRESSION_OPTIONS:
            assessment, category = "EXPRESSION_KIND", "expression"
            question = "Trong ngữ cảnh này, biểu thức trong ngoặc được dùng để làm gì?"
        elif role in MORPHEME_OPTIONS and role == "bound_morpheme":
            assessment, category = "MORPHEME_KIND", "bound_morpheme"
            question = (
                "Trong câu dưới đây, chữ trong ngoặc thuộc loại đơn vị nào? "
                "Chỉ xét cách dùng hiện đại trong câu này."
            )
        else:
            assessment = "GRAMMATICAL_FUNCTION" if role in FUNCTION_OPTIONS else "SYNTACTIC_ROLE"
            category = (
                "quantity_expression"
                if source["part_of_speech"] == "quantifier"
                else "idiom"
                if source["part_of_speech"] == "idiom" and index not in MODERN_EXPRESSIONS
                else "expression"
            )
            question = (
                "Trong câu dưới đây, phần trong ngoặc giữ chức năng ngữ pháp nào? "
                "Chỉ xét cách dùng trong câu, không xét từ loại từng chữ. "
                "Tân ngữ bao gồm cả tân ngữ của giới từ; vị ngữ bao gồm phần trung tâm vị ngữ."
            )
            if assessment == "GRAMMATICAL_FUNCTION":
                question = (
                    "Xét toàn bộ phần trong ngoặc, không xét từng chữ: "
                    "từ hoặc cụm từ này có chức năng tương đương nhóm nào? "
                    "Chọn từ loại chính của cả cụm, không chọn vị trí của cụm trong câu."
                )
        grammar = ContextualGrammar(
            lexical_category=category,
            assessment=assessment,
            source_part_of_speech=source["part_of_speech"],
            source_example=source["examples"][0]["simplified"],
            context_simplified=context,
            rationale=note,
            question_vi=question,
        )
        if context.count(word.simplified) != 1:
            raise ValueError("Authored assessment must mark exactly one lexical occurrence")
        glosses = source["vietnamese_meanings"]
        if any(is_hanzi(c) for gloss in glosses for c in gloss):
            raise ValueError("Source gloss would disclose Chinese before Hanzi")
        cue = usable_cue(CatalogEntry(word, glosses, True))
        prompt = (
            f"Viết mục từ đã học ({len(word.simplified)} chữ Hán). "
            + (f"Âm Hán-Việt «{word.sino_vietnamese}». " if cue else "")
            + "Nghĩa: "
            + "; ".join(glosses)
            + ". "
            + HANZI_CUES.get(index, "")
        )
        if not cue:
            translation = source["examples"][0]["vietnamese"]
            if any(is_hanzi(c) for c in translation):
                raise ValueError("Vietnamese source context contains Chinese")
            prompt += " Ngữ cảnh minh họa: " + translation
        policy = ReviewedPolicy(
            vocabulary_id=word.id,
            content_version=word.content_version,
            checksum=word.checksum,
            policy_version=POLICY_VERSION,
            sense_key="contextual-grammar-review-v1",
            vietnamese_prompt=prompt,
            reviewed_by="Codex session individual linguistic review 2026-10-28; no human approval",
            ambiguity_resolution=(
                "Exact catalog spelling and pronunciation only. Source lexical category and "
                "contextual syntactic function are distinct. New assessment context reviewed "
                "against the actual source meaning/example; its Chinese is disclosed only at "
                "the third stage after Hanzi/Pinyin. " + note
            ),
            accepted_pos=[role],
            grammatical_review=grammar,
        )
        policy.target(word)
        policies.append(policy)
        findings.append(
            {
                "vocabulary_id": str(word.id),
                "lexical_key": word.lexical_key,
                "content_version": word.content_version,
                "checksum": word.checksum,
                "source_part_of_speech": word.part_of_speech,
                "learning_level": word.learning_level,
                "lexical_category": category,
                "assessment": assessment,
                "accepted_functions": [role],
                "source_example": grammar.source_example,
                "assessment_context": context,
                "linguistic_finding": note,
                "decision": "POLICY_PREPARED",
                "pending_reasons": [],
                "published_metadata_changes": [],
            }
        )
    keys = lambda p: (p.vocabulary_id, p.content_version, p.checksum)
    if len({keys(p) for p in old + policies}) != len(old + policies):
        raise ValueError("New policy overlaps an existing identity")
    all_policies = sorted(old + policies, key=lambda p: str(p.vocabulary_id))
    report = {
        "reviewed_records": len(rows),
        "prepared": len(policies),
        "pending": [],
        "preserved_previous_policies": len(old),
        "proposed_policies": len(all_policies),
        "by_lexical_category": dict(Counter(r["lexical_category"] for r in findings)),
        "by_assessment": dict(Counter(r["assessment"] for r in findings)),
        "by_function": dict(Counter(p.accepted_pos[0] for p in policies)),
        "database_writes": 0,
        "published_metadata_changes": [],
        "records": findings,
    }
    return policies, all_policies, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--previous", required=True)
    parser.add_argument("--remaining-output", required=True)
    parser.add_argument("--final-output", required=True)
    parser.add_argument("--audit", required=True)
    args = parser.parse_args()
    checkpoint = json.loads(Path(args.checkpoint).read_text(encoding="utf-8"))
    previous = json.loads(Path(args.previous).read_text(encoding="utf-8"))
    policies, complete, report = prepare_remaining(checkpoint, previous)
    remaining = encode([p.model_dump(mode="json") for p in policies])
    final = encode([p.model_dump(mode="json") for p in complete])
    report["final_bundle_sha256"] = hashlib.sha256(final.encode()).hexdigest()
    report["checkpoint_sha256"] = hashlib.sha256(Path(args.checkpoint).read_bytes()).hexdigest()
    write_new(args.remaining_output, remaining)
    write_new(args.final_output, final)
    write_new(args.audit, encode(report))
    print(json.dumps({k: v for k, v in report.items() if k != "records"}))


if __name__ == "__main__":
    main()
