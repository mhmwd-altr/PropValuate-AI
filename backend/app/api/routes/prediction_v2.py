import logging
from fastapi import APIRouter, status
from ...schemas.prediction_v2 import (
    PredictionRequestV2,
    PredictionResponseV2,
    EngineeredFeaturesMetadata,
)
from ...services.model_service_v2 import model_service_v2
from ...services.feature_service import feature_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Valuation V2"])

@router.post(
    "/predict",
    response_model=PredictionResponseV2,
    status_code=status.HTTP_200_OK,
    summary="Estimate Property Valuation (Engine V2)",
    description=(
        "Estimates residential property valuation using Valuation Engine V2 "
        "(HistGradientBoosting pipeline). Automatically performs geospatial feature "
        "engineering (great-circle distances to Tier-1 metros, spatial density proxy, "
        "and municipality group resolution) from raw property and coordinate inputs."
    ),
)
async def predict_v2(request: PredictionRequestV2) -> PredictionResponseV2:
    # 1. Extract validated request fields
    raw_inputs = request.model_dump()
    
    # 2. Derive 16-feature schema via Feature Engineering Service
    features = feature_service.construct_v2_features(raw_inputs)
    
    # 3. Execute inference through cached V2 model pipeline
    predicted_inr = model_service_v2.predict(features)
    predicted_lakhs = round(predicted_inr / 100000.0, 2)
    
    # 4. Construct response with engineered metadata
    return PredictionResponseV2(
        status="success",
        predicted_price=round(predicted_inr, 2),
        predicted_price_lakhs=predicted_lakhs,
        currency="INR",
        model_version="2.0.0",
        model_name="Valuation Engine V2 (HistGradientBoosting)",
        engineered_features=EngineeredFeaturesMetadata(
            area_per_bhk=features["area_per_bhk"],
            dist_nearest_metro_km=features["dist_nearest_metro_km"],
            dist_mumbai_km=features["dist_mumbai_km"],
            dist_delhi_km=features["dist_delhi_km"],
            dist_bangalore_km=features["dist_bangalore_km"],
            city_grouped=features["city_grouped"],
        )
    )
