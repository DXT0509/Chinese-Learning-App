import base64
from datetime import datetime
from uuid import UUID, uuid4

from fastapi import HTTPException
from sqlalchemy import delete, func, or_, select, tuple_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DictionaryEntry, DictionaryImport
from app.models.personal_vocabulary import PersonalVocabularyEntry as Saved
from app.schemas.personal_vocabulary import SavedVocabulary, VocabularyPage, VocabularyQuery


def response(saved, entry):
    return SavedVocabulary(
        id=saved.id,
        dictionary_entry_id=entry.id,
        saved_at=saved.saved_at,
        simplified=entry.simplified,
        traditional=entry.traditional,
        pinyin=entry.pinyin,
        short_en_meaning=entry.english_glosses[0] if entry.english_glosses else None,
        active=entry.active,
        source_revision_at_save=saved.source_revision_at_save,
        saved_snapshot=saved.saved_snapshot,
    )


class PersonalVocabularyService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def status(self, user_id: UUID, entry_id: UUID):
        return await self.session.scalar(
            select(Saved.id).where(Saved.user_id == user_id, Saved.dictionary_entry_id == entry_id)
        )

    async def save(self, user_id: UUID, entry_id: UUID):
        async with self.session.begin():
            # Lock the source row while capturing its definition/revision atomically.
            row = (
                await self.session.execute(
                    select(DictionaryEntry, DictionaryImport)
                    .join(DictionaryImport, DictionaryEntry.import_id == DictionaryImport.id)
                    .where(DictionaryEntry.id == entry_id)
                    .with_for_update(read=True)
                )
            ).first()
            if row is None:
                raise HTTPException(404, "Dictionary entry not found")
            entry, origin = row
            snapshot = {
                "simplified": entry.simplified,
                "traditional": entry.traditional,
                "pinyin_numbered": entry.pinyin_numbered,
                "citation_pinyin": entry.pinyin,
                "meanings": {"en": entry.english_glosses},
                "source": entry.source,
                "revision": origin.revision,
                "import_id": str(origin.id),
                "source_url": origin.source_url,
                "license": origin.license,
                "license_url": origin.license_url,
                "attribution": origin.attribution,
                "changes": origin.changes,
            }
            saved = await self.session.scalar(
                insert(Saved)
                .values(
                    id=uuid4(),
                    user_id=user_id,
                    dictionary_entry_id=entry_id,
                    source_revision_at_save=origin.revision,
                    saved_snapshot=snapshot,
                )
                # A no-op update locks and returns the winning association even when
                # another device is removing it. Saved-time fields stay unchanged.
                .on_conflict_do_update(
                    index_elements=[Saved.user_id, Saved.dictionary_entry_id],
                    set_={"id": Saved.id},
                )
                .returning(Saved)
            )
            return response(saved, entry)

    async def detail(self, user_id: UUID, saved_id: UUID):
        row = (
            await self.session.execute(
                select(Saved, DictionaryEntry)
                .join(DictionaryEntry)
                .where(Saved.user_id == user_id, Saved.id == saved_id)
            )
        ).first()
        if row is None:
            raise HTTPException(404, "Saved entry not found")
        return response(*row)

    async def remove(self, user_id: UUID, saved_id: UUID):
        async with self.session.begin():
            await self.session.execute(
                delete(Saved).where(Saved.user_id == user_id, Saved.id == saved_id)
            )

    async def listing(self, user_id: UUID, query: VocabularyQuery):
        filters = [Saved.user_id == user_id]
        if query.q:
            # Literal substring search, restricted to this user's indexed collection first.
            filters.append(
                or_(
                    *(
                        column.icontains(query.q, autoescape=True)
                        for column in (
                            DictionaryEntry.simplified,
                            DictionaryEntry.traditional,
                            DictionaryEntry.pinyin,
                            DictionaryEntry.pinyin_numbered,
                        )
                    )
                )
            )
        base = select(Saved, DictionaryEntry).join(DictionaryEntry).where(*filters)
        total = await self.session.scalar(select(func.count()).select_from(base.subquery()))
        if query.cursor:
            try:
                timestamp, identifier = (
                    base64.urlsafe_b64decode(query.cursor).decode().split("|", 1)
                )
                before = datetime.fromisoformat(timestamp)
                if before.tzinfo is None:
                    raise ValueError()
                identifier = UUID(identifier)
            except (ValueError, UnicodeError):
                raise HTTPException(422, "Invalid request") from None
            base = base.where(tuple_(Saved.saved_at, Saved.id) < tuple_(before, identifier))
        rows = (
            await self.session.execute(
                base.order_by(Saved.saved_at.desc(), Saved.id.desc()).limit(query.limit + 1)
            )
        ).all()
        cursor = None
        if len(rows) > query.limit:
            last = rows[query.limit - 1][0]
            cursor = base64.urlsafe_b64encode(
                f"{last.saved_at.isoformat()}|{last.id}".encode()
            ).decode()
        return VocabularyPage(
            items=[response(*row) for row in rows[: query.limit]], total=total, next_cursor=cursor
        )
