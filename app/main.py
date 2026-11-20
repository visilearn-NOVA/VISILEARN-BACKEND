"""
VisiLearn Backend Main Application Entrypoint.
Initializes the FastAPI application, registers middleware, handles exceptions,
and mounts API routers.
"""

from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.v1.router import api_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("visilearn.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle events: executes startup and shutdown logic.
    """
    logger.info("Initializing %s in %s mode...", settings.PROJECT_NAME, settings.ENVIRONMENT)
    logger.info("PostgreSQL target: %s:%s/%s", settings.POSTGRES_SERVER, settings.POSTGRES_PORT, settings.POSTGRES_DB)
    logger.info("ML Active Model Version: %s", settings.ACTIVE_MODEL_VERSION)
    yield
    logger.info("Shutting down %s...", settings.PROJECT_NAME)


# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Student Performance Analytics System — Predicting and Visualising Academic Success",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Cross-Origin Resource Sharing (CORS) Middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception processing request to %s: %s", request.url.path, str(exc), exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "InternalServerError",
            "message": "An unexpected error occurred. Please contact the administrator.",
            "path": request.url.path,
        }
    )


# Mount API v1 Master Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
def root():
    """
    Root discovery endpoint providing welcome metadata and docs links.
    """
    return {
        "project": settings.PROJECT_NAME,
        "version": "1.0.0",
        "status": "online",
        "documentation": "/docs",
        "redoc": "/redoc",
        "api_v1": settings.API_V1_STR
    }


@app.get("/health", tags=["Root"])
def health():
    """
    System-level health check endpoint for monitoring, Docker healthchecks, and load balancers.
    """
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "database_configured": bool(settings.POSTGRES_SERVER)
    }
