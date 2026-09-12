"""
API v1 Router aggregation
"""

from fastapi import APIRouter
from app.api.v1.sessions import router as sessions_router

router = APIRouter()
router.include_router(sessions_router)
