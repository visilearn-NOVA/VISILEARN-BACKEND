"""
Placeholder Predictor for Phase 1-4.
Ensures zero fake data generation while maintaining system readiness for final trained models.
"""

from typing import Any, Dict
import pandas as pd
from app.ml.base import BasePredictor


class MockPredictor(BasePredictor):
    """
    Placeholder prediction engine active while the data science model is undergoing training.
    Explicitly reports that no model is loaded rather than returning fabricated predictions.
    """

    def __init__(self, message: str = "Trained machine learning model has not yet been integrated."):
        self.message = message
        self.version = "placeholder-0.0.0"
        self.model_name = "NotIntegratedPlaceholder"

    def is_ready(self) -> bool:
        """
        Placeholder is never ready for true scientific inferences.
        """
        return False

    def predict(self, features: pd.DataFrame) -> Dict[str, Any]:
        """
        Informs the caller of unintegrated model status without generating fake numbers.
        """
        return {
            "is_ready": False,
            "status": "model_unavailable",
            "message": self.message,
            "model_version": self.version,
            "model_name": self.model_name,
            "predicted_gpa": None,
            "performance_category": None,
            "confidence_score": None,
        }

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "status": "uncalibrated",
            "is_ready": False,
            "model_name": self.model_name,
            "model_version": self.version,
            "message": self.message,
            "supported_algorithms": [
                "RandomForestRegressor",
                "GradientBoostingRegressor",
                "LinearRegression",
                "RidgeRegressor"
            ]
        }
