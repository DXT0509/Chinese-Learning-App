import base64
import binascii
from datetime import datetime
from uuid import UUID, uuid4

from fastapi import HTTPException
from sqlalchemy import case, exists, func, or_, select, tuple_, update
from sqlalchemy.dialects.postgresql import insert

from app.core.config import get_settings
from app.models.curated_vocabulary import (
    CuratedUserVocabulary as Saved,
)
from app.models.curated_vocabulary import (
    CuratedVocabulary as Word,
)
from app.models.curated_vocabulary import (
    VocabularyAIReview,
    VocabularyExample,
    VocabularyLocalReview,
)
from app.models.curated_vocabulary import (
    VocabularyMeaning as Meaning,
)
from app.schemas.curated_api import (
    CuratedDetail,
    CuratedSaved,
    CuratedSearchResult,
    CuratedSuggestion,
    CuratedVocabularyPage,
)
from app.schemas.dictionary import DictionarySense


def visible():
    approved = Word.review_status == "HUMAN_APPROVED"
    if get_settings().allow_ai_approved_vocabulary:
        approved = approved | (
            (Word.review_status == "AI_APPROVED")
            & exists(
                select(VocabularyAIReview.id).where(
                    VocabularyAIReview.vocabulary_id == Word.id,
                    VocabularyAIReview.content_version == Word.content_version,
                    VocabularyAIReview.checksum == Word.checksum,
                    VocabularyAIReview.decision == "AI_APPROVED",
                )
            )
        )
    settings = get_settings()
    if settings.environment == "development" and settings.allow_local_codex_reviewed_vocabulary:
        approved = approved | (
            (Word.review_status == "LOCAL_CODEX_REVIEWED")
            & exists(
                select(VocabularyLocalReview.id).where(
                    VocabularyLocalReview.vocabulary_id == Word.id,
                    VocabularyLocalReview.content_version == Word.content_version,
                    VocabularyLocalReview.checksum == Word.checksum,
                )
            )
        )
    return approved & exists(
        select(Meaning.vocabulary_id).where(
            Meaning.vocabulary_id == Word.id,
            Meaning.language == "vi",
            func.length(func.trim(Meaning.gloss)) > 0,
        )
    )


def matches(query):
    return or_(
        *(
            column.icontains(query, autoescape=True)
            for column in (Word.simplified, Word.pinyin, Word.pinyin_numbered)
        ),
        exists(
            select(Meaning.vocabulary_id).where(
                Meaning.vocabulary_id == Word.id, Meaning.gloss.icontains(query, autoescape=True)
            )
        ),
    )


class CuratedCatalog:
    def __init__(self, session):
        self.session = session

    async def meanings(self, identifier):
        result = {}
        for meaning in await self.session.scalars(
            select(Meaning).where(Meaning.vocabulary_id == identifier).order_by(Meaning.position)
        ):
            result.setdefault(meaning.language, []).append(
                DictionarySense(sense_number=meaning.position + 1, gloss=meaning.gloss)
            )
        return result

    async def suggestion(self, word):
        meanings = await self.meanings(word.id)
        return CuratedSuggestion(
            entry_id=word.id,
            simplified=word.simplified,
            primary_pinyin=word.pinyin,
            short_vi_meaning=meanings["vi"][0].gloss,
            available_languages=sorted(meanings),
            content_version=word.content_version,
            learning_level=word.learning_level,
        )

    async def search(self, query):
        words = list(
            await self.session.scalars(
                select(Word)
                .where(visible(), matches(query.q))
                .order_by(
                    (Word.simplified != query.q), Word.simplified, Word.pinyin_numbered, Word.id
                )
                .offset(query.offset)
                .limit(query.limit + 1)
            )
        )
        return CuratedSearchResult(
            items=[await self.suggestion(w) for w in words[: query.limit]],
            next_offset=query.offset + query.limit if len(words) > query.limit else None,
        )

    async def get_entry(self, identifier):
        word = await self.session.scalar(select(Word).where(Word.id == identifier, visible()))
        if word is None:
            raise HTTPException(404, "Vocabulary not found")
        suggestion = await self.suggestion(word)
        examples = list(
            await self.session.scalars(
                select(VocabularyExample)
                .where(VocabularyExample.vocabulary_id == word.id)
                .order_by(VocabularyExample.position)
            )
        )
        return CuratedDetail(
            **suggestion.model_dump(),
            pinyin_numbered=word.pinyin_numbered,
            citation_pinyin=word.pinyin,
            meanings=await self.meanings(word.id),
            sino_vietnamese=word.sino_vietnamese,
            part_of_speech=word.part_of_speech,
            review_status=word.review_status,
            examples=[
                {"simplified": e.simplified, "pinyin": e.pinyin, "vietnamese": e.vietnamese}
                for e in examples
            ],
        )

    async def saved_response(self, saved, word):
        meanings = await self.meanings(word.id)
        return CuratedSaved(
            id=saved.id,
            dictionary_entry_id=word.id,
            saved_at=saved.saved_at,
            simplified=word.simplified,
            pinyin=word.pinyin,
            short_vi_meaning=meanings.get("vi", [DictionarySense(sense_number=1, gloss="")])[
                0
            ].gloss,
            short_en_meaning=meanings["en"][0].gloss if meanings.get("en") else None,
            active=saved.is_active
            and bool(await self.session.scalar(select(visible()).where(Word.id == word.id))),
            mastery_level=saved.mastery_level,
            next_review_at=saved.next_review_at,
            last_reviewed_at=saved.last_reviewed_at,
        )

    async def status(self, user_id, entry_id):
        return await self.session.scalar(
            select(Saved.id).where(
                Saved.user_id == user_id, Saved.vocabulary_id == entry_id, Saved.is_active
            )
        )

    async def save(self, user_id, entry_id):
        async with self.session.begin():
            settings = get_settings()
            await self.session.execute(
                select(
                    func.set_config(
                        "app.allow_local_codex_reviewed_vocabulary",
                        str(
                            settings.environment == "development"
                            and settings.allow_local_codex_reviewed_vocabulary
                        ).lower(),
                        True,
                    )
                )
            )
            await self.session.execute(
                select(
                    func.set_config(
                        "app.allow_ai_approved_vocabulary",
                        str(get_settings().allow_ai_approved_vocabulary).lower(),
                        True,
                    )
                )
            )
            word = await self.session.scalar(
                select(Word).where(Word.id == entry_id, visible()).with_for_update(read=True)
            )
            if word is None:
                raise HTTPException(404, "Vocabulary not found")
            saved = await self.session.scalar(
                insert(Saved)
                .values(id=uuid4(), user_id=user_id, vocabulary_id=entry_id)
                .on_conflict_do_update(
                    index_elements=[Saved.user_id, Saved.vocabulary_id],
                    set_={
                        "is_active": True,
                        "schedule_version": case(
                            (Saved.is_active, Saved.schedule_version),
                            else_=Saved.schedule_version + 1,
                        ),
                    },
                )
                .returning(Saved)
            )
            return await self.saved_response(saved, word)

    async def detail(self, user_id, saved_id):
        row = (
            await self.session.execute(
                select(Saved, Word)
                .join(Word)
                .where(Saved.id == saved_id, Saved.user_id == user_id, Saved.is_active)
            )
        ).first()
        if row is None:
            raise HTTPException(404, "Saved entry not found")
        return await self.saved_response(*row)

    async def remove(self, user_id, saved_id):
        async with self.session.begin():
            await self.session.execute(
                update(Saved)
                .where(Saved.id == saved_id, Saved.user_id == user_id, Saved.is_active)
                .values(is_active=False, schedule_version=Saved.schedule_version + 1)
            )

    async def listing(self, user_id, query):
        base = select(Saved, Word).join(Word).where(Saved.user_id == user_id, Saved.is_active)
        if query.q:
            base = base.where(matches(query.q))
        total = await self.session.scalar(select(func.count()).select_from(base.subquery()))
        if query.cursor:
            try:
                timestamp, identifier = (
                    base64.b64decode(query.cursor, altchars=b"-_", validate=True)
                    .decode()
                    .split("|", 1)
                )
                timestamp = datetime.fromisoformat(timestamp)
                if timestamp.tzinfo is None:
                    raise ValueError()
                base = base.where(
                    tuple_(Saved.saved_at, Saved.id) < tuple_(timestamp, UUID(identifier))
                )
            except (ValueError, UnicodeError, binascii.Error):
                raise HTTPException(422, "Invalid request") from None
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
        return CuratedVocabularyPage(
            items=[await self.saved_response(*r) for r in rows[: query.limit]],
            total=total,
            next_cursor=cursor,
        )
