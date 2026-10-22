from uuid import UUID

from fastapi import HTTPException

from app.repositories.dictionary import DictionaryRepository
from app.schemas.dictionary import (
    CharacterEnrichmentProvenance,
    DictionaryCharacterInfo,
    DictionaryDetail,
    DictionaryProvenance,
    DictionaryQuery,
    DictionarySearchResult,
    DictionarySense,
    DictionarySuggestion,
)


def suggestion(entry, imported) -> DictionarySuggestion:
    return DictionarySuggestion(
        entry_id=entry.id,
        simplified=entry.simplified,
        traditional=entry.traditional,
        primary_pinyin=entry.pinyin,
        available_languages=["en"],
        source=entry.source,
        source_revision=imported.revision,
    )


class DictionaryService:
    def __init__(self, repository: DictionaryRepository):
        self.repository = repository

    async def search(self, query: DictionaryQuery) -> DictionarySearchResult:
        rows = await self.repository.search(query)
        next_offset = query.offset + query.limit
        return DictionarySearchResult(
            items=[suggestion(entry, imported) for entry, imported in rows[: query.limit]],
            next_offset=next_offset if len(rows) > query.limit and next_offset <= 1000 else None,
        )

    async def get_entry(self, entry_id: UUID) -> DictionaryDetail:
        row = await self.repository.get_entry(entry_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Dictionary entry not found")
        entry, imported = row
        # Literal character forms only; this is intentionally not a lexical sense join.
        characters = set(entry.simplified) | set(entry.traditional or "")
        annotations = await self.repository.character_enrichments(characters)
        character_info = []
        for annotation, origin in annotations:
            known_forms = {annotation.hanzi, annotation.traditional} - {None}
            matched_forms = [
                form
                for form in dict.fromkeys(entry.simplified + (entry.traditional or ""))
                if form in known_forms
            ]
            if matched_forms:
                character_info.append(
                    DictionaryCharacterInfo(
                        form=matched_forms[0],
                        positions=[
                            i for i, char in enumerate(entry.simplified) if char in known_forms
                        ],
                        traditional_positions=[
                            i
                            for i, char in enumerate(entry.traditional or "")
                            if char in known_forms
                        ],
                        source_hanzi=annotation.hanzi,
                        traditional=annotation.traditional,
                        pinyin=annotation.pinyin,
                        sino_vietnamese=annotation.sino_vietnamese,
                        vietnamese_gloss=annotation.vietnamese_gloss,
                        matches_entry_pronunciation=(
                            annotation.pinyin == entry.pinyin
                            if len(entry.simplified) == 1
                            else None
                        ),
                        provenance=CharacterEnrichmentProvenance(
                            **{
                                name: getattr(origin, name)
                                for name in CharacterEnrichmentProvenance.model_fields
                            }
                        ),
                    )
                )
        return DictionaryDetail(
            **suggestion(entry, imported).model_dump(),
            pinyin_numbered=entry.pinyin_numbered,
            citation_pinyin=entry.pinyin,
            meanings={
                "en": [
                    DictionarySense(sense_number=i, gloss=gloss)
                    for i, gloss in enumerate(entry.english_glosses, 1)
                ]
            },
            active=entry.active,
            character_enrichments=character_info,
            provenance=DictionaryProvenance(
                **{name: getattr(imported, name) for name in DictionaryProvenance.model_fields}
            ),
        )
