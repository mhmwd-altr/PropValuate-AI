from typing import List, Optional
from pydantic import BaseModel, Field, model_validator

class PredictionRequest(BaseModel):
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
    bathroom: float = Field(
        ...,
        ge=1,
        le=20,
        description="Number of bathrooms (1 to 20)",
        examples=[2.0]
    )
    balcony: float = Field(
        default=1.0,
        ge=0,
        le=20,
        description="Number of balconies (0 to 20)",
        examples=[1.0]
    )
    floor_num: float = Field(
        default=1.0,
        ge=-5,
        le=200,
        description="Floor number (-1 for Basement, 0 for Ground, 1+ for standard floors)",
        examples=[4.0]
    )
    total_floors: float = Field(
        default=10.0,
        ge=1,
        le=200,
        description="Total number of floors in the building",
        examples=[10.0]
    )
    location: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Property city/locality (e.g. 'bangalore', 'mumbai', 'new-delhi')",
        examples=["bangalore"]
    )
    Furnishing: str = Field(
        default="Semi-Furnished",
        description="Furnishing status ('Furnished', 'Semi-Furnished', 'Unfurnished')",
        examples=["Semi-Furnished"]
    )
    Transaction: str = Field(
        default="Resale",
        description="Transaction type ('Resale', 'New Property', 'Other', 'Rent/Lease')",
        examples=["Resale"]
    )
    facing: str = Field(
        default="East",
        description="Facing orientation ('East', 'North', 'North - East', 'West', 'South', etc.)",
        examples=["East"]
    )
    Ownership: str = Field(
        default="Freehold",
        description="Ownership type ('Freehold', 'Leasehold', 'Co-operative Society', 'Power Of Attorney')",
        examples=["Freehold"]
    )

    @model_validator(mode='after')
    def validate_floor_numbers(self) -> 'PredictionRequest':
        if self.floor_num > 0 and self.floor_num > self.total_floors:
            raise ValueError(
                f"floor_num ({self.floor_num}) cannot exceed total_floors ({self.total_floors})"
            )
        return self

    model_config = {
        "json_schema_extra": {
            "example": {
                "area_sqft": 1500.0,
                "bhk": 3,
                "bathroom": 2.0,
                "balcony": 2.0,
                "floor_num": 4.0,
                "total_floors": 10.0,
                "location": "bangalore",
                "Furnishing": "Semi-Furnished",
                "Transaction": "Resale",
                "facing": "East",
                "Ownership": "Freehold"
            }
        }
    }

class PredictionResponse(BaseModel):
    predicted_price: float = Field(
        ...,
        description="Estimated property price in Indian Rupees (INR)",
        examples=[12465981.21]
    )
    predicted_price_lakhs: float = Field(
        ...,
        description="Estimated property price in Lakhs INR (INR / 100,000)",
        examples=[124.66]
    )
    currency: str = Field(
        default="INR",
        description="Currency code"
    )
    status: str = Field(
        default="success",
        description="Request status"
    )

class LocationsResponse(BaseModel):
    total_locations: int = Field(
        ...,
        description="Total number of verified locations",
        examples=[81]
    )
    locations: List[str] = Field(
        ...,
        description="List of verified city/location strings",
        examples=[["bangalore", "chennai", "delhi", "gurgaon", "mumbai"]]
    )

class HealthResponse(BaseModel):
    status: str = Field(
        default="ok",
        description="Overall service health status",
        examples=["ok"]
    )
    model_loaded: bool = Field(
        ...,
        description="True if the ML baseline model pipeline is loaded and ready for inference",
        examples=[True]
    )
    v2_model_loaded: bool = Field(
        default=False,
        description="True if the Valuation Engine V2 candidate model is loaded",
        examples=[True]
    )
    locations_loaded: bool = Field(
        ...,
        description="True if the locations metadata is loaded",
        examples=[True]
    )
    version: str = Field(
        ...,
        description="Backend API version",
        examples=["1.0.0"]
    )
