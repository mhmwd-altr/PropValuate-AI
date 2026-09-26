from fastapi import APIRouter
from .routes.health import router as health_router
from .routes.locations import router as locations_router
from .routes.prediction import router as prediction_router
from .routes.prediction_v2 import router as prediction_v2_router

api_router = APIRouter()

# Unversioned baseline endpoints (protected contracts)
api_router.include_router(health_router)
api_router.include_router(locations_router)
api_router.include_router(prediction_router)

# Version 2 API endpoints
api_router.include_router(prediction_v2_router, prefix="/api/v2")

__all__ = ["api_router"]

