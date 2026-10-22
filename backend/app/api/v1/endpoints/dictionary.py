from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.dependencies.authentication import Database, current_user_id
from app.repositories.dictionary import DictionaryRepository
from app.schemas.dictionary import DictionaryDetail, DictionaryQuery, DictionarySearchResult
from app.services.dictionary import DictionaryService

router = APIRouter(
    prefix="/dictionary", tags=["dictionary"], dependencies=[Depends(current_user_id)]
)


def dictionary_service(session: Database) -> DictionaryService:
    return DictionaryService(DictionaryRepository(session))


Service = Annotated[DictionaryService, Depends(dictionary_service)]


@router.get("/search", response_model=DictionarySearchResult)
async def search(query: Annotated[DictionaryQuery, Query()], service: Service):
    return await service.search(query)


@router.get("/entries/{entry_id}", response_model=DictionaryDetail)
async def detail(entry_id: UUID, service: Service):
    return await service.get_entry(entry_id)
