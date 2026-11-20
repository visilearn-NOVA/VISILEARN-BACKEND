"""
VisiLearn API v1 master router.
Aggregates all domain-specific routers into a unified namespace.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    students,
    academics,
    surveys,
    predictions,
    analytics,
)

api_router = APIRouter()

# Mount Domain Routers
api_router.include_router(auth.router)
api_router.include_router(students.router)
api_router.include_router(academics.router)
api_router.include_router(surveys.router)
api_router.include_router(predictions.router)
api_router.include_router(analytics.router)


@api_router.get("/health", tags=["System Health"])
def api_v1_health_check():
    """
    API v1 health status endpoint.
    """
    return {
        "status": "healthy",
        "api_version": "v1",
        "service": "VisiLearn Backend API"
    }
