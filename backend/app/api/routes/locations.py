from fastapi import APIRouter, status
from ...schemas.prediction import LocationsResponse
from ...services.location_service import location_service

router = APIRouter(tags=["Locations"])

@router.get(
    "/locations",
    response_model=LocationsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Allowed Real Estate Locations",
    description="Retrieves the full list of verified real-estate cities/localities available for house price estimation.",
)
async def get_locations() -> LocationsResponse:
    locations = location_service.get_locations()
    total = location_service.get_total_count()
    return LocationsResponse(
        total_locations=total,
        locations=locations
    )
