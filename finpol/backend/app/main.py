"""FastAPI application entry point with async support.

This module provides:
- FastAPI app initialization
- Async lifespan management
- Middleware configuration
- Global exception handling
- Dependency injection setup
"""
import logging
import warnings
from contextlib import asynccontextmanager
from uuid import uuid4

# Suppress deprecation warnings from third-party libraries
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message="distutils Version classes are deprecated")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

from app.config import settings
from app.api.router import api_router
from app.utils.logger import setup_logger, get_logger

# Setup logger
logger = setup_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    
    Handles startup and shutdown tasks:
    - Logging configuration
    - Service initialization
    - Resource cleanup
    """
    logger.info(f"Starting {settings.app_name} v{settings.api_version}")
    logger.info(f"Server running on {settings.host}:{settings.port}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Startup tasks
    try:
        # Initialize services lazily via dependency injection
        # This avoids loading ML models at startup
        logger.info("Services ready for lazy initialization via DI")
        
        if settings.debug:
            logger.warning("Debug mode enabled - do not use in production")
            
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise
    
    yield
    
    # Shutdown tasks
    logger.info("Shutting down FinPol API")
    
    # Cleanup resources
    try:
        from app.dependencies import ServiceFactory
        ServiceFactory.clear_instances()
        logger.info("Service instances cleared")
    except Exception as e:
        logger.warning(f"Cleanup warning: {e}")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.api_version,
    description="FinPol - AI-Powered Fintech Compliance Monitoring System",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
)


# ============================================================
# Middleware Configuration
# ============================================================

# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID to each request for tracing."""
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log incoming requests with timing."""
    logger = get_logger(__name__)
    
    # Skip logging for docs endpoints
    if request.url.path not in ["/docs", "/redoc", "/openapi.json"]:
        logger.info(f"Request: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    if request.url.path not in ["/docs", "/redoc", "/openapi.json"]:
        logger.info(f"Response: {response.status_code}")
    
    return response


# Configure CORS using settings
app.add_middleware(
    CORSMiddleware,
    **settings.get_cors_config()
)


# ============================================================
# Exception Handlers
# ============================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unhandled exceptions."""
    logger = get_logger(__name__)
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "request_id": getattr(request.state, "request_id", None),
            "path": str(request.url.path)
        }
    )


# ============================================================
# API Routes
# ============================================================

# Include API router with configured prefix
app.include_router(api_router, prefix=settings.api_prefix)


# ============================================================
# Health & Info Endpoints
# ============================================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to FinPol API",
        "version": settings.api_version,
        "description": "AI-Powered Fintech Compliance Monitoring",
        "docs": "/docs" if settings.debug else "Disabled",
        "endpoints": {
            "health": "/health",
            "api_docs": "/docs" if settings.debug else None,
            "transactions": f"{settings.api_prefix}/transactions",
            "compliance": f"{settings.api_prefix}/compliance"
        }
    }


# ============================================================
# OpenAPI Schema Customization
# ============================================================

def custom_openapi():
    """Customize OpenAPI schema."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "description": "JWT token authentication"
        }
    }
    
    # Make all endpoints require auth (optional)
    # openapi_schema["security"] = [{"Bearer": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# ============================================================
# Main Entry Point
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
