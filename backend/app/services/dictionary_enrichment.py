"""Source-grounded character annotations; never lexical translations or reading synthesis."""

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid5

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dictionary import DictionaryCharacterEnrichment, DictionaryEnrichmentImport
from app.services.cedict import NAMESPACE, DictionaryImportError
from app.services.dictionary_revision import validate_revision

SOURCE = "hsk-sino-viet"
SOURCE_URL = "https://github.com/xkhanhs/hsk-sino-viet"
LICENSE = "CC-BY-4.0"
LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/"
ATTRIBUTION = "Data from the Kai Hanzi HSK × Sino-Vietnamese dataset (https://kaihanzi.com/chu)."
REVIEW_STATUS = "source_declared_manual_not_independently_reviewed"
CHANGES = "Selected character fields; NFC normalization. No lexical translation or concatenation."


class CharacterRecord(BaseModel):
    # Upstream mnemonic/radical/HSK/stroke fields are deliberately outside this slice.
    model_config = ConfigDict(extra="ignore", frozen=True)
    hanzi: str = Field(min_length=1, max_length=1)
    traditional: str | None = Field(default=None, min_length=1, max_length=1)
    pinyin: str = Field(min_length=1, max_length=100)
    sinoViet: str = Field(min_length=1, max_length=200)
    meaningVi: str = Field(min_length=1, max_length=4000)

    @field_validator("hanzi", "traditional", "pinyin", "sinoViet", "meaningVi", mode="before")
    @classmethod
    def normalize(cls, value):
        if value is None:
            return None
        if not isinstance(value, str):
            return value  # Pydantic reports a typed validation error.
        normalized = unicodedata.normalize("NFC", value.strip())
        if not normalized or any(unicodedata.category(c).startswith("C") for c in normalized):
            raise ValueError("Invalid source text")
        return normalized

    @field_validator("hanzi", "traditional")
    @classmethod
    def han_character(cls, value):
        if value is not None and not unicodedata.name(value, "").startswith(
            "CJK UNIFIED IDEOGRAPH-"
        ):
            raise ValueError("Expected a single Han character")
        return value


@dataclass(frozen=True)
class CharacterDataset:
    sha256: str
    records: list[CharacterRecord]


def load_character_dataset(path: Path, expected_sha256: str) -> CharacterDataset:
    payload = path.read_bytes()
    actual = hashlib.sha256(payload).hexdigest()
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha256) or actual != expected_sha256:
        raise DictionaryImportError("Enrichment SHA-256 mismatch")
    try:
        rows = json.loads(payload.decode("utf-8-sig"))
        if not isinstance(rows, list) or not rows:
            raise ValueError("Expected nonempty records")
        records = [CharacterRecord.model_validate(row) for row in rows]
    except (ValueError, ValidationError, TypeError):
        raise DictionaryImportError("Invalid character enrichment dataset") from None
    # The selected source identifies one record per simplified character. Do not guess
    # which pronunciation to use if an incoming file violates that identity contract.
    identities = set()
    variants = {}
    for record in records:
        if record.hanzi in identities:
            raise DictionaryImportError("Duplicate/ambiguous character identity")
        identities.add(record.hanzi)
        for form in {record.hanzi, record.traditional} - {None}:
            if form in variants and variants[form] != record.hanzi:
                raise DictionaryImportError("Ambiguous simplified/traditional mapping")
            variants[form] = record.hanzi
    return CharacterDataset(actual, records)


async def import_character_enrichment(
    session: AsyncSession,
    dataset: CharacterDataset,
    revision: str,
) -> dict:
    validate_revision(revision)
    if not dataset.records:
        raise DictionaryImportError("Empty enrichment dataset")
    import_id = uuid5(NAMESPACE, f"{SOURCE}:revision:{revision}")
    async with session.begin():
        await session.execute(select(func.pg_advisory_xact_lock(731032)))
        previous = await session.scalar(
            select(DictionaryEnrichmentImport).where(
                DictionaryEnrichmentImport.source == SOURCE,
                DictionaryEnrichmentImport.revision == revision,
            )
        )
        if previous:
            if previous.sha256 != dataset.sha256:
                raise DictionaryImportError("Enrichment revision is immutable")
            return {"records": previous.record_count, "replayed": True, "batches": 0}
        session.add(
            DictionaryEnrichmentImport(
                id=import_id,
                source=SOURCE,
                revision=revision,
                sha256=dataset.sha256,
                source_url=SOURCE_URL,
                license=LICENSE,
                license_url=LICENSE_URL,
                attribution=ATTRIBUTION,
                changes=CHANGES,
                review_status=REVIEW_STATUS,
                record_count=len(dataset.records),
            )
        )
        await session.flush()
        # Partial coverage is additive. Omitted characters keep last-seen provenance.
        # Refuse a new alias that would make existing character resolution ambiguous.
        existing = (
            await session.scalars(
                select(DictionaryCharacterEnrichment).where(
                    DictionaryCharacterEnrichment.source == SOURCE,
                )
            )
        ).all()
        merged = {row.hanzi: row.traditional for row in existing}
        merged.update({row.hanzi: row.traditional for row in dataset.records})
        variants = {}
        for hanzi, traditional in merged.items():
            for form in {hanzi, traditional} - {None}:
                if form in variants and variants[form] != hanzi:
                    raise DictionaryImportError("Ambiguous character variant across imports")
                variants[form] = hanzi
        batches = 0
        for start in range(0, len(dataset.records), 500):
            statement = insert(DictionaryCharacterEnrichment).values(
                [
                    {
                        "source": SOURCE,
                        "hanzi": row.hanzi,
                        "traditional": row.traditional,
                        "pinyin": row.pinyin,
                        "sino_vietnamese": row.sinoViet,
                        "vietnamese_gloss": row.meaningVi,
                        "import_id": import_id,
                    }
                    for row in dataset.records[start : start + 500]
                ]
            )
            await session.execute(
                statement.on_conflict_do_update(
                    index_elements=[
                        DictionaryCharacterEnrichment.source,
                        DictionaryCharacterEnrichment.hanzi,
                    ],
                    set_={
                        name: getattr(statement.excluded, name)
                        for name in (
                            "traditional",
                            "pinyin",
                            "sino_vietnamese",
                            "vietnamese_gloss",
                            "import_id",
                        )
                    },
                )
            )
            batches += 1
    return {"records": len(dataset.records), "replayed": False, "batches": batches}
