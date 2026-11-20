"""
Integration test for Scikit-learn trained model pipeline.
Creates a real Scikit-learn RandomForestRegressor, serializes it, and verifies real inference.
"""

import json
import os
import shutil
import tempfile
import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestRegressor
import joblib

from app.ml.scikit_predictor import ScikitLearnPredictor
from app.ml.preprocessing import MLPreprocessor, FEATURE_COLUMNS


@pytest.fixture
def temp_trained_model():
    """
    Creates and serializes a real synthetic RandomForestRegressor for testing.
    """
    temp_dir = tempfile.mkdtemp()
    model_path = os.path.join(temp_dir, "model.joblib")
    meta_path = os.path.join(temp_dir, "metadata.json")

    # Generate synthetic training data
    np.random.seed(42)
    X = np.random.rand(50, len(FEATURE_COLUMNS))
    y = 2.0 + 2.5 * X[:, 0] + 0.5 * X[:, 1]  # Simulated GPA
    y = np.clip(y, 0.0, 5.0)

    model = RandomForestRegressor(n_estimators=10, random_state=42)
    model.fit(X, y)
    joblib.dump(model, model_path)

    metadata = {
        "model_name": "RandomForestRegressor",
        "version": "v1.0.0-test",
        "metrics": {"r2_score": 0.82, "rmse": 0.28}
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f)

    yield model_path, meta_path

    shutil.rmtree(temp_dir)


def test_scikit_predictor_real_inference(temp_trained_model):
    """
    Tests that ScikitLearnPredictor loads a real joblib model and produces valid predictions.
    """
    model_path, meta_path = temp_trained_model
    predictor = ScikitLearnPredictor(model_path, meta_path)

    assert predictor.is_ready() is True
    info = predictor.get_model_info()
    assert info["status"] == "ready"
    assert info["model_name"] == "RandomForestRegressor"
    assert info["model_version"] == "v1.0.0-test"

    # Preprocess a sample student feature vector
    raw_features = {
        "study_hours_per_week": 16.0,
        "attendance_rate_pct": 92.0,
        "sleep_hours_per_night": 8.0,
        "travel_time_minutes": 20,
        "social_media_hours_per_day": 1.5,
        "participates_extracurricular": True,
        "internet_access": "good",
        "class_participation": "high",
        "parental_education": "tertiary",
        "stress_level": "low",
        "financial_support": "abundant",
        "current_level": 300,
        "cumulative_gpa": 4.10,
    }
    features_df = MLPreprocessor.transform(raw_features)

    # Perform inference
    result = predictor.predict(features_df)
    assert result["is_ready"] is True
    assert result["status"] == "success"
    assert 0.0 <= result["predicted_gpa"] <= 5.0
    assert result["performance_category"] in [
        "First Class Honours",
        "Second Class Upper",
        "Second Class Lower",
        "Third Class",
        "At-Risk / Academic Probation"
    ]
    assert result["confidence_score"] is not None
