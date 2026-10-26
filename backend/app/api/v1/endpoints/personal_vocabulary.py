from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response

from app.dependencies.authentication import Database, current_user_id
from app.schemas.curated_api import CuratedSaved, CuratedVocabularyPage
from app.schemas.personal_vocabulary import (
    SaveVocabulary,
    VocabularyQuery,
    VocabularyStatus,
)
from app.services.curated_catalog import CuratedCatalog as PersonalVocabularyService

router = APIRouter(prefix="/me/vocabulary", tags=["personal vocabulary"])
Owner = Annotated[UUID, Depends(current_user_id)]


@router.get("", response_model=CuratedVocabularyPage)
async def listing(owner: Owner, session: Database, query: Annotated[VocabularyQuery, Query()]):
    return await PersonalVocabularyService(session).listing(owner, query)


@router.post("", response_model=CuratedSaved)
async def save(body: SaveVocabulary, owner: Owner, session: Database):
    return await PersonalVocabularyService(session).save(owner, body.dictionary_entry_id)


@router.get("/status", response_model=VocabularyStatus)
async def status(dictionary_entry_id: UUID, owner: Owner, session: Database):
    return VocabularyStatus(
        saved_id=await PersonalVocabularyService(session).status(owner, dictionary_entry_id)
    )


@router.get("/{saved_id}", response_model=CuratedSaved)
async def detail(saved_id: UUID, owner: Owner, session: Database):
    return await PersonalVocabularyService(session).detail(owner, saved_id)


@router.delete("/{saved_id}", status_code=204)
async def remove(saved_id: UUID, owner: Owner, session: Database):
    await PersonalVocabularyService(session).remove(owner, saved_id)
    return Response(status_code=204)
