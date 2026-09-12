"""
API v1 Router aggregation
"""

from fastapi import APIRouter
from .sessions import router as sessions_router
from .documents import router as documents_router

router = APIRouter()
router.include_router(sessions_router)
router.include_router(documents_router)
