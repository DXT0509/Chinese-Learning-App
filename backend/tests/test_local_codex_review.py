"""Synthetic fixtures exercise local policy; never vocabulary review evidence."""

import json
import shutil
from pathlib import Path
from uuid import uuid5

import pytest
from pydantic import ValidationError
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from app.core.config import Settings, get_settings
from app.models.curated_vocabulary import CuratedVocabulary, VocabularyLocalReview
from app.services.curated_import import NAMESPACE, record_checksum
from app.services.local_codex_review import ASPECTS, POLICY, accept_local, load_checkpoint, preview
from tests.test_curated_vocabulary import (
    curated_client as curated_client,  # noqa: PLC0414
)
from tests.test_curated_vocabulary import (
    curated_sessions as curated_sessions,  # noqa: PLC0414
)
from tests.test_curated_vocabulary import install, record, register

ROOT = Path(__file__).resolve().parents[2] / "docs/datasets/codex-review-4.0.3"


def sample():
    row = record(
        examples=[
            {
                "simplified": "我学中文。",
                "pinyin": "Wǒ xué Zhōngwén.",
                "vietnamese": "Tôi học tiếng Trung.",
            }
        ]
    )
    evidence = {
        row.lexical_key: {
            "policy": POLICY,
            "authentication": "LOCAL_OPERATOR_ATTESTED_SESSION_NOTES",
            "reviewer_label": "Codex session",
            "reviewer_model": None,
            "reviewer_version": None,
            "record": {
                "lexical_key": row.lexical_key,
                "reviewed_content_version": row.content_version,
                "reviewed_checksum": record_checksum(row),
                "linguistic_outcome": "PASS",
                "local_development_candidate": True,
                "pending_reason": None,
                "checked_aspects": sorted(ASPECTS),
                "note": "Synthetic test note, not an actual review.",
            },
        }
    }
    return row, evidence


@pytest.mark.parametrize("environment", ["test", "production"])
def test_cannot_enable_outside_development(environment):
    with pytest.raises(ValidationError):
        Settings(environment=environment, allow_local_codex_reviewed_vocabulary=True)


def test_real_checkpoint_coverage_and_stale_notes(tmp_path):
    records, evidence, coverage = load_checkpoint(ROOT)
    assert coverage["reviewed"] + coverage["unreviewed"] == 2501
    assert len(records) == len(evidence) == coverage["accepted"]
    assert coverage["accepted"] < coverage["reviewed"]
    for row in records:
        assert row.examples and row.review_status != "NEEDS_REVIEW"
        assert evidence[row.lexical_key]["record"]["reviewed_checksum"] == record_checksum(row)
    # A real note with altered content is refused even when the JSONL file is intact.
    source = tmp_path / "original-zhvi"
    shutil.copytree(ROOT.parent / "original-zhvi", source)
    target = tmp_path / "checkpoint"
    shutil.copytree(ROOT / "L4-B001", target / "L4-B001")
    path = target / "L4-B001/review-notes.json"
    notes = json.loads(path.read_text(encoding="utf-8"))
    notes["records"][0]["reviewed_checksum"] = "0" * 64
    path.write_text(json.dumps(notes), encoding="utf-8")
    with pytest.raises(ValueError, match="Stale"):
        load_checkpoint(target)


@pytest.mark.postgres
async def test_local_visibility_save_replay_stale_and_immutable(
    curated_sessions, curated_client, monkeypatch
):
    row, evidence = sample()
    identifier = uuid5(NAMESPACE, row.lexical_key)
    await install(curated_sessions, [row])
    headers = await register(curated_client, "local-review-owner")
    detail = f"/api/v1/dictionary/entries/{identifier}"
    async with curated_sessions() as session:
        with pytest.raises(ValueError, match="enablement"):
            await accept_local(session, [row], evidence, "Test operator")
    monkeypatch.setattr(get_settings(), "environment", "development")
    monkeypatch.setattr(get_settings(), "allow_local_codex_reviewed_vocabulary", True)
    for _ in range(2):
        async with curated_sessions() as session:
            await accept_local(session, [row], evidence, "Test operator")
    async with curated_sessions() as session:
        receipts = list(await session.scalars(select(VocabularyLocalReview)))
        assert len(receipts) == 1 and receipts[0].evidence["reviewer_model"] is None
    response = await curated_client.get(detail, headers=headers)
    assert (
        response.status_code == 200 and response.json()["review_status"] == "LOCAL_CODEX_REVIEWED"
    )
    search = await curated_client.get(
        "/api/v1/dictionary/search", params={"q": "học"}, headers=headers
    )
    assert search.json()["items"][0]["entry_id"] == str(identifier)
    saved = await curated_client.post(
        "/api/v1/me/vocabulary", json={"dictionary_entry_id": str(identifier)}, headers=headers
    )
    assert saved.status_code == 200 and saved.json()["mastery_level"] == 0
    monkeypatch.setattr(get_settings(), "allow_local_codex_reviewed_vocabulary", False)
    assert (await curated_client.get(detail, headers=headers)).status_code == 404
    monkeypatch.setattr(get_settings(), "allow_local_codex_reviewed_vocabulary", True)
    async with curated_sessions() as session:
        with pytest.raises(IntegrityError):
            async with session.begin():
                await session.execute(update(VocabularyLocalReview).values(submitted_by="Changed"))
    # New content/version invalidates approval and hides any old receipt.
    revised = row.model_copy(update={"content_version": 2, "vietnamese_meanings": ["học tập"]})
    await install(curated_sessions, [revised], "v2-local", "b" * 64)
    assert (await curated_client.get(detail, headers=headers)).status_code == 404
    async with curated_sessions() as session:
        with pytest.raises(ValueError, match="no longer"):
            await accept_local(session, [row], evidence, "Test operator")


@pytest.mark.postgres
async def test_hold_preservation_and_confirmation_changes(curated_sessions, monkeypatch):
    row, evidence = sample()
    await install(curated_sessions, [row])
    monkeypatch.setattr(get_settings(), "environment", "development")
    monkeypatch.setattr(get_settings(), "allow_local_codex_reviewed_vocabulary", True)
    async with curated_sessions() as session:
        before = await preview(session, [row], evidence, {})
    async with curated_sessions() as session, session.begin():
        await session.execute(update(CuratedVocabulary).values(review_status="NEEDS_REVIEW"))
    async with curated_sessions() as session:
        after = await preview(session, [row], evidence, {})
        assert after["confirmation"] != before["confirmation"]
        assert after["changes"][0]["action"] == "PRESERVE_HOLD"
        await session.rollback()
        with pytest.raises(ValueError, match="editorial"):
            await accept_local(session, [row], evidence, "Test operator")
