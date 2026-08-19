import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

class ModelNotLoadedError(Exception):
    """Raised when inference is requested but the ML model is not loaded."""
    def __init__(self, message: str = "Machine Learning model is not loaded."):
        self.message = message
        super().__init__(self.message)

class LocationDataNotFoundError(Exception):
    """Raised when locations.json artifact is missing or corrupt."""
    def __init__(self, message: str = "Locations metadata artifact is not available."):
        self.message = message
        super().__init__(self.message)

class PredictionExecutionError(Exception):
    """Raised when an internal error occurs during model inference execution."""
    def __init__(self, message: str = "An error occurred during price prediction."):
        self.message = message
        super().__init__(self.message)

async def model_not_loaded_handler(request: Request, exc: ModelNotLoadedError) -> JSONResponse:
    logger.error(f"ModelNotLoadedError on {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": exc.message, "error_type": "ModelNotLoadedError"}
    )

async def location_not_found_handler(request: Request, exc: LocationDataNotFoundError) -> JSONResponse:
    logger.error(f"LocationDataNotFoundError on {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": exc.message, "error_type": "LocationDataNotFoundError"}
    )

async def prediction_error_handler(request: Request, exc: PredictionExecutionError) -> JSONResponse:
    logger.error(f"PredictionExecutionError on {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": exc.message, "error_type": "PredictionExecutionError"}
    )

async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(f"Unhandled exception on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error. Please try again later.", "error_type": "InternalServerError"}
    )
