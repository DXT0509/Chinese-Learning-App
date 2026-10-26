"""Synthetic reviewer fixtures are test evidence only, never real linguistic review."""

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4, uuid5

import pytest
from pydantic import ValidationError
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError

from app.core.config import get_settings
from app.models.curated_vocabulary import (
    CuratedUserVocabulary,
    CuratedVocabulary,
    VocabularyAIReview,
)
from app.schemas.curated_review import ASPECTS, POLICY, ModelIdentity, ReviewResult
from app.services.curated_batch001 import convert_batch001
from app.services.curated_import import NAMESPACE, load_records
from app.services.curated_review import coverage, import_reviews, review_inputs
from tests.test_curated_vocabulary import (
    curated_client as curated_client,  # noqa: PLC0414 -- pytest fixture re-export
)
from tests.test_curated_vocabulary import (
    curated_sessions as curated_sessions,  # noqa: PLC0414 -- pytest fixture re-export
)
from tests.test_curated_vocabulary import (
    install,
    record,
    register,
)


def request_for(row=None):
    row = row or record(
        examples=[
            {
                "simplified": "我学中文。",
                "pinyin": "wǒ xué zhōng wén.",
                "vietnamese": "Tôi học tiếng Trung.",
            }
        ]
    )
    return review_inputs(
        [row], ModelIdentity(provider="fixture-generator", model="generator", version="test-1")
    )[0]


def result_for(request, **changes):
    return ReviewResult.model_validate(
        {
            "schema_version": 1,
            "review_id": str(uuid4()),
            "policy_version": POLICY,
            "lexical_key": request.content.lexical_key,
            "content_version": request.content.content_version,
            "content_checksum": request.content_checksum,
            "generator": request.generator.model_dump(),
            "reviewer": {"provider": "fixture-reviewer", "model": "reviewer", "version": "test-2"},
            "reviewed_at": datetime.now(UTC),
            "decision": "AI_APPROVED",
            "confidence": 0.99,
            "assessments": [
                {"aspect": a, "result": "pass", "rationale": "Synthetic test assertion"}
                for a in ASPECTS
            ],
            "findings": [],
            "automated_validation": request.automated_validation.model_dump(),
            **changes,
        }
    )


@pytest.mark.parametrize(
    "changes",
    [
        {"confidence": 0.8},
        {"policy_version": "unknown"},
        {"reviewed_at": "2099-01-01T00:00:00Z"},
        {"reviewed_at": "2026-01-01T00:00:00"},
        {"assessments": []},
        {
            "reviewer": {
                "provider": "fixture-generator",
                "model": "generator",
                "version": "different-version",
            }
        },
        {
            "findings": [
                {
                    "aspect": "ambiguity",
                    "severity": "blocking",
                    "resolved": False,
                    "message": "Uncertain meaning",
                }
            ]
        },
    ],
)
def test_invalid_approval_evidence(changes):
    with pytest.raises(ValidationError):
        result_for(request_for(), **changes)


def test_batch001_conversion_preserves_source_and_holds(tmp_path):
    source = (
        Path(__file__).resolve().parents[2] / "docs/datasets/original-zhvi/level-0-batch-001.jsonl"
    )
    before = source.read_bytes()
    rows, provenance = convert_batch001(source)
    assert source.read_bytes() == before
    assert len(rows) == 51
    assert sum(r.review_status == "NEEDS_REVIEW" for r in rows) == 5
    assert len(provenance["mappings"]) == 51
    output = tmp_path / "converted.jsonl"
    output.write_text("\n".join(r.model_dump_json() for r in rows), encoding="utf-8")
    assert len(load_records(output)[1]) == 51


@pytest.mark.postgres
async def test_ai_publication_replay_versions_and_owner_mastery(
    curated_sessions, curated_client, monkeypatch
):
    sessions, client = curated_sessions, curated_client
    request = request_for()
    await install(sessions, [request.content])
    result = result_for(request)
    async with sessions() as session:
        assert (await import_reviews(session, [request], [result], "test operator"))[
            "AI_APPROVED"
        ] == 1
        assert (await import_reviews(session, [request], [result], "test operator"))[
            "replayed"
        ] == 1
    a, b = await register(client, "ai-owner"), await register(client, "ai-other")
    identifier = uuid5(NAMESPACE, request.content.lexical_key)
    detail = f"/api/v1/dictionary/entries/{identifier}"
    path = "/api/v1/me/vocabulary"
    body = {"dictionary_entry_id": str(identifier)}
    assert (await client.get(detail, headers=a)).status_code == 404
    assert (await client.post(path, json=body, headers=a)).status_code == 404
    monkeypatch.setattr(get_settings(), "allow_ai_approved_vocabulary", True)
    response = await client.get(detail, headers=a)
    assert response.status_code == 200 and response.json()["review_status"] == "AI_APPROVED"
    assert (
        len(
            (await client.get("/api/v1/dictionary/search", params={"q": "学"}, headers=a)).json()[
                "items"
            ]
        )
        == 1
    )
    saved = (await client.post(path, json=body, headers=a)).json()
    saved_path = path + "/" + saved["id"]
    assert (await client.get(saved_path, headers=b)).status_code == 404
    assert (await client.delete(saved_path, headers=b)).status_code == 204
    assert (await client.get(path, headers=b)).json()["total"] == 0
    async with sessions() as session, session.begin():
        await session.execute(update(CuratedUserVocabulary).values(mastery_level=4))
    revised = request_for(request.content.model_copy(update={"content_version": 2}))
    await install(sessions, [revised.content], "batch2", "b" * 64)
    assert (await client.get(detail, headers=a)).status_code == 404
    assert (await client.get(saved_path, headers=a)).json()["mastery_level"] == 4
    assert (await client.get(saved_path, headers=a)).json()["active"] is False
    async with sessions() as session:
        with pytest.raises(ValueError, match="Stale"):
            await import_reviews(session, [request], [result], "operator")
        await import_reviews(session, [revised], [result_for(revised)], "operator")
    assert (await client.post(path, json=body, headers=a)).json()["mastery_level"] == 4
    monkeypatch.setattr(get_settings(), "allow_ai_approved_vocabulary", False)
    assert (await client.get(saved_path, headers=a)).json()["active"] is False


@pytest.mark.postgres
async def test_rejection_evidence_and_replay(curated_sessions):
    sessions = curated_sessions
    request = request_for()
    await install(sessions, [request.content])
    approved = result_for(request)
    async with sessions() as session:
        with pytest.raises(ValueError):
            await import_reviews(session, [request], [result_for(request, content_version=2)], "op")
        assert await session.scalar(select(func.count()).select_from(VocabularyAIReview)) == 0
        await session.rollback()
        await import_reviews(session, [request], [approved], "operator")
        await import_reviews(session, [request], [result_for(request, decision="REJECTED")], "op")
        await import_reviews(session, [request], [approved], "operator")
        word = await session.get(CuratedVocabulary, uuid5(NAMESPACE, request.content.lexical_key))
        assert word.review_status == "REJECTED"
        report = await coverage(session)
        assert report["rejected"] == 1 and report["by_learning_level"]["0"] == 1
        await session.rollback()
        with pytest.raises(ValueError, match="different evidence"):
            await import_reviews(
                session, [request], [approved.model_copy(update={"confidence": 0.98})], "operator"
            )
    async with sessions() as session:
        with pytest.raises(IntegrityError):
            async with session.begin():
                await session.execute(update(VocabularyAIReview).values(submitted_by="tampered"))


@pytest.mark.postgres
async def test_editorial_holds(curated_sessions):
    request = request_for(record(review_status="NEEDS_REVIEW"))
    await install(curated_sessions, [request.content])
    async with curated_sessions() as session:
        counts = await import_reviews(session, [request], [result_for(request)], "operator")
        assert counts["NEEDS_REVIEW"] == 1


@pytest.mark.postgres
async def test_batch_rollback_and_unresolved_semantic_findings(curated_sessions):
    first = request_for()
    second = request_for(
        record(lexical_key="你|ni3", simplified="你", pinyin="nǐ", pinyin_numbered="ni3")
    )
    await install(curated_sessions, [first.content, second.content])
    async with curated_sessions() as session:
        with pytest.raises(ValueError):
            await import_reviews(
                session,
                [first, second],
                [result_for(first), result_for(second, content_version=2)],
                "op",
            )
        assert await session.scalar(select(func.count()).select_from(VocabularyAIReview)) == 0
        await session.rollback()
        uncertain = result_for(
            first,
            decision="NEEDS_REVIEW",
            confidence=0.6,
            findings=[
                {
                    "aspect": "duplicate_identity",
                    "severity": "blocking",
                    "resolved": False,
                    "message": "Possible lexical duplicate requiring resolution",
                }
            ],
        )
        await import_reviews(session, [first], [uncertain], "op")
        counts = await import_reviews(session, [first], [result_for(first)], "op")
        assert counts["NEEDS_REVIEW"] == 1
        # Missing examples also prevents publication even with nominal semantic approval.
        counts = await import_reviews(session, [second], [result_for(second)], "op")
        assert counts["NEEDS_REVIEW"] == 1


@pytest.mark.postgres
async def test_forged_ai_status_and_pending_are_not_publishable(
    curated_sessions, curated_client, monkeypatch
):
    monkeypatch.setattr(get_settings(), "allow_ai_approved_vocabulary", True)
    request = request_for()
    await install(curated_sessions, [request.content])
    headers = await register(curated_client, "no-evidence")
    identifier = uuid5(NAMESPACE, request.content.lexical_key)
    for status in ("AI_APPROVED", "NEEDS_REVIEW", "REJECTED"):
        async with curated_sessions() as session, session.begin():
            await session.execute(
                update(CuratedVocabulary)
                .where(CuratedVocabulary.id == identifier)
                .values(review_status=status)
            )
        assert (
            await curated_client.get(f"/api/v1/dictionary/entries/{identifier}", headers=headers)
        ).status_code == 404
        assert (
            await curated_client.post(
                "/api/v1/me/vocabulary",
                headers=headers,
                json={"dictionary_entry_id": str(identifier)},
            )
        ).status_code == 404
    async with curated_sessions() as session:
        report = await coverage(session)
        assert report["total_unique_vocabulary"] == 1
        assert report["missing_required_content"] == 0
