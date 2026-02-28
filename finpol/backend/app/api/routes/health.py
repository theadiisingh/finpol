"""Health check routes."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "FinPol API"}


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    return {"ready": True}
