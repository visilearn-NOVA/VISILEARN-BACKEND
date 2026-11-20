"""
Tests for Machine Learning Integration and Prediction Endpoints.
Validates feature preprocessing, placeholder status, and model lifecycle handling.
"""

import uuid
import pytest
from app.ml.preprocessing import MLPreprocessor, categorize_gpa
from app.ml.model_loader import get_predictor


def test_gpa_categorization():
    """
    Tests grading scale categorization logic.
    """
    assert categorize_gpa(4.85) == "First Class Honours"
    assert categorize_gpa(3.90) == "Second Class Upper"
    assert categorize_gpa(2.80) == "Second Class Lower"
    assert categorize_gpa(1.80) == "Third Class"
    assert categorize_gpa(1.20) == "At-Risk / Academic Probation"


def test_preprocessor_validation():
    """
    Ensures impossible feature values are flagged as errors.
    """
    valid, errors = MLPreprocessor.validate_raw_features({
        "attendance_rate_pct": 115.0,  # Invalid: > 100
        "study_hours_per_week": 200.0,  # Invalid: > 168
    })
    assert valid is False
    assert len(errors) == 2


def test_preprocessor_transform():
    """
    Validates ordinal encoding and missing value imputation.
    """
    raw = {
        "study_hours_per_week": 14.0,
        "attendance_rate_pct": 82.5,
        "internet_access": "good",
        "stress_level": "low",
        "participates_extracurricular": True,
    }
    df = MLPreprocessor.transform(raw)

    assert df.shape == (1, 13)
    assert df["internet_access_encoded"].iloc[0] == 3  # 'good' -> 3
    assert df["stress_level_encoded"].iloc[0] == 1  # 'low' -> 1
    assert df["participates_extracurricular"].iloc[0] == 1
    assert df["sleep_hours_per_night"].iloc[0] == 7.0  # Imputed default


def test_prediction_placeholder_response(client, auth_headers):
    """
    Verifies that when the model is in training (placeholder), the API returns
    a clear message indicating unintegrated status and NEVER generates fake numbers.
    """
    admin_id = uuid.uuid4()
    headers = auth_headers(admin_id, role="admin")

    # Create a student
    student_res = client.post("/api/v1/students", json={
        "matric_number": "ML/2021/001",
        "department": "Computer Science",
        "programme": "B.Sc. Computer Science",
        "current_level": 300,
        "gender": "female"
    }, headers=headers)
    student_id = student_res.json()["id"]

    # Trigger prediction
    pred_res = client.post("/api/v1/predictions/predict", json={
        "student_id": student_id
    }, headers=headers)

    assert pred_res.status_code == 200
    data = pred_res.json()
    assert data["success"] is False
    assert data["prediction"]["status"] == "model_unavailable"
    assert data["prediction"]["predicted_gpa"] is None
    assert "not yet" in data["prediction"]["message"].lower()


def test_model_info_endpoint(client, auth_headers):
    """
    Tests model diagnostic inspection endpoint.
    """
    headers = auth_headers(uuid.uuid4(), role="faculty")
    res = client.get("/api/v1/predictions/model-info", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert "model_name" in data
