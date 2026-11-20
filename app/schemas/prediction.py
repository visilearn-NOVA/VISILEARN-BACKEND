"""
Pydantic schemas for Machine Learning Predictions and Prediction History.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field, ConfigDict


class PredictionRequest(BaseModel):
    """
    Request payload to trigger a performance prediction.
    Automatically fetches student records and survey data from DB,
    with optional override features for 'what-if' sensitivity simulations.
    """
    student_id: uuid.UUID = Field(..., description="Target student profile UUID")
    override_features: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional feature overrides for simulation (e.g. increase study hours)"
    )


class PredictionResult(BaseModel):
    """
    Structured outcome of the machine learning inference.
    """
    predicted_gpa: Optional[float] = Field(None, description="Predicted GPA (0.00 to 5.00)")
    performance_category: Optional[str] = Field(None, description="Class honours or risk category")
    confidence_score: Optional[float] = Field(None, description="Model certainty metric")
    model_version: str
    model_name: str
    status: str
    message: Optional[str] = None


class PredictionResponse(BaseModel):
    """
    Standard JSON response returned by the prediction endpoint.
    """
    success: bool
    prediction: PredictionResult


class PredictionHistoryResponse(BaseModel):
    """
    Historical prediction snapshot representation.
    """
    id: uuid.UUID
    prediction_id: uuid.UUID
    student_id: uuid.UUID
    change_reason: str
    prior_predicted_gpa: Optional[float]
    new_predicted_gpa: float
    model_version: str
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ModelInfoResponse(BaseModel):
    """
    Public metadata detailing current ML model status.
    """
    status: str
    is_ready: bool
    model_name: str
    model_version: str
    supported_algorithms: Optional[List[str]] = None
    metrics: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
