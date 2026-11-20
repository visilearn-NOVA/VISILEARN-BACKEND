"""
Prediction REST Endpoints.
Provides machine learning inference execution, longitudinal history inspection, and model metadata.
"""

from typing import List
import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import (
    get_db,
    get_current_user,
    check_student_record_access,
)
from app.models.user import User
from app.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
    PredictionHistoryResponse,
    ModelInfoResponse,
)
from app.services.prediction_service import PredictionService

router = APIRouter(prefix="/predictions", tags=["Predictions & Machine Learning"])


@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Generate academic performance prediction"
)
def predict_student_performance(
    request: PredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Executes the machine learning prediction pipeline for a student.
    - Gathers demographic, academic, and behavioral questionnaire features.
    - Performs validation and ordinal/numerical preprocessing.
    - If model is unintegrated, returns a clear status message (no fake predictions).
    - If model is active, predicts GPA, categorizes performance tier, and logs audit history.
    """
    check_student_record_access(request.student_id, current_user)
    return PredictionService.generate_prediction(db, request)


@router.get(
    "/students/{student_id}",
    summary="Get latest prediction for a student"
)
def get_student_latest_prediction(
    student_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves the most recent prediction recorded for the specified student.
    """
    check_student_record_access(student_id, current_user)
    prediction = PredictionService.get_latest_prediction(db, student_id)
    return {
        "id": prediction.id,
        "student_id": prediction.student_id,
        "model_name": prediction.model_name,
        "model_version": prediction.model_version,
        "predicted_gpa": prediction.predicted_gpa,
        "performance_category": prediction.performance_category,
        "confidence_score": prediction.confidence_score,
        "input_features": prediction.input_features_snapshot,
        "created_at": prediction.created_at,
    }


@router.get(
    "/students/{student_id}/history",
    response_model=List[PredictionHistoryResponse],
    summary="Get prediction trajectory history"
)
def get_prediction_history(
    student_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves the historical timeline of predictions across academic semesters.
    """
    check_student_record_access(student_id, current_user)
    return PredictionService.get_prediction_history(db, student_id, skip=skip, limit=limit)


@router.get(
    "/model-info",
    response_model=ModelInfoResponse,
    summary="Inspect active machine learning model metadata"
)
def get_model_information(
    current_user: User = Depends(get_current_user)
):
    """
    Returns diagnostic details on the active ML model, including algorithm name,
    version, calibration status, and supported future regressors.
    """
    return PredictionService.get_model_info()
