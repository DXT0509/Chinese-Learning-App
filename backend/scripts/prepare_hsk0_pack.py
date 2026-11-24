"""Prepare the small HSK 0 review packet without asserting human educational approval."""

import argparse
from pathlib import Path
from uuid import UUID, uuid5

from app.schemas.roadmap_preparation import PreparationPlan
from app.services.roadmap_preparation import (
    checksum,
    compile_drafts,
    generate,
    load_catalog,
    load_json,
    write_artifact,
)

HERE = Path(__file__).resolve().parents[1]
PACK = HERE / "content/roadmaps/preparation/hsk-0-pack"
REVIEW_DIR = PACK / "review-preview-v3"
CATALOG = HERE.parent / "docs/datasets/original-zhvi/level-0-batch-001.converted.jsonl"


def build_plan():
    plan = load_json(HERE / "content/roadmaps/preparation/hsk-0.plan.json")
    plan.update(version=3, title="HSK 0 — Tôi, bạn và tốt")
    plan["templates"] = {
        "quizzes": ["PINYIN", "WORD_TO_MEANING"],
        "review_quizzes": ["MEANING_TO_WORD"],
        "pinyin_tone_distractors": True,
        "components_activity": False,
        "review_introduction_required": False,
        "pronunciation_repetitions": 2,
    }
    refs = plan["groups"][0]["vocabulary"]
    characters = ["我", "你", "好"]
    stems = ["wo", "ni", "hao"]
    # New original Vietnamese explanations describe visible structure, not historical invention.
    components = [
        [
            (
                "戈",
                "OVERLAPPING",
                "STRUCTURAL",
                "Có thể nhận diện phần 戈 trong hình chữ; đây cũng là bộ dùng để tra chữ. Không suy ra nghĩa ‘tôi’ bằng cách cộng nghĩa các nét hoặc thành phần.",
            )
        ],
        [
            (
                "亻",
                "LEFT",
                "SEMANTIC_RADICAL",
                "亻 là dạng đứng bên trái của 人 và là bộ tra chữ 你; gợi liên hệ với người. Không phải mọi thành phần đều góp nghĩa trực tiếp.",
            ),
            (
                "尔",
                "RIGHT",
                "STRUCTURAL",
                "Phần bên phải được viết là 尔. Chỉ dùng để nhận diện cấu trúc ở bài này; không đọc 你 theo cách đọc hiện đại của 尔.",
            ),
        ],
        [
            (
                "女",
                "LEFT",
                "SEMANTIC_RADICAL",
                "女 ở bên trái và là bộ tra chữ 好. Nhận diện vị trí của bộ; không suy diễn một câu chuyện lịch sử hay quan niệm về con người từ nghĩa hiện đại.",
            ),
            (
                "子",
                "RIGHT",
                "STRUCTURAL",
                "子 ở bên phải. Khi viết trong 好, chú ý nét cuối của phần 女 nối hướng sang phải; xem mẫu thứ tự nét.",
            ),
        ],
    ]
    examples = [
        ("我在家。", "Wǒ zài jiā.", "wo3 zai4 jia1", "Tôi ở nhà.", 0),
        ("你喝茶吗？", "Nǐ hē chá ma?", "ni3 he1 cha2 ma5", "Bạn có uống trà không?", 0),
        ("我很好。", "Wǒ hěn hǎo.", "wo3 hen3 hao3", "Tôi khỏe.", 2),
    ]
    notes = [
        "我 dùng để nói về bản thân: tôi, mình. wǒ có thanh 3; khi đọc riêng, nghe và nhắc lại mẫu. Âm Hán Việt ‘ngã’ không phải cách phát âm Quan thoại.",
        "你 dùng để gọi người đang nói chuyện với mình: bạn, cậu. nǐ có thanh 3. Trong 你好, thanh đầu thường đổi khi nói; Pinyin từ điển vẫn ghi nǐ hǎo. Mẫu âm ở bài này là nǐ đọc riêng.",
        "Bài này học 好 đọc hǎo (thanh 3): tốt, ổn; trong 我很好 có thể hiểu là khỏe. Không nhầm với cách đọc hào (thanh 4, nghĩa thích) thuộc một cách đọc/nghĩa khác. Ví dụ ghi thanh từ điển, không phải hướng dẫn chi tiết biến điệu.",
    ]
    plan["enrichments"] = []
    for index, ref in enumerate(refs):
        chinese, pinyin, numbered, vi, offset = examples[index]
        plan["enrichments"].append(
            {
                "reference": ref,
                "components": [
                    {
                        "character_position": 0,
                        "character": characters[index],
                        "component": component,
                        "position": position,
                        "role": role,
                        "explanation_vi": explanation,
                        "interpretation": "ORIGIN_UNAVAILABLE",
                    }
                    for component, position, role, explanation in components[index]
                ],
                "examples": [
                    {
                        "content": {"simplified": chinese, "pinyin": pinyin, "vietnamese": vi},
                        "pinyin_numbered": numbered,
                        "target_character_position": offset,
                        "difficulty": 0,
                    }
                ],
                "notes_vi": notes[index],
            }
        )
    sources = {row["file"]: row for row in load_json(PACK / "sources/sources.json")}
    plan["assets"] = []
    for index, ref in enumerate(refs):
        for suffix, purpose in (("ogg", "AUDIO"), ("gif", "STROKE_ORDER")):
            row = sources[f"{stems[index]}.{suffix}"]
            creator = (
                "Wei Gao, Vion Nicolas — The Shtooka Project"
                if suffix == "ogg"
                else (
                    "Micheletb, Yug — Wikimedia Commons CJK Stroke Order Project"
                    if index == 0
                    else "Wikic — Wikimedia Commons CJK Stroke Order Project"
                )
            )
            plan["assets"].append(
                {
                    "id": str(uuid5(UUID(plan["id"]), "commons:" + row["title"])),
                    "version": 1,
                    "purpose": purpose,
                    "reference": ref,
                    "simplified": characters[index],
                    "pinyin_numbered": ["wo3", "ni3", "hao3"][index] if suffix == "ogg" else None,
                    "file": "sources/" + row["file"],
                    "sha256": row["sha256"],
                    "byte_length": row["byte_length"],
                    "media_type": row["media_type"],
                    "source": row["source"],
                    "attribution": creator + "; original bytes, no changes",
                    "license": row["license_url"],
                    "redistribution_allowed": True,
                    "origin": "HUMAN_RECORDED" if suffix == "ogg" else "DATASET",
                }
            )
    for enrichment in plan["enrichments"]:
        credits = [
            f"{asset['attribution']}. Nguồn: {asset['source']}. Giấy phép: {asset['license']}."
            for asset in plan["assets"]
            if asset["reference"] == enrichment["reference"]
        ]
        enrichment["notes_vi"] += "\n\nGhi công tư liệu:\n" + "\n".join(credits)
    return PreparationPlan.model_validate(plan)


def audit_original(plan, catalog):
    original = load_json(HERE / "content/roadmaps/preparation/hsk-0-v1/roadmap.json")
    optimized, _, _ = compile_drafts(plan, catalog, PACK, operator_preview=True)
    retained = {str(a.id): a for n in optimized.nodes for a in n.lesson.activities}
    findings = []
    for node in original["nodes"]:
        for activity in node["lesson"]["activities"]:
            kept = retained.get(activity["id"])
            if kept:
                decision = "OPTIONAL" if not kept.required else "KEEP"
                reason = (
                    "Informational group introduction; quizzes own completion."
                    if not kept.required
                    else "Recall the same syllable with contrasting tone marks."
                    if activity["kind"] == "QUIZ" and "Pinyin" in activity["prompt"]
                    else "Concise meaning recall or essential participation."
                )
            else:
                decision, reason = (
                    "REMOVE",
                    "Redundant recognition; reverse recall is retained in the group review.",
                )
            findings.append(
                {
                    "id": activity["id"],
                    "node": node["title"],
                    "kind": activity["kind"],
                    "prompt": activity["prompt"],
                    "options": activity["options"],
                    "decision": decision,
                    "reason": reason,
                    "answer_key_valid": activity["kind"] != "QUIZ"
                    or (
                        0 <= activity["correct_option"] < len(activity["options"])
                        and len(set(activity["options"])) == len(activity["options"])
                    ),
                    "human_review": "PENDING",
                }
            )
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    plan = build_plan()
    catalog = load_catalog([CATALOG])
    write_artifact(PACK / "plan-v3.json", plan.model_dump(mode="json"), immutable=True)
    write_artifact(PACK / "activity-audit.json", audit_original(plan, catalog), immutable=True)
    # Actual reviewed release generation must use the normal compiler after real approval.
    _, report = generate(plan, catalog, PACK, REVIEW_DIR, operator_preview=True)
    generate(plan, catalog, PACK, PACK / "draft-v3")
    definition, _, _ = compile_drafts(plan, catalog, PACK, operator_preview=True)
    release_id = uuid5(definition.id, str(definition.version))
    payloads = []
    for node in definition.nodes:
        public = node.model_dump(mode="json")
        for activity in public["lesson"]["activities"]:
            activity.pop("correct_option", None)
        words = []
        for ref in node.lesson.vocabulary:
            word = catalog[ref.vocabulary_id]
            words.append(
                {
                    "vocabulary_id": str(ref.vocabulary_id),
                    "content_version": ref.content_version,
                    **word.model_dump(
                        include={
                            "simplified",
                            "pinyin",
                            "pinyin_numbered",
                            "sino_vietnamese",
                            "vietnamese_meanings",
                            "examples",
                        }
                    ),
                }
            )
        payloads.append(
            {
                "node_version_id": str(uuid5(release_id, str(node.id))),
                "lesson_version_id": str(uuid5(release_id, f"lesson:{node.id}")),
                "definition": public,
                "vocabulary": words,
            }
        )
    write_artifact(PACK / "android-payloads-v3.json", payloads, immutable=True)
    write_artifact(
        PACK / "operator-review-bundle-v3.json",
        {
            "purpose": "OPERATOR_REVIEW_ONLY",
            "publication_ready": False,
            "human_approval": None,
            "plan": plan.model_dump(mode="json"),
            "definition": definition.model_dump(mode="json"),
            "manifest": load_json(REVIEW_DIR / "manifest.json"),
            "quality": report.payload(),
            "assets": load_json(REVIEW_DIR / "assets.json"),
        },
        immutable=True,
    )
    write_artifact(
        PACK / "quiz-quality-v3.json",
        {
            "purpose": "PRIVATE_OPERATOR_AUDIT",
            "human_approval": None,
            "questions": [
                {
                    "node": node.title,
                    "activity_id": str(activity.id),
                    "prompt": activity.prompt,
                    "choices": activity.options,
                    "server_correct_index": activity.correct_option,
                    "correct_label": activity.options[activity.correct_option],
                    "distinct_options": len(activity.options) == len(set(activity.options)),
                    "learner_key_removed": True,
                }
                for node in definition.nodes
                for activity in node.lesson.activities
                if activity.kind == "QUIZ"
            ],
        },
        immutable=True,
    )
    write_artifact(HERE.parent / "android/app/src/test/resources/hsk0-lessons.json", payloads)
    write_artifact(
        HERE.parent / "android/app/src/androidTest/assets/hsk0-lessons.json",
        payloads,
    )
    review_items = []
    for asset in plan.assets:
        review_items.append(
            {
                "location": f"asset:{asset.id}",
                "sha256": checksum(asset.model_dump(mode="json", exclude={"review"})),
            }
        )
    for extra in plan.enrichments:
        for i, component in enumerate(extra.components):
            review_items.append(
                {
                    "location": f"{extra.reference.vocabulary_id}:component:{i}",
                    "sha256": checksum(component.model_dump(mode="json", exclude={"review"})),
                }
            )
        for i, example in enumerate(extra.examples):
            review_items.append(
                {
                    "location": f"{extra.reference.vocabulary_id}:example:{i}",
                    "sha256": checksum(example.model_dump(mode="json", exclude={"review"})),
                }
            )
        review_items.append(
            {
                "location": f"{extra.reference.vocabulary_id}:notes",
                "sha256": checksum(
                    extra.model_dump(mode="json", exclude={"review", "notes_review"})
                ),
            }
        )
    write_artifact(
        PACK / "review-bindings-v3.json",
        {"human_approval": None, "items": review_items},
        immutable=True,
    )
    print(
        f"Prepared private review packet; {report.payload()['counts']['ERROR']} pending review gates; not publication ready"
    )


if __name__ == "__main__":
    main()
