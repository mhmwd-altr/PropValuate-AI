# pyrefly: ignore [missing-import]
from fastapi import APIRouter, status
from ...schemas.prediction import HealthResponse
from ...services.model_service import model_service
from ...services.model_service_v2 import model_service_v2
from ...services.location_service import location_service
from ...core.config import settings

router = APIRouter(tags=["Health"])

@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Service Health Check",
    description="Returns the operational status of the API, confirming whether ML models and locations are loaded.",
)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        model_loaded=model_service.is_loaded,
        v2_model_loaded=model_service_v2.is_loaded,
        locations_loaded=location_service.is_loaded,
        version=settings.VERSION
    )
