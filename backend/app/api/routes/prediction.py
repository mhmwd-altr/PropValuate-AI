from fastapi import APIRouter, status
from ...schemas.prediction import PredictionRequest, PredictionResponse
from ...services.model_service import model_service

router = APIRouter(tags=["Prediction"])

@router.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict House Valuation",
    description=(
        "Estimates residential property price based on physical specifications, floor height, "
        "and geographical location using the trained Scikit-Learn Pipeline."
    ),
)
async def predict_house_price(request: PredictionRequest) -> PredictionResponse:
    # Convert validated request to feature dictionary
    feature_dict = request.model_dump()
    
    # Run inference through ML pipeline
    predicted_val_inr = model_service.predict(feature_dict)
    predicted_val_lakhs = round(predicted_val_inr / 100000.0, 2)
    
    return PredictionResponse(
        predicted_price=round(predicted_val_inr, 2),
        predicted_price_lakhs=predicted_val_lakhs,
        currency="INR",
        status="success"
    )
