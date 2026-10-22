from uuid import UUID

from sqlalchemy import case, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dictionary import (
    DictionaryCharacterEnrichment,
    DictionaryEnrichmentImport,
    DictionaryImport,
)
from app.models.dictionary import DictionaryEntry as Entry
from app.schemas.dictionary import DictionaryQuery


def prefix_end(value: str) -> str:
    # Input validation excludes surrogate/control/unassigned codepoints.
    return value[:-1] + chr(ord(value[-1]) + 1)


def search_statement(query: DictionaryQuery):
    lower, upper = query.q, prefix_end(query.q)
    exact = or_(Entry.simplified == lower, Entry.traditional == lower)
    return (
        select(Entry, DictionaryImport)
        .join(DictionaryImport, Entry.import_id == DictionaryImport.id)
        .where(
            Entry.active.is_(True),
            or_(
                (Entry.simplified >= lower) & (Entry.simplified < upper),
                (Entry.traditional >= lower) & (Entry.traditional < upper),
            ),
        )
        .order_by(
            case((exact, 0), else_=1),
            Entry.simplified,
            Entry.traditional,
            Entry.pinyin_numbered.collate("C"),
            Entry.id,
        )
        .offset(query.offset)
        .limit(query.limit + 1)
    )


class DictionaryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def search(self, query: DictionaryQuery):
        return (await self.session.execute(search_statement(query))).all()

    async def get_entry(self, entry_id: UUID):
        return (
            await self.session.execute(
                select(Entry, DictionaryImport)
                .join(DictionaryImport, Entry.import_id == DictionaryImport.id)
                .where(Entry.id == entry_id)
            )
        ).one_or_none()

    async def character_enrichments(self, characters: set[str]):
        return (
            await self.session.execute(
                select(DictionaryCharacterEnrichment, DictionaryEnrichmentImport)
                .join(
                    DictionaryEnrichmentImport,
                    DictionaryCharacterEnrichment.import_id == DictionaryEnrichmentImport.id,
                )
                .where(
                    or_(
                        DictionaryCharacterEnrichment.hanzi.in_(characters),
                        DictionaryCharacterEnrichment.traditional.in_(characters),
                    )
                )
                .order_by(DictionaryCharacterEnrichment.source, DictionaryCharacterEnrichment.hanzi)
            )
        ).all()
