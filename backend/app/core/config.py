import os
from pathlib import Path
from typing import List
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "House Price Prediction API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = (
        "Production-ready FastAPI backend for residential house price prediction in India. "
        "Built on a validated Scikit-Learn Pipeline combining automated preprocessing and "
        "HistGradientBoostingRegressor."
    )
    
    # Base directory resolution
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    
    # Artifact paths
    MODEL_PATH: Path = BASE_DIR / "models" / "house_price.pkl"
    MODEL_V2_PATH: Path = BASE_DIR / "models" / "house_price_v2.pkl"
    LOCATIONS_PATH: Path = BASE_DIR / "models" / "locations.json"
    
    # Model Versions
    BASELINE_VERSION: str = "1.0.0"
    V2_VERSION: str = "2.0.0"
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

settings = Settings()
