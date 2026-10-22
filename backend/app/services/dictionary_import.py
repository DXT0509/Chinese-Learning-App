"""Atomic, serialized snapshot imports, with bounded SQL batches and no curriculum writes."""

from dataclasses import asdict
from uuid import uuid5

from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dictionary import DictionaryEntry, DictionaryImport
from app.services.cedict import (
    ATTRIBUTION,
    CHANGES,
    LICENSE,
    LICENSE_URL,
    NAMESPACE,
    SOURCE,
    SOURCE_URL,
    CedictDataset,
    DictionaryImportError,
)
from app.services.dictionary_revision import validate_revision


async def import_dictionary(session: AsyncSession, dataset: CedictDataset, revision: str) -> dict:
    validate_revision(revision)
    if not dataset.entries:
        raise DictionaryImportError("Dataset contains no entries")
    import_id = uuid5(NAMESPACE, f"{SOURCE}:revision:{revision}")
    async with session.begin():
        # One source importer at a time, including imports of different revisions.
        await session.execute(select(func.pg_advisory_xact_lock(731031)))
        # Maintenance can correct a revision while retaining its original import UUID/FKs.
        previous = await session.scalar(
            select(DictionaryImport).where(
                DictionaryImport.source == SOURCE,
                DictionaryImport.revision == revision,
            )
        )
        if previous:
            if previous.sha256 != dataset.sha256:
                raise DictionaryImportError("Revision is immutable; use a new revision")
            # Replaying a superseded revision must not roll the live source backwards.
            other = await session.scalar(
                select(DictionaryEntry.id)
                .where(
                    DictionaryEntry.source == SOURCE,
                    DictionaryEntry.active.is_(True),
                    DictionaryEntry.import_id != previous.id,
                )
                .limit(1)
            )
            if other:
                raise DictionaryImportError("Revision superseded; use a new revision")
            return {
                "entries": previous.entry_count,
                "duplicate_rows": dataset.duplicate_rows,
                "replayed": True,
                "batches": 0,
            }
        # An automatic label must not disguise the accidental placeholder as a new snapshot.
        same_artifact = (
            await session.scalars(
                select(DictionaryImport).where(
                    DictionaryImport.source == SOURCE,
                    DictionaryImport.sha256 == dataset.sha256,
                )
            )
        ).all()
        for historical in same_artifact:
            try:
                validate_revision(historical.revision)
            except DictionaryImportError:
                raise DictionaryImportError(
                    "Artifact already has a placeholder import; run repair_dictionary_revision"
                ) from None
        session.add(
            DictionaryImport(
                id=import_id,
                source=SOURCE,
                revision=revision,
                sha256=dataset.sha256,
                source_url=SOURCE_URL,
                license=LICENSE,
                license_url=LICENSE_URL,
                attribution=ATTRIBUTION,
                changes=CHANGES,
                entry_count=len(dataset.entries),
            )
        )
        await session.flush()
        await session.execute(
            update(DictionaryEntry)
            .where(
                DictionaryEntry.source == SOURCE,
                DictionaryEntry.active.is_(True),
            )
            .values(active=False)
        )
        batches = 0
        for start in range(0, len(dataset.entries), 500):
            values = [
                dict(asdict(entry), source=SOURCE, import_id=import_id, active=True)
                for entry in dataset.entries[start : start + 500]
            ]
            statement = insert(DictionaryEntry).values(values)
            await session.execute(
                statement.on_conflict_do_update(
                    index_elements=[DictionaryEntry.id],
                    set_={
                        name: getattr(statement.excluded, name)
                        for name in (
                            "import_id",
                            "pinyin",
                            "english_glosses",
                            "active",
                        )
                    },
                )
            )
            batches += 1
    return {
        "entries": len(dataset.entries),
        "duplicate_rows": dataset.duplicate_rows,
        "replayed": False,
        "batches": batches,
    }
