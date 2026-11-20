"""
Model Loader and Lifecycle Manager.
Discovers and loads active machine learning model artifacts or safely activates the placeholder.
"""

import logging
import os
from typing import Optional
from app.core.config import settings
from app.ml.base import BasePredictor
from app.ml.mock_predictor import MockPredictor
from app.ml.scikit_predictor import ScikitLearnPredictor

logger = logging.getLogger("visilearn.ml.loader")

_ACTIVE_PREDICTOR: Optional[BasePredictor] = None


def load_active_predictor() -> BasePredictor:
    """
    Initializes the active predictor based on available model artifacts on disk.
    If no trained model is found, returns a safe MockPredictor.
    """
    global _ACTIVE_PREDICTOR

    model_dir = os.path.join(settings.ML_MODEL_DIR, settings.ACTIVE_MODEL_VERSION)
    model_file = os.path.join(model_dir, "model.joblib")
    meta_file = os.path.join(model_dir, "metadata.json")

    if os.path.exists(model_file):
        try:
            logger.info("Found trained model artifact at %s. Loading ScikitLearnPredictor...", model_file)
            _ACTIVE_PREDICTOR = ScikitLearnPredictor(model_file, meta_file)
            return _ACTIVE_PREDICTOR
        except Exception as exc:
            logger.error("Failed to load model from %s: %s. Falling back to placeholder.", model_file, str(exc))

    logger.info(
        "No trained ML model artifact located at '%s'. Activating MockPredictor placeholder (no fake predictions).",
        model_file
    )
    _ACTIVE_PREDICTOR = MockPredictor(
        message=f"Machine learning model '{settings.ACTIVE_MODEL_VERSION}' is not yet trained or integrated. Please place trained model.joblib in '{model_dir}'."
    )
    return _ACTIVE_PREDICTOR


def get_predictor() -> BasePredictor:
    """
    Retrieves the global predictor instance.
    """
    global _ACTIVE_PREDICTOR
    if _ACTIVE_PREDICTOR is None:
        _ACTIVE_PREDICTOR = load_active_predictor()
    return _ACTIVE_PREDICTOR
