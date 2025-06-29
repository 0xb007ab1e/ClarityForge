"""API v1 endpoints for ClarityForge."""

from fastapi import APIRouter

router = APIRouter(prefix="/v1", tags=["v1"])


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
