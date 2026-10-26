"""Offline review exchange and atomic audit import. No AI API is invoked."""

import json
from uuid import uuid5

from sqlalchemy import func, select

from app.models.curated_vocabulary import CuratedVocabulary, VocabularyAIReview, VocabularyRevision
from app.schemas.curated_review import AutomatedValidation, ReviewInput, ReviewResult
from app.schemas.curated_vocabulary import CuratedRecord
from app.services.curated_import import NAMESPACE, digest, record_checksum


def mechanical(record):
    record = CuratedRecord.model_validate(record.model_dump())
    return AutomatedValidation(
        validator_version="curated-record-v1",
        content_checksum=record_checksum(record),
        passed=True,
        checks=[
            "strict_schema",
            "simplified_only",
            "pinyin_rendering",
            "lexical_identity",
            "level_0_5",
            "required_vietnamese",
        ],
    )


def review_inputs(records, generator, catalog_records=()):
    return [
        ReviewInput(
            generator=generator,
            content_checksum=record_checksum(r),
            content=r,
            automated_validation=mechanical(r),
            lexical_catalog=sorted({item.lexical_key for item in [*records, *catalog_records]}),
        )
        for r in records
    ]


def load_exchange(path, schema):
    rows = [
        schema.model_validate_json(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not rows:
        raise ValueError("Empty exchange")
    return rows


async def import_reviews(session, requests, results, operator):
    if not operator.strip():
        raise ValueError("Named submitting operator required")
    expected = {r.content.lexical_key: r for r in requests}
    if len(expected) != len(requests) or len({r.lexical_key for r in results}) != len(results):
        raise ValueError("Duplicate exchange identities")
    counts = {"AI_APPROVED": 0, "NEEDS_REVIEW": 0, "REJECTED": 0, "replayed": 0}
    async with session.begin():
        await session.execute(select(func.pg_advisory_xact_lock(740001)))
        for result in results:
            # Revalidate even callers passing constructed models.
            result = ReviewResult.model_validate(result.model_dump())
            request = expected.get(result.lexical_key)
            if request is None:
                raise ValueError("Missing original review request")
            record = request.content
            validation = mechanical(record)
            if (
                request.content_checksum != validation.content_checksum
                or result.content_checksum != validation.content_checksum
                or result.content_version != record.content_version
                or result.generator != request.generator
                or result.automated_validation != validation
                or request.automated_validation != validation
            ):
                raise ValueError("Review evidence does not match request content/validation")
            identifier = uuid5(NAMESPACE, record.lexical_key)
            word = await session.get(CuratedVocabulary, identifier, with_for_update=True)
            if (
                word is None
                or word.checksum != result.content_checksum
                or (word.content_version != result.content_version)
            ):
                raise ValueError("Stale or missing catalog revision")
            revision = await session.get(VocabularyRevision, (identifier, word.content_version))
            original = {k: v for k, v in revision.payload.items() if k != "human_review"}
            if record_checksum(CuratedRecord.model_validate(original)) != word.checksum:
                raise ValueError("Revision integrity failure")
            evidence = {
                "review": result.model_dump(mode="json"),
                "automated_validation": validation.model_dump(),
                "request": request.model_dump(mode="json"),
            }
            evidence_hash = digest(json.dumps(evidence, sort_keys=True).encode())
            prior = await session.get(VocabularyAIReview, result.review_id)
            if prior:
                if prior.evidence_checksum != evidence_hash:
                    raise ValueError("Review ID reused with different evidence")
                counts["replayed"] += 1
                continue
            decision = result.decision
            # Editorial holds require a corrected, newly versioned draft, never an AI override.
            if decision == "AI_APPROVED" and (
                record.review_status == "NEEDS_REVIEW"
                or word.review_status in {"NEEDS_REVIEW", "REJECTED"}
                or not record.examples
            ):
                decision = "NEEDS_REVIEW"
            if word.review_status == "HUMAN_APPROVED":
                raise ValueError("AI review cannot overwrite human approval")
            session.add(
                VocabularyAIReview(
                    id=result.review_id,
                    vocabulary_id=identifier,
                    content_version=word.content_version,
                    checksum=word.checksum,
                    decision=decision,
                    evidence_checksum=evidence_hash,
                    evidence={
                        **evidence,
                        "effective_decision": decision,
                    },
                    submitted_by=operator,
                )
            )
            word.review_status = decision
            counts[decision] += 1
    return counts


async def coverage(session):
    from app.models.curated_vocabulary import VocabularyExample, VocabularyMeaning

    words = list(await session.scalars(select(CuratedVocabulary)))
    meanings = set(
        await session.scalars(
            select(VocabularyMeaning.vocabulary_id).where(
                VocabularyMeaning.language == "vi",
                func.length(func.trim(VocabularyMeaning.gloss)) > 0,
            )
        )
    )
    examples = set(await session.scalars(select(VocabularyExample.vocabulary_id)))
    reviews = list(
        await session.scalars(
            select(VocabularyAIReview).order_by(
                VocabularyAIReview.received_at.desc(), VocabularyAIReview.id.desc()
            )
        )
    )
    latest = {}
    for review in reviews:
        latest.setdefault(review.vocabulary_id, review)
    duplicates = {
        r.vocabulary_id
        for r in latest.values()
        if any(
            f["aspect"] == "duplicate_identity" and not f["resolved"]
            for f in r.evidence["review"]["findings"]
        )
        and any(w.id == r.vocabulary_id and w.checksum == r.checksum for w in words)
    }
    return {
        "total_unique_vocabulary": len(words),
        "target": 2500,
        "by_learning_level": {str(i): sum(w.learning_level == i for w in words) for i in range(6)},
        "pending_review": sum(
            w.review_status in {"GENERATED_UNREVIEWED", "NEEDS_REVIEW"} for w in words
        ),
        "ai_approved": sum(w.review_status == "AI_APPROVED" for w in words),
        "human_approved": sum(w.review_status == "HUMAN_APPROVED" for w in words),
        "rejected": sum(w.review_status == "REJECTED" for w in words),
        "duplicate_candidates": len(duplicates),
        "missing_required_content": sum(
            w.id not in meanings or w.id not in examples for w in words
        ),
    }
