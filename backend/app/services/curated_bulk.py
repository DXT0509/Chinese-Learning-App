"""Explicit database reconciliation and resumable transactional batch imports."""

from collections import Counter
from uuid import uuid5

from sqlalchemy import func, select, text

from app.models.curated_vocabulary import CuratedBatch, CuratedVocabulary, VocabularyAIReview
from app.services.curated_catalog import visible
from app.services.curated_import import (
    NAMESPACE,
    digest,
    import_records,
    load_records,
    record_checksum,
)

HEAD = "0010_local_codex_review"


async def reconcile(session, audit, records):
    async with session.begin():
        await session.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"))
        identity = dict(
            (
                await session.execute(
                    text(
                        "SELECT current_database() AS database, current_user AS role, "
                        "inet_server_addr()::text AS host, inet_server_port() AS port"
                    )
                )
            )
            .mappings()
            .one()
        )
        revisions = list(await session.scalars(text("SELECT version_num FROM alembic_version")))
        if revisions != [HEAD]:
            return {
                "identity": identity,
                "migration": revisions,
                "blocked": "Apply reviewed head explicitly",
            }
        words = {w.lexical_key: w for w in await session.scalars(select(CuratedVocabulary))}
        batches = {b.id: b.checksum for b in await session.scalars(select(CuratedBatch))}
        actions = []
        for r in records:
            w = words.get(r.lexical_key)
            checksum = record_checksum(r)
            action = "INSERT"
            if w:
                if w.id != uuid5(NAMESPACE, r.lexical_key):
                    action = "IDENTITY_CONFLICT"
                elif w.checksum == checksum and w.content_version == r.content_version:
                    action = "IDENTICAL"
                elif r.content_version > w.content_version:
                    action = "NEW_REVISION"
                else:
                    action = "VERSION_CONFLICT"
            actions.append(
                {
                    "lexical_key": r.lexical_key,
                    "action": action,
                    "source_checksum": checksum,
                    "source_version": r.content_version,
                    "existing_checksum": w.checksum if w else None,
                    "existing_version": w.content_version if w else None,
                }
            )
        source_keys = {r.lexical_key for r in records}
        evidence = list(await session.scalars(select(VocabularyAIReview)))
        current_reviews = [
            e
            for e in evidence
            if any(
                w.id == e.vocabulary_id
                and w.checksum == e.checksum
                and w.content_version == e.content_version
                for w in words.values()
            )
        ]
        failures = Counter(
            f["aspect"]
            for e in current_reviews
            for f in e.evidence["review"]["findings"]
            if not f["resolved"]
        )
        visible_count = await session.scalar(
            select(func.count()).select_from(CuratedVocabulary).where(visible())
        )
        source_visible = await session.scalar(
            select(func.count())
            .select_from(CuratedVocabulary)
            .where(visible(), CuratedVocabulary.lexical_key.in_(source_keys))
        )
        statuses = Counter(w.review_status for w in words.values())
        matched = {
            w.id
            for k, w in words.items()
            if k in source_keys
            and any(a["lexical_key"] == k and a["action"] == "IDENTICAL" for a in actions)
        }
        result = {
            "identity": identity,
            "migration": revisions,
            "actions": actions,
            "action_counts": dict(Counter(a["action"] for a in actions)),
            "database_batches": batches,
            "catalog_status_counts": dict(statuses),
            "catalog_total": len(words),
            "dataset_identities_present": len(words.keys() & source_keys),
            "catalog_by_learning_level": dict(
                Counter(str(w.learning_level) for w in words.values())
            ),
            "outside_dataset": len(words.keys() - source_keys),
            "search_visible_catalog": visible_count,
            "search_visible_dataset": source_visible,
            "linguistic_failure_categories": dict(failures),
            "actual_review_models": [
                dict(t)
                for t in sorted(
                    {
                        tuple(sorted(e.evidence["review"]["reviewer"].items()))
                        for e in current_reviews
                    }
                )
            ],
            "stages": {
                **audit["stages"],
                "IMPORTED": len(matched),
                "AI_REVIEWED": len({e.vocabulary_id for e in current_reviews} & matched),
                "AI_APPROVED": sum(
                    w.id in matched and w.review_status == "AI_APPROVED" for w in words.values()
                ),
                "HUMAN_APPROVED": sum(
                    w.id in matched and w.review_status == "HUMAN_APPROVED" for w in words.values()
                ),
                "PENDING": sum(
                    w.id in matched and w.review_status in {"GENERATED_UNREVIEWED", "NEEDS_REVIEW"}
                    for w in words.values()
                ),
                "REJECTED": sum(
                    w.id in matched and w.review_status == "REJECTED" for w in words.values()
                ),
                "PUBLISHED": source_visible,
            },
        }
        return result


def plan_token(plan, audit):
    import json

    return digest(json.dumps({"plan": plan, "files": audit["files"]}, sort_keys=True).encode())


async def import_batches(sessions, root, audit, progress):
    """DB batch receipts are authoritative; progress is a convenience, not a skip gate."""
    for batch in audit["files"]:
        sha, records = load_records(root / batch["file"])
        if sha != batch["sha256"]:
            raise ValueError("Source changed after audit")
        batch_id = f"bulk-{batch['batch']}-{sha}"
        async with sessions() as session:
            result = await import_records(session, batch_id, sha, records)
        progress(batch["batch"], result)  # Only after commit; rerun recovers a lost checkpoint.
