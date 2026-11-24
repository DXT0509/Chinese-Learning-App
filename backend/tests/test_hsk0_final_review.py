"""Exact corrected drafts and honest approval dependency handling; no development writes."""

import pytest

from app.schemas.roadmap_preparation import Review
from app.services.content_files import ContentError
from app.services.roadmap_preparation import checksum, load_catalog, load_json
from scripts.finalize_hsk0_review import (
    NU_TECHNIQUE,
    audit_assets,
    audit_quizzes,
    bind_pending_reviews,
    corrected_plan,
    prepare,
    review_items,
)
from scripts.prepare_hsk0_pack import CATALOG, PACK


def test_corrections_preserve_frozen_v3_and_asset_bytes(tmp_path):
    old = load_json(PACK / "operator-review-bundle-v3.json")
    plan = corrected_plan()
    assert plan.version == 4
    assert NU_TECHNIQUE in plan.enrichments[2].components[0].explanation_vi
    assert "女" not in plan.enrichments[2].components[1].explanation_vi
    assert "ní hǎo" in plan.enrichments[1].notes_vi
    assert [a.model_dump(mode="json") for a in plan.assets] == old["plan"]["assets"]
    assert load_json(PACK / "operator-review-bundle-v3.json") == old
    report = prepare(plan, tmp_path)
    assert report["counts"] == {
        "APPROVED": 0,
        "READY_FOR_APPROVAL": 17,
        "REQUEST_CHANGES": 0,
        "BLOCKED": 0,
    }
    assert report["technical_content_validation_errors"] == 0
    assert not report["publication_ready"] and not report["development_published"]
    assert len(load_json(tmp_path / "bundle.json")["definition"]["nodes"]) == 4
    assert all(
        i["review"]["status"] == "UNREVIEWED" and i["review"]["reviewer"] is None
        for i in report["items"]
    )
    assert len(load_json(tmp_path / "quiz-audit.json")) == 9


def test_notes_hashes_refresh_after_child_reviews_and_signed_stale_content_is_refused():
    plan = bind_pending_reviews(corrected_plan())
    extra = plan.enrichments[2]
    initial = extra.notes_review.content_sha256
    child = extra.components[0]
    child.review = Review(
        status="REVIEWED",
        reviewer="SYNTHETIC TEST ONLY",
        evidence="not a real educational approval",
        content_sha256=child.review.content_sha256,
    )
    bind_pending_reviews(plan)
    assert extra.notes_review.content_sha256 != initial
    assert extra.notes_review.status == "UNREVIEWED" and extra.notes_review.reviewer is None
    assert extra.notes_review.content_sha256 == checksum(
        extra.model_dump(mode="json", exclude={"review", "notes_review"})
    )
    child.explanation_vi += " changed"
    with pytest.raises(ContentError, match="stale signed review"):
        bind_pending_reviews(plan)


def test_every_proposed_binding_matches_actual_review_payload():
    plan = bind_pending_reviews(corrected_plan())
    for _, _, item, review, excluded in review_items(plan):
        assert review.content_sha256 == checksum(item.model_dump(mode="json", exclude=excluded))
        assert review.status == "UNREVIEWED" and review.reviewer is None and review.evidence is None
    for asset in audit_assets(plan):
        assert asset["original_bytes_unchanged"]
        assert asset["owner_inspection"]["evidence_type"] == "USER_REPORTED_INSPECTION"
        assert not asset["owner_inspection"]["formal_approval"]
        assert not asset["owner_inspection"]["owner_supplied_checksum"]


def test_final_quiz_audit_rejects_wrong_private_keys_and_scopes():
    from app.services.roadmap_preparation import compile_drafts

    catalog = load_catalog([CATALOG])
    definition, _, _ = compile_drafts(corrected_plan(), catalog, PACK, operator_preview=True)
    assert len(audit_quizzes(definition, catalog)) == 9
    activity = next(a for a in definition.nodes[0].lesson.activities if a.kind == "QUIZ")
    activity.correct_option = (activity.correct_option + 1) % len(activity.options)
    with pytest.raises(ContentError, match="sole correct"):
        audit_quizzes(definition, catalog)


def test_unsigned_review_form_cannot_satisfy_normal_publication_gates(tmp_path):
    from app.services.roadmap_preparation import validate_generated

    prepare(corrected_plan(), tmp_path)
    from app.schemas.roadmap_preparation import PreparationPlan

    plan = PreparationPlan.model_validate(load_json(tmp_path / "plan.json"))
    assert not validate_generated(plan, load_catalog([CATALOG]), PACK, tmp_path / "content")[
        1
    ].payload()["draft_valid"]
    assert load_json(tmp_path / "content/manifest.json")["purpose"] == "OPERATOR_REVIEW_ONLY"


def test_partial_signoffs_do_not_auto_approve_parents_and_require_real_fields(tmp_path):
    from pydantic import ValidationError

    from app.schemas.roadmap_preparation import PreparationPlan
    from scripts.finalize_hsk0_review import apply_signoffs

    prepare(corrected_plan(), tmp_path)
    plan = PreparationPlan.model_validate(load_json(tmp_path / "plan.json"))
    form = load_json(tmp_path / "signoff-form.json")
    row = next(i for i in form["items"] if i["category"] == "COMPONENT")
    row["decision"] = "APPROVED"
    row["review"]["status"] = "REVIEWED"
    with pytest.raises(ValidationError):
        apply_signoffs(plan, form)
    row["review"].update(reviewer="SYNTHETIC TEST ONLY", evidence="isolated fixture only")
    result = apply_signoffs(plan, form)
    assert result.enrichments[0].components[0].review.status == "REVIEWED"
    assert result.enrichments[0].notes_review.status == "UNREVIEWED"
    assert (
        result.enrichments[0].notes_review.content_sha256
        != plan.enrichments[0].notes_review.content_sha256
    )
    assert plan.enrichments[0].components[0].review.status == "UNREVIEWED"
    # Exercise the documented two-stage flow with synthetic signatures only, in tmp_path.
    for item in form["items"]:
        if item["category"] != "NOTES":
            item["decision"] = "APPROVED"
            item["review"].update(
                status="REVIEWED", reviewer="SYNTHETIC TEST ONLY", evidence="isolated fixture only"
            )
    children = apply_signoffs(plan, form)
    child_report = prepare(children, tmp_path / "children")
    assert child_report["counts"]["APPROVED"] == 14
    parent_form = load_json(tmp_path / "children/signoff-form.json")
    for item in parent_form["items"]:
        if item["category"] == "NOTES":
            item["decision"] = "APPROVED"
            item["review"].update(
                status="REVIEWED", reviewer="SYNTHETIC TEST ONLY", evidence="isolated fixture only"
            )
    signed = apply_signoffs(children, parent_form)
    report = prepare(signed, tmp_path / "signed")
    assert report["counts"]["APPROVED"] == 17
    assert not report[
        "publication_ready"
    ]  # Overall acceptance and release authorization remain separate.
    assert "purpose" not in load_json(tmp_path / "signed/content/manifest.json")


def test_signing_children_and_stale_parent_hashes_in_one_form_is_rejected(tmp_path):
    from app.schemas.roadmap_preparation import PreparationPlan
    from scripts.finalize_hsk0_review import apply_signoffs

    prepare(corrected_plan(), tmp_path)
    plan = PreparationPlan.model_validate(load_json(tmp_path / "plan.json"))
    form = load_json(tmp_path / "signoff-form.json")
    for row in form["items"]:
        row["decision"] = "APPROVED"
        row["review"].update(
            status="REVIEWED", reviewer="SYNTHETIC TEST ONLY", evidence="isolated fixture only"
        )
    with pytest.raises(ContentError, match="notes follow children"):
        apply_signoffs(plan, form)
