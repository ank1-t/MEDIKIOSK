"""
API router registering all v1 endpoints
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1")

@router.get("/health", tags=["Health"])
async def v1_health():
    return {"status": "ok", "api_version": "v1"}
