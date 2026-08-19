from fastapi import APIRouter
from .routes.health import router as health_router
from .routes.locations import router as locations_router
from .routes.prediction import router as prediction_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(locations_router)
api_router.include_router(prediction_router)

__all__ = ["api_router"]
