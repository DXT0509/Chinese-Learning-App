"""Transactional import and explicit human review, independent of retired providers."""

import hashlib
import json
from pathlib import Path
from uuid import UUID, uuid5

from sqlalchemy import delete, func, select

from app.models.curated_vocabulary import (
    CuratedBatch,
    CuratedVocabulary,
    VocabularyExample,
    VocabularyMeaning,
    VocabularyRevision,
)
from app.schemas.curated_vocabulary import CuratedRecord

NAMESPACE = UUID("18403e9f-d86b-4db3-b227-bab850de41fe")


def digest(payload: bytes):
    return hashlib.sha256(payload).hexdigest()


def load_records(path: Path):
    payload = path.read_bytes()
    records = [
        CuratedRecord.model_validate_json(line)
        for line in payload.decode("utf-8").splitlines()
        if line.strip()
    ]
    if not records or len({r.lexical_key for r in records}) != len(records):
        raise ValueError("Empty batch or duplicate lexical identities")
    return digest(payload), records


def record_checksum(record):
    return digest(
        json.dumps(
            record.model_dump(), ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
    )


async def import_records(session, batch_id, checksum, records):
    if not batch_id or len(batch_id) > 100:
        raise ValueError("Invalid batch identity")
    async with session.begin():
        await session.execute(select(func.pg_advisory_xact_lock(740001)))
        batch = await session.get(CuratedBatch, batch_id)
        if batch:
            if batch.checksum != checksum:
                raise ValueError("Batch identity already belongs to different bytes")
            for record in records:
                entry = await session.get(CuratedVocabulary, uuid5(NAMESPACE, record.lexical_key))
                if (
                    entry is None
                    or entry.checksum != record_checksum(record)
                    or entry.content_version != record.content_version
                ):
                    raise ValueError(
                        "Imported batch receipt does not match current catalog content"
                    )
            return {"unchanged_batch": True, "records": len(records)}
        session.add(CuratedBatch(id=batch_id, checksum=checksum))
        await session.flush()
        for record in records:
            identifier = uuid5(NAMESPACE, record.lexical_key)
            entry = await session.get(CuratedVocabulary, identifier)
            content_checksum = record_checksum(record)
            if entry and entry.checksum == content_checksum:
                continue
            if entry and record.content_version <= entry.content_version:
                raise ValueError("Revisions require a strictly increasing content_version")
            values = record.model_dump(
                exclude={"schema_version", "vietnamese_meanings", "english_meanings", "examples"}
            )
            if entry is None:
                entry = CuratedVocabulary(
                    id=identifier, **values, batch_id=batch_id, checksum=content_checksum
                )
                session.add(entry)
            else:
                for key, value in values.items():
                    setattr(entry, key, value)
                entry.batch_id, entry.checksum = batch_id, content_checksum
            await session.flush()
            for model in (VocabularyMeaning, VocabularyExample):
                await session.execute(delete(model).where(model.vocabulary_id == identifier))
            for language, meanings in (
                ("vi", record.vietnamese_meanings),
                ("en", record.english_meanings),
            ):
                for position, gloss in enumerate(meanings):
                    session.add(
                        VocabularyMeaning(
                            vocabulary_id=identifier,
                            language=language,
                            position=position,
                            gloss=gloss,
                        )
                    )
            for position, example in enumerate(record.examples):
                session.add(
                    VocabularyExample(
                        vocabulary_id=identifier, position=position, **example.model_dump()
                    )
                )
            session.add(
                VocabularyRevision(
                    vocabulary_id=identifier,
                    content_version=record.content_version,
                    checksum=content_checksum,
                    payload=record.model_dump(),
                )
            )
        return {"unchanged_batch": False, "records": len(records)}


async def approve_record(session, identifier, checksum, reviewer):
    if not reviewer.strip():
        raise ValueError("A named human reviewer is required")
    async with session.begin():
        await session.execute(select(func.pg_advisory_xact_lock(740001)))
        entry = await session.get(CuratedVocabulary, identifier, with_for_update=True)
        if entry is None or entry.checksum != checksum:
            raise ValueError("Review checksum does not match current content")
        meaning = await session.scalar(
            select(VocabularyMeaning.gloss).where(
                VocabularyMeaning.vocabulary_id == identifier,
                VocabularyMeaning.language == "vi",
                func.length(func.trim(VocabularyMeaning.gloss)) > 0,
            )
        )
        if meaning is None:
            raise ValueError("Human approval requires a usable Vietnamese meaning")
        revision = await session.get(VocabularyRevision, (identifier, entry.content_version))
        revision.payload = {
            **revision.payload,
            "human_review": {"reviewer": reviewer, "checksum": checksum},
        }
        entry.review_status = "HUMAN_APPROVED"
