import logging
from pathlib import Path
from typing import Dict, Any, Optional
import joblib
import pandas as pd
from sklearn.pipeline import Pipeline
from ..core.config import settings
from ..utils.errors import ModelNotLoadedError, PredictionExecutionError

logger = logging.getLogger(__name__)

# Exact feature names expected by the trained pipeline
NUMERICAL_FEATURES = [
    'area_sqft',
    'bhk',
    'bathroom',
    'balcony',
    'floor_num',
    'total_floors',
]

CATEGORICAL_FEATURES = [
    'location',
    'Furnishing',
    'Transaction',
    'facing',
    'Ownership',
]

FEATURE_CONTRACT = NUMERICAL_FEATURES + CATEGORICAL_FEATURES

class ModelService:
    def __init__(self, model_path: Optional[Path] = None):
        self.model_path = model_path or settings.MODEL_PATH
        self._pipeline: Optional[Pipeline] = None
        self._is_loaded: bool = False

    def load(self) -> None:
        """Loads the Scikit-Learn Pipeline artifact once into memory."""
        if not self.model_path.exists():
            logger.error(f"Model artifact not found at: {self.model_path}")
            raise ModelNotLoadedError(f"Model artifact not found at {self.model_path}")
        
        try:
            self._pipeline = joblib.load(self.model_path)
            self._is_loaded = True
            logger.info(f"ML Model Pipeline successfully loaded from {self.model_path}")
        except Exception as e:
            logger.exception(f"Failed to load ML model artifact: {str(e)}")
            raise ModelNotLoadedError(f"Failed to load ML model: {str(e)}")

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded and self._pipeline is not None

    def predict(self, feature_data: Dict[str, Any]) -> float:
        """
        Executes house price inference on the provided feature dictionary.
        
        Parameters:
            feature_data (dict): Validated dictionary matching FEATURE_CONTRACT.
            
        Returns:
            float: Predicted house price in Indian Rupees (INR).
        """
        if not self.is_loaded or self._pipeline is None:
            raise ModelNotLoadedError("Model is not initialized or loaded.")
        
        try:
            # Construct a DataFrame matching exact column names and expected types
            row_data = {
                'area_sqft': float(feature_data['area_sqft']),
                'bhk': float(feature_data['bhk']),
                'bathroom': float(feature_data['bathroom']),
                'balcony': float(feature_data['balcony']),
                'floor_num': float(feature_data['floor_num']),
                'total_floors': float(feature_data['total_floors']),
                'location': str(feature_data['location']).strip().lower(),
                'Furnishing': str(feature_data['Furnishing']),
                'Transaction': str(feature_data['Transaction']),
                'facing': str(feature_data['facing']),
                'Ownership': str(feature_data['Ownership']),
            }
            
            df_input = pd.DataFrame([row_data], columns=FEATURE_CONTRACT)
            
            # Perform inference through the encapsulated pipeline
            raw_prediction = self._pipeline.predict(df_input)[0]
            
            # Return finite positive float
            predicted_val = float(raw_prediction)
            return max(0.0, predicted_val)
            
        except Exception as e:
            logger.exception(f"Error during model prediction: {str(e)}")
            raise PredictionExecutionError(f"Prediction failed: {str(e)}")

model_service = ModelService()
