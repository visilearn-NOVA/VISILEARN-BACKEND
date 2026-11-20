"""
Production Scikit-learn Predictor Engine.
Loads serialized models (.joblib / .pkl) and executes real inference.
"""

import json
import os
from typing import Any, Dict, Optional
import joblib
import numpy as np
import pandas as pd
from app.ml.base import BasePredictor
from app.ml.preprocessing import categorize_gpa


class ScikitLearnPredictor(BasePredictor):
    """
    Inference adapter for trained Scikit-learn regression models
    (RandomForestRegressor, GradientBoostingRegressor, Ridge, etc.).
    """

    def __init__(
        self,
        model_path: str,
        metadata_path: Optional[str] = None
    ):
        self.model_path = model_path
        self.metadata_path = metadata_path
        self.model = None
        self.model_name = "ScikitLearnModel"
        self.version = "v1.0.0"
        self.metrics = {}
        self._load()

    def _load(self):
        """
        Loads the model from disk and reads companion metadata if present.
        """
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found at {self.model_path}")

        self.model = joblib.load(self.model_path)

        if self.metadata_path and os.path.exists(self.metadata_path):
            try:
                with open(self.metadata_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    self.model_name = meta.get("model_name", type(self.model).__name__)
                    self.version = meta.get("version", "v1.0.0")
                    self.metrics = meta.get("metrics", {})
            except Exception:
                self.model_name = type(self.model).__name__
        else:
            self.model_name = type(self.model).__name__

    def is_ready(self) -> bool:
        return self.model is not None

    def predict(self, features: pd.DataFrame) -> Dict[str, Any]:
        """
        Executes prediction on the preprocessed feature vector.
        """
        if not self.is_ready():
            raise RuntimeError("Model is not initialized.")

        # Generate numerical regression output
        raw_pred = self.model.predict(features)
        predicted_gpa = float(raw_pred[0])

        # Clip GPA to institutional boundaries (0.00 to 5.00)
        clipped_gpa = max(0.0, min(5.0, predicted_gpa))
        rounded_gpa = round(clipped_gpa, 2)

        # Performance categorization
        category = categorize_gpa(rounded_gpa)

        # Confidence estimation for ensemble models (e.g. tree variance)
        confidence = None
        if hasattr(self.model, "estimators_"):
            try:
                tree_predictions = [tree.predict(features.values)[0] for tree in self.model.estimators_]
                std_dev = float(np.std(tree_predictions))
                # Lower variance implies higher agreement / confidence
                confidence = round(max(0.5, 1.0 - (std_dev / 2.0)), 3)
            except Exception:
                confidence = 0.85

        return {
            "is_ready": True,
            "status": "success",
            "predicted_gpa": rounded_gpa,
            "performance_category": category,
            "confidence_score": confidence,
            "model_version": self.version,
            "model_name": self.model_name,
        }

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "status": "ready",
            "is_ready": True,
            "model_name": self.model_name,
            "model_version": self.version,
            "metrics": self.metrics,
            "model_type": type(self.model).__name__,
        }
