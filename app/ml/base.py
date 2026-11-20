"""
Abstract Base Predictor Interface.
Establishes the contract for both placeholder and production machine learning models.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
import pandas as pd


class BasePredictor(ABC):
    """
    Abstract interface for machine learning predictors in VisiLearn.
    Allows transparent switching between mock placeholders and trained Scikit-learn models.
    """

    @abstractmethod
    def is_ready(self) -> bool:
        """
        Returns True if a real trained model is loaded and ready to infer; False otherwise.
        """
        pass

    @abstractmethod
    def predict(self, features: pd.DataFrame) -> Dict[str, Any]:
        """
        Accepts a preprocessed Pandas DataFrame containing student features.
        Returns a dictionary with predicted_gpa, performance_category, and model metadata.
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Returns model metadata including algorithm name, version, training date, and status.
        """
        pass
