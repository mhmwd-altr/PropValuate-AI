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

    # Language AI & LLM Provider Configuration
    LLM_MODEL_PATH: Path = BASE_DIR.parent / "data" / "models" / "qwen2.5-3b-instruct-q4_k_m.gguf"
    LLM_PROVIDER_TYPE: str = os.getenv("LLM_PROVIDER_TYPE", "local")  # "local" or "mock"
    LLM_CONTEXT_WINDOW: int = int(os.getenv("LLM_CONTEXT_WINDOW", "2048"))
    LLM_THREADS: int = int(os.getenv("LLM_THREADS", "4"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "180"))
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    
    # Assistant Session Limits
    SESSION_TTL_MINUTES: int = int(os.getenv("SESSION_TTL_MINUTES", "30"))
    SESSION_MAX_MESSAGES: int = int(os.getenv("SESSION_MAX_MESSAGES", "10"))
    MAX_USER_MESSAGE_LENGTH: int = int(os.getenv("MAX_USER_MESSAGE_LENGTH", "1000"))

settings = Settings()
