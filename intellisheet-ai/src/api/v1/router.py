from fastapi import APIRouter

from .endpoints.health import router as health_router
from .endpoints.rag import router as rag_router

router = APIRouter()

router.include_router(health_router)
router.include_router(rag_router)