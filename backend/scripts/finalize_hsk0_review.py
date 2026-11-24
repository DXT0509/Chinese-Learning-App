"""Correct and audit the existing pack; prepare real sign-off fields without granting approval."""

import argparse
import hashlib
from collections import Counter
from pathlib import Path
from uuid import uuid5

from app.core.pinyin import tone_marks
from app.schemas.roadmap_preparation import PreparationPlan, Review
from app.services.content_files import ContentError
from app.services.roadmap_preparation import (
    asset_reference_id,
    checksum,
    compile_drafts,
    generate,
    load_catalog,
    load_json,
    write_artifact,
)
from scripts.prepare_hsk0_pack import CATALOG, PACK

FINAL = PACK / "final-review-v4"
NU_TECHNIQUE = (
    "Trong chữ 好, nét ngang cuối của bộ 女 được viết thành nét hất (提), hướng lên bên phải."
)
EDUCATIONAL_SOURCES = {
    "我": ["https://zdic.net/hans/我", "https://hvdic.thivien.net/whv/我"],
    "你": ["https://zdic.net/hans/你", "https://hvdic.thivien.net/whv/你"],
    "好": ["https://zdic.net/hans/好", "https://hvdic.thivien.net/whv/好"],
    "writing": [
        "https://commons.wikimedia.org/wiki/File:好-order.gif",
        "https://r3-ndr.ykt.cbern.com.cn/edu_product/esp/assets_document/7ca54092-9f89-4e9f-9111-50b4578e69e9.pkg/pdf.pdf",
    ],
    "tone_sandhi": [
        "https://www.chineseclass101.com/lesson/taiwanese-mandarin-survival-phrases-4-basic-greetings?lp=122"
    ],
}


def corrected_plan():
    # Adopt exactly the frozen reviewed proposal, not a rerun of its earlier generator.
    bundle = load_json(PACK / "operator-review-bundle-v3.json")
    plan = PreparationPlan.model_validate(bundle["plan"])
    if checksum(bundle["definition"]) != bundle["manifest"]["definition_sha256"]:
        raise ContentError("v3 source bundle integrity mismatch")
    if plan.model_dump(mode="json") != load_json(PACK / "plan-v3.json"):
        raise ContentError("v3 plan differs from frozen review bundle")
    plan.version = 4
    hao = plan.enrichments[2]
    hao.components[0].explanation_vi += " " + NU_TECHNIQUE
    hao.components[
        1
    ].explanation_vi = "子 ở bên phải. Nhận diện phần 子 để ghi nhớ cấu trúc trái–phải của chữ 好; xem mẫu thứ tự nét khi tập viết."
    ni = plan.enrichments[1]
    ni.notes_vi = ni.notes_vi.replace(
        "Trong 你好, thanh đầu thường đổi khi nói; Pinyin từ điển vẫn ghi nǐ hǎo.",
        "Khi hai âm tiết thanh 3 đứng liền nhau, thanh 3 đầu được đọc như thanh 2: 你好 thường đọc ní hǎo. Pinyin từ điển vẫn ghi nǐ hǎo.",
    )
    return plan


def review_items(plan):
    """Children precede notes: notes bind the actual child review objects, not stale hashes."""
    for asset in plan.assets:
        yield f"asset:{asset.id}", "ASSET", asset, asset.review, {"review"}
    for extra in plan.enrichments:
        identifier = str(extra.reference.vocabulary_id)
        for index, component in enumerate(extra.components):
            yield (
                f"{identifier}:component:{index}",
                "COMPONENT",
                component,
                component.review,
                {"review"},
            )
        for index, example in enumerate(extra.examples):
            yield f"{identifier}:example:{index}", "EXAMPLE", example, example.review, {"review"}
        yield f"{identifier}:notes", "NOTES", extra, extra.notes_review, {"review", "notes_review"}


def bind_pending_reviews(plan):
    for location, _, item, review, excluded in review_items(plan):
        digest = checksum(item.model_dump(mode="json", exclude=excluded))
        if review.status == "REVIEWED":
            if review.content_sha256 != digest:
                raise ContentError(
                    f"{location}: stale signed review; obtain a new explicit approval"
                )
        else:
            # A proposed checksum is not a decision, name or evidence. Never refresh a signed hash.
            review.content_sha256 = digest
    return plan


def apply_signoffs(plan, form):
    """Apply explicit per-item approvals only; pending parents receive refreshed proposals."""
    rows = form["items"]
    by_location = {r["location"]: r for r in rows}
    expected = {location for location, *_ in review_items(plan)}
    if len(by_location) != len(rows) or set(by_location) != expected:
        raise ContentError("sign-off form must identify exactly the 17 review items once")
    if form["plan_sha256"] != checksum(plan.model_dump(mode="json")):
        raise ContentError("sign-off form belongs to a different exact plan")
    result = plan.model_copy(deep=True)
    for location, _, item, review, excluded in review_items(result):
        row = by_location[location]
        if row["decision"] != "APPROVED":
            if row["decision"] != "READY_FOR_APPROVAL":
                raise ContentError("resolve requested changes or blocked items before proceeding")
            continue
        signed = Review.model_validate(row["review"])
        digest = checksum(item.model_dump(mode="json", exclude=excluded))
        if signed.status != "REVIEWED" or signed.content_sha256 != digest:
            raise ContentError(
                f"{location}: approval must bind current content; notes follow children"
            )
        review.status, review.reviewer, review.evidence, review.content_sha256 = (
            signed.status,
            signed.reviewer,
            signed.evidence,
            signed.content_sha256,
        )
    return bind_pending_reviews(result)


def audit_assets(plan):
    receipts = {r["file"]: r for r in load_json(PACK / "sources/sources.json")}
    frozen = {
        a["id"]: {k: v for k, v in a.items() if k != "review"}
        for a in load_json(PACK / "operator-review-bundle-v3.json")["plan"]["assets"]
    }
    findings = []
    for asset in plan.assets:
        if asset.model_dump(mode="json", exclude={"review"}) != frozen.get(str(asset.id)):
            raise ContentError("asset identity/provenance changed from the frozen v3 source")
        row = receipts[Path(asset.file).name]
        raw = (PACK / asset.file).read_bytes()
        expected_license = (
            "https://creativecommons.org/licenses/by/2.0/fr/"
            if asset.purpose == "AUDIO"
            else "https://creativecommons.org/licenses/by/3.0/"
        )
        if (
            hashlib.sha256(raw).hexdigest() != asset.sha256
            or len(raw) != asset.byte_length
            or hashlib.sha1(raw).hexdigest() != row["upstream_sha1"]
            or asset.sha256 != row["sha256"]
            or asset.source != row["source"]
            or asset.license != row["license_url"]
            or asset.license != expected_license
            or not asset.attribution
            or not asset.redistribution_allowed
        ):
            raise ContentError(
                "asset bytes, provenance or selected license differs from reviewed source"
            )
        note = next(e.notes_vi for e in plan.enrichments if e.reference == asset.reference)
        if not all(value in note for value in (asset.attribution, asset.source, asset.license)):
            raise ContentError("visible notes must preserve complete asset attribution")
        findings.append(
            {
                "asset_id": str(asset.id),
                "lesson_asset_id": str(asset_reference_id(asset)),
                "file": asset.file,
                "sha256": asset.sha256,
                "reference": asset.reference.model_dump(mode="json"),
                "simplified": asset.simplified,
                "pinyin_numbered": asset.pinyin_numbered,
                "source": asset.source,
                "attribution": asset.attribution,
                "license": asset.license,
                "original_bytes_unchanged": True,
                "visible_attribution_present": True,
                "owner_inspection": {
                    "evidence_type": "USER_REPORTED_INSPECTION",
                    "report": "Product owner reports listening to the three OGG recordings and watching the three GIFs; all six appear satisfactory.",
                    "source": "User-supplied Phase 6.3B Final Educational Review request in this conversation",
                    "filename_association_only": True,
                    "owner_supplied_checksum": False,
                    "reviewer_identity": None,
                    "review_reference": None,
                    "formal_approval": False,
                    "independent_expert_verification": False,
                },
                "redistribution_requirements": [
                    "Preserve creator credit, source and license links",
                    "Retain unchanged-status notice; do not imply endorsement",
                    "Add no incompatible restrictions",
                ],
            }
        )
    return findings


def audit_vocabulary(plan, catalog):
    expected = [
        ("我", "wo3", "wǒ", "ngã", "tôi"),
        ("你", "ni3", "nǐ", "nhĩ", "bạn"),
        ("好", "hao3", "hǎo", "hảo", "tốt"),
    ]
    refs = [r for group in plan.groups for r in group.vocabulary]
    if len(refs) != 3:
        raise ContentError("expected the exact three-word first pack")
    rows = []
    for ref, (character, numbered, pinyin, sino, meaning) in zip(refs, expected, strict=True):
        word = catalog[ref.vocabulary_id]
        if (
            word.simplified,
            word.pinyin_numbered,
            word.pinyin,
            word.sino_vietnamese,
            word.vietnamese_meanings[0],
            word.content_version,
        ) != (character, numbered, pinyin, sino, meaning, ref.content_version):
            raise ContentError(
                "catalog lexical content differs; handle separately through catalog versioning"
            )
        extra = next(e for e in plan.enrichments if e.reference == ref)
        if len(extra.examples) != 1 or extra.examples[0].content not in word.examples:
            raise ContentError(
                "example differs from the selected catalog sentence; review separately"
            )
        rows.append(
            {
                "reference": ref.model_dump(mode="json"),
                "simplified": character,
                "pinyin": pinyin,
                "pinyin_numbered": numbered,
                "sino_vietnamese": sino,
                "meanings": word.vietnamese_meanings,
                "example": extra.examples[0].content.model_dump(mode="json"),
                "sources": EDUCATIONAL_SOURCES[character],
                "catalog_modification_required": False,
                "decision": "READY_FOR_APPROVAL",
            }
        )
    return rows


def audit_quizzes(definition, catalog):
    results = []
    introduced = []
    group_meanings = {
        catalog[r.vocabulary_id].vietnamese_meanings[0]
        for n in definition.nodes
        if n.node_type == "NEW_WORD"
        for r in n.lesson.vocabulary
    }
    for node in definition.nodes:
        if node.node_type == "NEW_WORD":
            introduced.extend(node.lesson.vocabulary)
        elif node.lesson.vocabulary != introduced:
            raise ContentError("review scope differs from immediately preceding group")
        for activity in node.lesson.activities:
            if activity.kind != "QUIZ":
                continue
            match = [
                (ref, kind)
                for ref in node.lesson.vocabulary
                for kind in ("PINYIN", "WORD_TO_MEANING", "MEANING_TO_WORD")
                if activity.id == uuid5(node.id, f"quiz:{ref.vocabulary_id}:{kind}")
            ]
            if len(match) != 1:
                raise ContentError("quiz target identity is ambiguous")
            ref, kind = match[0]
            word = catalog[ref.vocabulary_id]
            expected = (
                word.pinyin
                if kind == "PINYIN"
                else (word.vietnamese_meanings[0] if kind == "WORD_TO_MEANING" else word.simplified)
            )
            if (
                len(set(activity.options)) != len(activity.options)
                or activity.options.count(expected) != 1
                or activity.options[activity.correct_option] != expected
            ):
                raise ContentError("quiz answer is not the sole correct expected label")
            if kind == "PINYIN":
                allowed = {tone_marks(word.pinyin_numbered[:-1] + str(t)) for t in range(1, 5)}
            elif kind == "MEANING_TO_WORD":
                allowed = {catalog[r.vocabulary_id].simplified for r in node.lesson.vocabulary}
            else:
                allowed = {catalog[r.vocabulary_id].vietnamese_meanings[0] for r in introduced}
                # Existing NEW_WORD policy permits meaning distractors from this fixed group.
                allowed |= group_meanings
            if not set(activity.options) <= allowed:
                raise ContentError("quiz distractors violate the lesson/group policy")
            results.append(
                {
                    "activity_id": str(activity.id),
                    "node_type": node.node_type,
                    "target": ref.model_dump(mode="json"),
                    "template": kind,
                    "prompt": activity.prompt,
                    "options": activity.options,
                    "private_correct_index": activity.correct_option,
                    "correct_label": expected,
                    "single_correct_option": True,
                    "editorial_decision": "READY_FOR_APPROVAL",
                    "rationale": "Exact tone-marked citation reading"
                    if kind == "PINYIN"
                    else "Distinct meanings tôi/bạn/tốt; exact target identity, no synonyms among choices",
                }
            )
    if len(results) != 9:
        raise ContentError("expected all nine final quiz questions")
    return results


def prepare(plan, output):
    plan = bind_pending_reviews(plan.model_copy(deep=True))
    catalog = load_catalog([CATALOG])
    definition, quality, _ = compile_drafts(plan, catalog, PACK, operator_preview=True)
    errors = [
        i
        for i in quality.issues
        if i["severity"] == "ERROR" and i["code"] != "HUMAN_REVIEW_REQUIRED"
    ]
    if errors:
        raise ContentError("unresolved content-validation errors: " + str(errors))
    previous = load_json(PACK / "operator-review-bundle-v3.json")["definition"]
    if [(str(n.id), [str(a.id) for a in n.lesson.activities]) for n in definition.nodes] != [
        (n["id"], [a["id"] for a in n["lesson"]["activities"]]) for n in previous["nodes"]
    ]:
        raise ContentError("stable node/activity identities changed")
    if sum(len(n.lesson.activities) for n in definition.nodes) != 22:
        raise ContentError("the reviewed structure must retain 22 activities")
    vocabulary = audit_vocabulary(plan, catalog)
    assets = audit_assets(plan)
    quizzes = audit_quizzes(definition, catalog)
    items = []
    for location, category, item, review, excluded in review_items(plan):
        items.append(
            {
                "location": location,
                "category": category,
                "decision": "APPROVED" if review.status == "REVIEWED" else "READY_FOR_APPROVAL",
                "payload_sha256": checksum(item.model_dump(mode="json", exclude=excluded)),
                "review": review.model_dump(mode="json"),
                "proposed_decision": "ACCEPT",
                "analysis_by": "AI-assisted editorial and technical audit; not a human reviewer",
                "evidence": "asset-audit.json" if category == "ASSET" else "educational-audit.md",
            }
        )
    counts = Counter(i["decision"] for i in items)
    report = {
        "proposal_version": plan.version,
        "counts": {
            k: counts[k] for k in ("APPROVED", "READY_FOR_APPROVAL", "REQUEST_CHANGES", "BLOCKED")
        },
        "technical_content_validation_errors": 0,
        "pending_item_approval_gates": counts["READY_FOR_APPROVAL"],
        "overall_pack_approval": None,
        "development_write_authorization": None,
        "publication_ready": False,
        "development_published": False,
        "development_activated": False,
        "items": items,
    }
    write_artifact(output / "plan.json", plan.model_dump(mode="json"), immutable=True)
    write_artifact(output / "review-status.json", report, immutable=True)
    write_artifact(
        output / "signoff-form.json",
        {
            "plan_sha256": checksum(plan.model_dump(mode="json")),
            "reviewer_identity": None,
            "review_reference": None,
            "overall_decision": None,
            "items": items,
            "dependency_order": "Assets/components/examples first; refresh pending notes hashes after child review fields change; notes last.",
        },
        immutable=True,
    )
    all_reviewed = all(i["decision"] == "APPROVED" for i in items)
    generate(plan, catalog, PACK, output / "content", operator_preview=not all_reviewed)
    write_artifact(output / "asset-audit.json", assets, immutable=True)
    write_artifact(output / "vocabulary-audit.json", vocabulary, immutable=True)
    write_artifact(output / "quiz-audit.json", quizzes, immutable=True)
    write_artifact(
        output / "review-bindings.json",
        {
            "plan_sha256": checksum(plan.model_dump(mode="json")),
            "items": [{"location": i["location"], "sha256": i["payload_sha256"]} for i in items],
        },
        immutable=True,
    )
    write_artifact(
        output / "bundle.json",
        {
            "purpose": "OPERATOR_REVIEW_ONLY" if not all_reviewed else "ROADMAP_DRAFT_CANDIDATE",
            "publication_ready": False,
            "plan": plan.model_dump(mode="json"),
            "definition": definition.model_dump(mode="json"),
            "review_status": report,
            "manifest": load_json(output / "content/manifest.json"),
            "assets": load_json(output / "content/assets.json"),
        },
        immutable=True,
    )
    lines = [
        "# Version 4 educational audit — proposed decisions",
        "",
        "AI-assisted editorial audit; this is not a human approval. All 17 items need attributable sign-off.",
        "",
        "## Vocabulary and examples",
        "",
        "| Word | Pinyin | Hán Việt | Meanings | Example | Translation |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for word in vocabulary:
        example = word["example"]
        lines.append(
            f"| {word['simplified']} | {word['pinyin']} | {word['sino_vietnamese']} | {'; '.join(word['meanings'])} | {example['simplified']} / {example['pinyin']} | {example['vietnamese']} |"
        )
    lines += [
        "",
        "All three examples are short contextual illustrations from the pinned catalog. Other sentence words are not roadmap introduction targets. Pinyin retains citation tones; 很 is a degree word here, and 我很好 naturally means Tôi khỏe in this context. No catalog correction is proposed.",
        "",
        "## Five component explanations",
        "",
    ]
    for extra in plan.enrichments:
        for component in extra.components:
            lines += [
                f"- **{component.character} / {component.component} ({component.position}, {component.role})**: {component.explanation_vi}"
            ]
    lines += [
        "",
        "女's writing-technique sentence describes the final rising stroke in the existing 好 GIF. Radical identification and visible structure are retained; historical formation remains unavailable, with no verified etymology asserted. The old hint was removed from 子 to avoid assigning 女's technique to the wrong component.",
        "",
        "## Three educational notes",
        "",
    ]
    for extra in plan.enrichments:
        word = catalog[extra.reference.vocabulary_id]
        lines += [f"### {word.simplified}", "", extra.notes_vi, ""]
    lines += [
        "## Nine private quiz checks",
        "",
        "Operator-only answer keys below must not be served to learners.",
        "",
        "| Prompt | Choices (zero-based order) | Correct index | Correct label |",
        "| --- | --- | --- | --- |",
    ]
    for quiz in quizzes:
        lines.append(
            f"| {quiz['prompt']} | {' / '.join(quiz['options'])} | {quiz['private_correct_index']} | {quiz['correct_label']} |"
        )
    lines += [
        "",
        "Each question has one correct selected-sense answer. Tone alternatives contrast citation readings; hào is wrong for the selected 好/hǎo/tốt identity. New-word meaning distractors follow the existing fixed-group policy; they introduce no vocabulary references. REVIEW is after all three introductions and uses exactly 我/你/好. Learner API stripping is checked by the isolated HTTP rehearsal.",
        "",
        "## Supporting source references",
        "",
    ]
    for category, urls in EDUCATIONAL_SOURCES.items():
        lines += [
            f"- {category}: " + ", ".join(f"[source {i + 1}]({url})" for i, url in enumerate(urls))
        ]
    lines += [
        "",
        "The textbook search extract supports 女字旁's final rising stroke; the PDF could not be fully fetched by the web tool. The actual existing GIF frame sheet was inspected for compatibility with that explanation. No independent expert acoustic or stroke-order certification is claimed.",
        "",
    ]
    write_artifact(output / "educational-audit.md", "\n".join(lines), immutable=True)
    status_lines = [
        "# Version 4 sign-off status",
        "",
        *[f"- {name}: {count}" for name, count in report["counts"].items()],
        "",
        "Content validation errors: 0. Pending item approval gates are retained; publication is not authorized.",
        "",
        "| Item | Category | Status | Exact payload SHA-256 |",
        "| --- | --- | --- | --- |",
    ]
    status_lines += [
        f"| {i['location']} | {i['category']} | {i['decision']} | `{i['payload_sha256']}` |"
        for i in items
    ]
    write_artifact(output / "review-status.md", "\n".join(status_lines) + "\n", immutable=True)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--plan",
        type=Path,
        help="Actual operator-edited plan; signed hashes are validated, never invented",
    )
    parser.add_argument("--output", type=Path, default=FINAL)
    parser.add_argument(
        "--signoffs",
        type=Path,
        help="Apply only explicitly supplied attributable per-item approvals",
    )
    args = parser.parse_args()
    try:
        plan = (
            PreparationPlan.model_validate(load_json(args.plan)) if args.plan else corrected_plan()
        )
        if args.signoffs:
            plan = apply_signoffs(bind_pending_reviews(plan), load_json(args.signoffs))
        report = prepare(plan, args.output)
        print(report["counts"])
    except (ContentError, ValueError, OSError) as error:
        parser.exit(2, f"final review: {error}\n")


if __name__ == "__main__":
    main()
