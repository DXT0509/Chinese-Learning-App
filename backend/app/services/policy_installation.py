"""Atomic operator-only import. Caller owns the transaction."""

from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert

from app.models.curated_vocabulary import VocabularyExample
from app.models.srs import SrsTargetPolicy
from app.services.policy_coverage import GENERATOR as CONTEXT_GENERATOR
from app.services.policy_coverage import GENERATORS, prepare_coverage
from app.services.policy_preparation import GENERATOR, catalog_entries, prepare


async def import_policies(session, policies, *, install=False):
    keys = [(p.vocabulary_id, p.content_version, p.checksum) for p in policies]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate policy identity")
    # Serialize importers, and block concurrent content/evidence/publication edits
    # while checking the entire catalog for newly introduced cue/readings collisions.
    if install:
        await session.execute(
            text(
                "LOCK TABLE curated_vocabulary, vocabulary_meanings, vocabulary_examples, "
                "curated_vocabulary_ai_reviews, curated_vocabulary_local_reviews "
                "IN SHARE MODE"
            )
        )
        await session.execute(text("LOCK TABLE srs_target_policies IN SHARE ROW EXCLUSIVE MODE"))
    entries = await catalog_entries(session)
    by_id = {e.word.id: e for e in entries}
    generated, _ = prepare(entries)
    generated = {p.vocabulary_id: p for p in generated}
    context_generated, _ = prepare_coverage(entries)
    context_generated = {p.vocabulary_id: p for p in context_generated}
    counts = {
        "validated": 0,
        "inserted": 0,
        "unchanged": 0,
        "preserved_manual": 0,
        "would_insert": 0,
        "would_update": 0,
    }
    for policy, key in zip(policies, keys, strict=True):
        entry = by_id.get(policy.vocabulary_id)
        if entry is None or not entry.published:
            raise ValueError("Policy vocabulary is not currently published")
        policy.target(entry.word)
        if (
            policy.grammatical_review
            and await session.scalar(
                select(VocabularyExample.vocabulary_id)
                .where(
                    VocabularyExample.vocabulary_id == policy.vocabulary_id,
                    VocabularyExample.simplified == policy.grammatical_review.source_example,
                )
                .limit(1)
            )
            is None
        ):
            raise ValueError("Contextual grammar source example does not match the bound catalog")
        existing = await session.get(SrsTargetPolicy, key)
        payload = policy.model_dump(mode="json")
        if existing and existing.policy != payload:
            if (
                policy.policy_version in GENERATORS
                and existing.policy.get("policy_version") not in GENERATORS
            ):
                counts["preserved_manual"] += 1
                continue
            raise ValueError(
                "Existing policy is immutable; correction requires a new content version"
            )
        if policy.policy_version == GENERATOR and generated.get(policy.vocabulary_id) != policy:
            raise ValueError("Generated policy no longer matches current catalog; regenerate")
        if (
            policy.policy_version == CONTEXT_GENERATOR
            and context_generated.get(policy.vocabulary_id) != policy
        ):
            raise ValueError("Generated policy no longer matches current catalog; regenerate")
        counts["validated"] += 1
        if existing:
            counts["unchanged"] += 1
        else:
            counts["would_insert"] += 1
            if install:
                await session.execute(
                    insert(SrsTargetPolicy).values(
                        vocabulary_id=policy.vocabulary_id,
                        content_version=policy.content_version,
                        checksum=policy.checksum,
                        policy=payload,
                    )
                )
                counts["inserted"] += 1
    return counts
