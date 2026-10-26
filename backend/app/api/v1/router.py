from fastapi import APIRouter

from app.api.v1.endpoints.dictionary import router as dictionary_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.personal_vocabulary import router as personal_vocabulary_router

router = APIRouter(prefix="/api/v1")
router.include_router(health_router)
router.include_router(dictionary_router)
router.include_router(personal_vocabulary_router)
