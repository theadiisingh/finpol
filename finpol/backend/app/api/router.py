"""API Router - combines all route handlers."""
from fastapi import APIRouter
from app.api.routes import transactions, compliance, health

api_router = APIRouter()

# Include all route modules
api_router.include_router(health.router, tags=["health"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(compliance.router, prefix="/compliance", tags=["compliance"])
