import logging
from pathlib import Path
from typing import Dict, Any, Optional
import joblib
import pandas as pd
from sklearn.pipeline import Pipeline
from ..core.config import settings
from ..utils.errors import ModelNotLoadedError, PredictionExecutionError
from .feature_service import feature_service, FEATURE_CONTRACT_V2

logger = logging.getLogger(__name__)

class ModelServiceV2:
    """
    Dedicated Model Service for Valuation Engine V2 candidate model (house_price_v2.pkl).
    Manages lifecycle, memory caching, and inference execution.
    """

    def __init__(self, model_path: Optional[Path] = None):
        self.model_path = model_path or settings.MODEL_V2_PATH
        self._pipeline: Optional[Pipeline] = None
        self._is_loaded: bool = False

    def load(self) -> None:
        """Loads the Scikit-Learn V2 Pipeline artifact once into memory."""
        if not self.model_path.exists():
            logger.error(f"V2 Model artifact not found at: {self.model_path}")
            raise ModelNotLoadedError(f"V2 Model artifact not found at {self.model_path}")
        
        try:
            self._pipeline = joblib.load(self.model_path)
            self._is_loaded = True
            logger.info(f"Valuation Engine V2 Pipeline successfully loaded from {self.model_path}")
        except Exception as e:
            logger.exception(f"Failed to load V2 ML model artifact: {str(e)}")
            raise ModelNotLoadedError(f"Failed to load V2 ML model: {str(e)}")

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded and self._pipeline is not None

    def predict(self, feature_data: Dict[str, Any]) -> float:
        """
        Executes house price inference on the provided 16-feature dictionary.
        
        Parameters:
            feature_data (dict): Feature dictionary matching FEATURE_CONTRACT_V2.
            
        Returns:
            float: Estimated valuation in Indian Rupees (INR).
        """
        if not self.is_loaded or self._pipeline is None:
            raise ModelNotLoadedError("V2 Model is not initialized or loaded.")
        
        try:
            # Construct DataFrame matching exact feature contract
            df_input = feature_service.to_dataframe(feature_data)
            
            # Perform inference through the encapsulated V2 pipeline
            raw_prediction = self._pipeline.predict(df_input)[0]
            
            # Ensure finite, strictly positive output
            predicted_val = float(raw_prediction)
            return max(0.0, predicted_val)
            
        except Exception as e:
            logger.exception(f"Error during V2 model prediction: {str(e)}")
            raise PredictionExecutionError(f"V2 Prediction failed: {str(e)}")

model_service_v2 = ModelServiceV2()
