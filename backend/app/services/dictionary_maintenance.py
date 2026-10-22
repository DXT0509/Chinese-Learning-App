"""Narrow metadata correction: stable import/entry IDs and an auditable original label."""

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid5

from sqlalchemy import func, inspect, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dictionary import DictionaryEntry, DictionaryImport
from app.services.cedict import NAMESPACE, SOURCE, DictionaryImportError, load_dataset
from app.services.dictionary_revision import artifact_revision


async def correct_revision(
    session: AsyncSession,
    path: Path,
    expected_sha256: str,
    from_revision: str = "your-actual-source-release",
    *,
    confirm: bool = False,
) -> dict:
    evidence = artifact_revision(path, expected_sha256)
    dataset = load_dataset(path, expected_sha256)
    target = evidence["revision"]
    if from_revision == target:
        raise DictionaryImportError("Original and corrected revisions must differ")
    async with session.begin():
        if confirm:
            await session.execute(select(func.pg_advisory_xact_lock(731031)))
        connection = await session.connection()
        names = await connection.run_sync(
            lambda sync: {c["name"] for c in inspect(sync).get_columns("dictionary_imports")}
        )
        has_audit = "revision_correction" in names
        # Dry-run also works before 0006, without selecting its new audit column.
        columns = [c for c in DictionaryImport.__table__.c if c.name in names]
        statement = select(*columns).where(
            DictionaryImport.source == SOURCE,
            DictionaryImport.revision.in_([from_revision, target]),
        )
        if confirm:
            statement = statement.with_for_update()
        matches = (await session.execute(statement)).mappings().all()
        if len(matches) != 1:
            raise DictionaryImportError("Expected one unambiguous original/corrected import")
        imported = matches[0]
        if imported["sha256"] != expected_sha256 or imported["id"] != uuid5(
            NAMESPACE, f"{SOURCE}:revision:{from_revision}"
        ):
            raise DictionaryImportError("Artifact checksum or original import identity mismatch")
        count, active = (
            await session.execute(
                select(
                    func.count(DictionaryEntry.id),
                    func.count(DictionaryEntry.id).filter(DictionaryEntry.active.is_(True)),
                ).where(DictionaryEntry.import_id == imported["id"])
            )
        ).one()
        if count != imported["entry_count"] or count != len(dataset.entries) or active != count:
            raise DictionaryImportError("Refusing partial or superseded import correction")
        already = imported["revision"] == target
        audit = imported.get("revision_correction")
        if already and (
            not audit
            or audit.get("original_revision") != from_revision
            or audit.get("sha256") != expected_sha256
        ):
            raise DictionaryImportError("Corrected revision lacks matching audit evidence")
        if not already and audit is not None:
            raise DictionaryImportError("Import already has a different correction history")
        summary = {
            "import_id": str(imported["id"]),
            "source": SOURCE,
            "from_revision": from_revision,
            "to_revision": target,
            "sha256": expected_sha256,
            "associated_entries": count,
            "original_imported_at": imported["imported_at"].isoformat(),
            "evidence": evidence,
            "requires_migration": not has_audit,
            "already_corrected": already,
            "changed": confirm and not already,
        }
        if confirm and not already:
            if not has_audit:
                raise DictionaryImportError(
                    "Apply 0006_dictionary_enrichment before confirmed repair"
                )
            await session.execute(
                update(DictionaryImport)
                .where(
                    DictionaryImport.id == imported["id"],
                )
                .values(
                    revision=target,
                    revision_correction={
                        **evidence,
                        "original_revision": from_revision,
                        "corrected_at": datetime.now(UTC).isoformat(),
                    },
                )
            )
    return summary
