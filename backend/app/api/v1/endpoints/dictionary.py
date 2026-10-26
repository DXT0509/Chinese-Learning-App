from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.dependencies.authentication import Database, current_user_id
from app.schemas.curated_api import CuratedDetail, CuratedSearchResult
from app.schemas.dictionary import DictionaryQuery
from app.services.curated_catalog import CuratedCatalog

router = APIRouter(
    prefix="/dictionary", tags=["dictionary"], dependencies=[Depends(current_user_id)]
)


def dictionary_service(session: Database) -> CuratedCatalog:
    return CuratedCatalog(session)


Service = Annotated[CuratedCatalog, Depends(dictionary_service)]


@router.get("/search", response_model=CuratedSearchResult)
async def search(query: Annotated[DictionaryQuery, Query()], service: Service):
    return await service.search(query)


@router.get("/entries/{entry_id}", response_model=CuratedDetail)
async def detail(entry_id: UUID, service: Service):
    return await service.get_entry(entry_id)
