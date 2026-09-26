import logging
from typing import Dict, Any, List
import pandas as pd
from .geo_service import (
    calculate_metro_distances,
    normalize_city_group,
    is_valid_india_coordinate,
)

logger = logging.getLogger(__name__)

# Exact 16-feature schema expected by the trained V2 ColumnTransformer
NUMERICAL_FEATURES_V2: List[str] = [
    "area_sqft",
    "bhk",
    "is_rk",
    "rera",
    "under_construction",
    "ready_to_move",
    "resale",
    "latitude",
    "longitude",
    "area_per_bhk",
    "dist_nearest_metro_km",
    "dist_mumbai_km",
    "dist_delhi_km",
    "dist_bangalore_km",
]

CATEGORICAL_FEATURES_V2: List[str] = [
    "posted_by",
    "city_grouped",
]

FEATURE_CONTRACT_V2: List[str] = NUMERICAL_FEATURES_V2 + CATEGORICAL_FEATURES_V2

VALID_POSTED_BY_VALUES = {"owner": "Owner", "dealer": "Dealer", "builder": "Builder"}

class FeatureEngineeringService:
    """
    Service responsible for converting raw property inputs into the exact
    16-feature matrix expected by the V2 Valuation Engine.
    """

    @staticmethod
    def normalize_posted_by(posted_by_raw: Any) -> str:
        """Normalizes transaction party to 'Owner', 'Dealer', or 'Builder'."""
        if not posted_by_raw:
            return "Owner"
        cleaned = str(posted_by_raw).strip().lower()
        return VALID_POSTED_BY_VALUES.get(cleaned, "Owner")

    @classmethod
    def construct_v2_features(cls, raw_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates and derives the full 16-feature dictionary from raw property inputs.
        
        Parameters:
            raw_input: Dictionary containing raw fields from PredictionRequestV2.
            
        Returns:
            Dict[str, Any] with all 16 features.
        """
        area_sqft = float(raw_input["area_sqft"])
        bhk = int(raw_input["bhk"])
        lat = float(raw_input["latitude"])
        lon = float(raw_input["longitude"])
        
        # Validate coordinates before calculating distances
        if not is_valid_india_coordinate(lat, lon):
            raise ValueError(
                f"Coordinates ({lat}, {lon}) are outside valid India bounding box "
                f"(Lat: [6.0, 38.0], Lon: [68.0, 98.0])"
            )
        
        # Geospatial Distance Calculations
        metro_distances = calculate_metro_distances(lat, lon)
        
        # Spatial Interaction Ratio
        area_per_bhk = area_sqft / (float(bhk) + 0.1)
        
        # Layout & Binary Flags
        is_rk = int(raw_input.get("is_rk", 0))
        rera = int(raw_input.get("rera", 1))
        under_construction = int(raw_input.get("under_construction", 0))
        ready_to_move = int(raw_input.get("ready_to_move", 1))
        resale = int(raw_input.get("resale", 1))
        
        # Categorical normalization
        posted_by = cls.normalize_posted_by(raw_input.get("posted_by", "Owner"))
        city_grouped = normalize_city_group(raw_input.get("city"))
        
        features = {
            "area_sqft": area_sqft,
            "bhk": bhk,
            "is_rk": is_rk,
            "rera": rera,
            "under_construction": under_construction,
            "ready_to_move": ready_to_move,
            "resale": resale,
            "latitude": lat,
            "longitude": lon,
            "area_per_bhk": round(area_per_bhk, 4),
            "dist_nearest_metro_km": metro_distances["dist_nearest_metro_km"],
            "dist_mumbai_km": metro_distances["dist_mumbai_km"],
            "dist_delhi_km": metro_distances["dist_delhi_km"],
            "dist_bangalore_km": metro_distances["dist_bangalore_km"],
            "posted_by": posted_by,
            "city_grouped": city_grouped,
        }
        
        return features

    @classmethod
    def to_dataframe(cls, features: Dict[str, Any]) -> pd.DataFrame:
        """Converts feature dictionary to single-row DataFrame matching FEATURE_CONTRACT_V2."""
        return pd.DataFrame([features], columns=FEATURE_CONTRACT_V2)

feature_service = FeatureEngineeringService()
