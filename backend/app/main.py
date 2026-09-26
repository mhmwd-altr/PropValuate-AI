import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .services.model_service import model_service
from .services.model_service_v2 import model_service_v2
from .services.location_service import location_service
from .api import api_router
from .utils.errors import (
    ModelNotLoadedError,
    LocationDataNotFoundError,
    PredictionExecutionError,
    model_not_loaded_handler,
    location_not_found_handler,
    prediction_error_handler,
    generic_exception_handler,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("backend.app")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown lifecycle.
    Loads baseline ML model, V2 candidate model, and locations metadata once on startup.
    """
    logger.info("Starting PropValuate AI Backend...")
    try:
        model_service.load()
        model_service_v2.load()
        location_service.load()
        logger.info("All model artifacts and location data loaded successfully.")
    except Exception as e:
        logger.error(f"Critical error during startup artifact loading: {str(e)}")
    
    yield
    
    logger.info("PropValuate AI Backend shutting down.")

# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Register custom exception handlers
app.add_exception_handler(ModelNotLoadedError, model_not_loaded_handler)
app.add_exception_handler(LocationDataNotFoundError, location_not_found_handler)
app.add_exception_handler(PredictionExecutionError, prediction_error_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Register API routes
app.include_router(api_router)

@app.get("/", tags=["Root"])
async def root():
    """Returns basic API service metadata and documentation links."""
    return {
        "message": "House Price Prediction API is running.",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "endpoints": {
            "health": "/health",
            "locations": "/locations",
            "predict": "/predict",
            "predict_v2": "/api/v2/predict"
        }
    }
