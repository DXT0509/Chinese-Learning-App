"""Verify the actual owner-supplied approval artifact without creating any approvals."""

import pytest

from app.schemas.roadmap_preparation import PreparationPlan, Review
from app.services.content_files import ContentError
from app.services.roadmap_preparation import checksum, load_catalog, load_json, validate_generated
from scripts.finalize_hsk0_review import FINAL, bind_pending_reviews, review_items
from scripts.prepare_hsk0_pack import CATALOG, PACK

SIGNED = PACK / "signed-complete-v4"


def test_owner_signatures_bind_exact_v4_content_and_all_dependencies():
    source = load_json(FINAL / "bundle.json")
    plan = PreparationPlan.model_validate(load_json(SIGNED / "plan.json"))
    authorization = load_json(SIGNED / "owner-authorization.json")
    before = plan.model_dump(mode="json")
    assert bind_pending_reviews(plan).model_dump(mode="json") == before
    items = list(review_items(plan))
    assert len(items) == 17
    for _, _, item, review, excluded in items:
        assert review.status == "REVIEWED"
        assert review.reviewer == "dxt" and review.evidence == "HSK0-EDU-REVIEW-20261102"
        assert review.content_sha256 == checksum(item.model_dump(mode="json", exclude=excluded))
    assert authorization["signed_plan_sha256"] == checksum(before)
    overall = Review.model_validate(authorization["overall_educational_review"])
    assert overall.content_sha256 == checksum(source["definition"])
    assert overall.reviewer == "dxt" and overall.evidence == "HSK0-EDU-REVIEW-20261102"
    assert not authorization["development_write_authorization"]
    assert not authorization["published"] and not authorization["activated"]


def test_signed_pack_passes_normal_gates_without_changing_accepted_educational_content():
    plan = PreparationPlan.model_validate(load_json(SIGNED / "plan.json"))
    definition, report = validate_generated(plan, load_catalog([CATALOG]), PACK, SIGNED / "content")
    assert report.payload()["counts"]["ERROR"] == 0
    assert report.payload()["draft_valid"]
    assert definition.model_dump(mode="json") == load_json(FINAL / "bundle.json")["definition"]
    assert "purpose" not in load_json(SIGNED / "content/manifest.json")
    assert load_json(SIGNED / "review-status.json")["counts"] == {
        "APPROVED": 17,
        "READY_FOR_APPROVAL": 0,
        "REQUEST_CHANGES": 0,
        "BLOCKED": 0,
    }


def test_signed_content_edits_invalidate_approval_instead_of_refreshing_signed_hash():
    plan = PreparationPlan.model_validate(load_json(SIGNED / "plan.json"))
    previous_hash = plan.enrichments[2].components[0].review.content_sha256
    plan.enrichments[2].components[0].explanation_vi += " changed after approval"
    with pytest.raises(ContentError, match="stale signed review"):
        bind_pending_reviews(plan)
    assert plan.enrichments[2].components[0].review.content_sha256 == previous_hash
