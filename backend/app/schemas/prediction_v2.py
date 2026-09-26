from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, model_validator

class PredictionRequestV2(BaseModel):
    area_sqft: float = Field(
        ...,
        gt=0,
        le=50000,
        description="Property area in square feet (sqft)",
        examples=[1500.0]
    )
    bhk: int = Field(
        ...,
        ge=1,
        le=20,
        description="Number of bedrooms (BHK: 1 to 20)",
        examples=[3]
    )
    latitude: float = Field(
        ...,
        ge=6.0,
        le=38.0,
        description="Geographical latitude in decimal degrees ([6.0, 38.0] for India)",
        examples=[12.9716]
    )
    longitude: float = Field(
        ...,
        ge=68.0,
        le=98.0,
        description="Geographical longitude in decimal degrees ([68.0, 98.0] for India)",
        examples=[77.5946]
    )
    city: Optional[str] = Field(
        default="other",
        description="City or municipality name (e.g., 'bangalore', 'mumbai', 'gurgaon')",
        examples=["bangalore"]
    )
    posted_by: str = Field(
        default="Owner",
        description="Listing channel entity ('Owner', 'Dealer', 'Builder')",
        examples=["Owner"]
    )
    rera: int = Field(
        default=1,
        ge=0,
        le=1,
        description="RERA regulatory approval status (1 = RERA Approved, 0 = Non-RERA)",
        examples=[1]
    )
    under_construction: int = Field(
        default=0,
        ge=0,
        le=1,
        description="Under construction lifecycle flag (1 = Under Construction, 0 = Completed)",
        examples=[0]
    )
    ready_to_move: int = Field(
        default=1,
        ge=0,
        le=1,
        description="Immediate possession availability (1 = Ready to Move, 0 = Not Ready)",
        examples=[1]
    )
    resale: int = Field(
        default=1,
        ge=0,
        le=1,
        description="Transaction type (1 = Resale Property, 0 = Primary Developer Sale)",
        examples=[1]
    )
    is_rk: int = Field(
        default=0,
        ge=0,
        le=1,
        description="Room-Kitchen layout flag (1 = RK Studio layout, 0 = Standard BHK)",
        examples=[0]
    )

    @field_validator("posted_by")
    @classmethod
    def validate_posted_by(cls, v: str) -> str:
        cleaned = str(v).strip().title()
        if cleaned not in {"Owner", "Dealer", "Builder"}:
            raise ValueError(
                f"Invalid posted_by '{v}'. Must be one of: 'Owner', 'Dealer', 'Builder'."
            )
        return cleaned

    model_config = {
        "json_schema_extra": {
            "example": {
                "area_sqft": 1500.0,
                "bhk": 3,
                "latitude": 12.9716,
                "longitude": 77.5946,
                "city": "bangalore",
                "posted_by": "Owner",
                "rera": 1,
                "under_construction": 0,
                "ready_to_move": 1,
                "resale": 1,
                "is_rk": 0
            }
        }
    }

class EngineeredFeaturesMetadata(BaseModel):
    area_per_bhk: float = Field(
        ...,
        description="Calculated ratio of area to BHK (sqft per room proxy)",
        examples=[483.87]
    )
    dist_nearest_metro_km: float = Field(
        ...,
        description="Calculated great-circle distance to closest tier-1 metro core in km",
        examples=[0.0]
    )
    dist_mumbai_km: float = Field(
        ...,
        description="Calculated distance to Mumbai commercial core in km",
        examples=[841.4]
    )
    dist_delhi_km: float = Field(
        ...,
        description="Calculated distance to Delhi-NCR Connaught Place in km",
        examples=[1740.2]
    )
    dist_bangalore_km: float = Field(
        ...,
        description="Calculated distance to Bangalore MG Road core in km",
        examples=[0.0]
    )
    city_grouped: str = Field(
        ...,
        description="Standardized municipality categorical group (top 50 or 'other')",
        examples=["bangalore"]
    )

class PredictionResponseV2(BaseModel):
    status: str = Field(
        default="success",
        description="Inference response status",
        examples=["success"]
    )
    predicted_price: float = Field(
        ...,
        description="Estimated property valuation in Indian Rupees (INR)",
        examples=[9236394.38]
    )
    predicted_price_lakhs: float = Field(
        ...,
        description="Estimated property valuation in Lakhs INR (INR / 100,000)",
        examples=[92.36]
    )
    currency: str = Field(
        default="INR",
        description="Currency ISO code",
        examples=["INR"]
    )
    model_version: str = Field(
        default="2.0.0",
        description="Valuation Engine version",
        examples=["2.0.0"]
    )
    model_name: str = Field(
        default="Valuation Engine V2 (HistGradientBoosting)",
        description="Model architecture description"
    )
    engineered_features: Optional[EngineeredFeaturesMetadata] = Field(
        default=None,
        description="Derived geospatial and structural features used during inference"
    )
