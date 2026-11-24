"""Read-only reconciliation of the selected HSK 0 identities; never imports or approves."""

import argparse
import asyncio
from pathlib import Path

from sqlalchemy import select, text

from app.core.database import engine, session_factory
from app.core.event_loop import new_event_loop
from app.models.curated_vocabulary import CuratedVocabulary, VocabularyRevision
from app.schemas.roadmap_preparation import PreparationPlan
from app.services.curated_catalog import visible
from app.services.curated_import import record_checksum
from app.services.roadmap_preparation import checksum, load_catalog, load_json, write_artifact
from scripts.prepare_hsk0_pack import CATALOG, build_plan


async def reconcile(output, plan_file=None, catalog_files=None):
    plan = PreparationPlan.model_validate(load_json(plan_file)) if plan_file else build_plan()
    catalog = load_catalog(catalog_files or [CATALOG])
    refs = [ref for group in plan.groups for ref in group.vocabulary]
    try:
        async with session_factory() as session, session.begin():
            await session.execute(text("SET TRANSACTION READ ONLY"))
            revision = await session.scalar(text("SELECT version_num FROM alembic_version"))
            rows = (
                await session.execute(
                    select(
                        CuratedVocabulary,
                        visible().label("visible"),
                    ).where(CuratedVocabulary.id.in_([r.vocabulary_id for r in refs]))
                )
            ).all()
            current = {row[0].id: row for row in rows}
            results = []
            for ref in refs:
                source = catalog[ref.vocabulary_id]
                row = current.get(ref.vocabulary_id)
                word = row[0] if row else None
                pinned = await session.get(
                    VocabularyRevision, (ref.vocabulary_id, ref.content_version)
                )
                match = bool(
                    word
                    and pinned
                    and word.content_version == ref.content_version
                    and word.checksum == pinned.checksum == record_checksum(source)
                )
                results.append(
                    {
                        "vocabulary_id": str(ref.vocabulary_id),
                        "lexical_key": source.lexical_key,
                        "expected_version": ref.content_version,
                        "current_version": word.content_version if word else None,
                        "review_status": word.review_status if word else None,
                        "visible_under_current_policy": bool(row[1]) if row else False,
                        "source_checksum": record_checksum(source),
                        "current_checksum": word.checksum if word else None,
                        "exact_revision_match": match,
                    }
                )
        report = {
            "plan_sha256": checksum(plan.model_dump(mode="json")),
            "read_only": True,
            "alembic_revision": revision,
            "identities": results,
            "all_bindings_match": all(
                r["exact_revision_match"] and r["visible_under_current_policy"] for r in results
            ),
            "educational_approval": "PENDING",
            "publication_ready": False,
        }
        write_artifact(output, report)
        print(
            "Read-only reconciliation saved; exact visible bindings: "
            + str(report["all_bindings_match"])
        )
        return 0 if report["all_bindings_match"] else 1
    finally:
        await engine.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--catalog", type=Path, nargs="+")
    args = parser.parse_args()
    with asyncio.Runner(loop_factory=new_event_loop) as runner:
        raise SystemExit(runner.run(reconcile(args.output, args.plan, args.catalog)))


if __name__ == "__main__":
    main()
