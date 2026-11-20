"""
Prediction Service orchestrating feature gathering, preprocessing, ML inference, and audit logging.
"""

from typing import Any, Dict, List, Optional
import uuid
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.ml.model_loader import get_predictor
from app.ml.preprocessing import MLPreprocessor
from app.models.student import Student
from app.repositories.academic_repository import AcademicRepository
from app.repositories.prediction_repository import PredictionRepository
from app.repositories.student_repository import StudentRepository
from app.repositories.survey_repository import SurveyRepository
from app.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
    PredictionResult,
    ModelInfoResponse,
)


class PredictionService:
    """
    Business logic layer for academic predictions and machine learning lifecycle.
    """

    @classmethod
    def assemble_student_features(
        cls,
        db: Session,
        student: Student,
        override_features: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Gathers features from the student profile, latest academic record,
        and latest questionnaire survey response.
        """
        features: Dict[str, Any] = {
            "current_level": student.current_level,
            "department": student.department,
            "programme": student.programme,
        }

        # 1. Fetch academic history
        latest_record = AcademicRepository.get_latest_record(db, student.id)
        if latest_record:
            features["cumulative_gpa"] = latest_record.cumulative_gpa
            features["total_credits_earned"] = latest_record.total_credits_earned
        else:
            features["cumulative_gpa"] = 3.0  # Baseline median assumption

        # 2. Fetch latest survey response
        latest_survey = SurveyRepository.get_latest_by_student(db, student.id)
        if latest_survey:
            features["study_hours_per_week"] = latest_survey.study_hours_per_week
            features["attendance_rate_pct"] = latest_survey.attendance_rate_pct
            features["sleep_hours_per_night"] = latest_survey.sleep_hours_per_night
            features["travel_time_minutes"] = latest_survey.travel_time_minutes
            features["internet_access"] = latest_survey.internet_access
            features["class_participation"] = latest_survey.class_participation
            features["parental_education"] = latest_survey.parental_education
            features["social_media_hours_per_day"] = latest_survey.social_media_hours_per_day
            features["participates_extracurricular"] = latest_survey.participates_extracurricular
            features["stress_level"] = latest_survey.stress_level
            features["financial_support"] = latest_survey.financial_support

        # 3. Apply optional overrides (for scenario simulations)
        if override_features:
            features.update(override_features)

        return features

    @classmethod
    def generate_prediction(
        cls,
        db: Session,
        request: PredictionRequest
    ) -> PredictionResponse:
        """
        End-to-end prediction pipeline:
        1. Validate target student existence
        2. Assemble feature vector
        3. Validate feature values
        4. Apply preprocessing pipeline
        5. Invoke ML predictor
        6. Persist to DB if real prediction generated
        7. Return structured outcome
        """
        student = StudentRepository.get_by_id(db, request.student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with ID '{request.student_id}' does not exist."
            )

        # 1. Assemble raw features
        raw_features = cls.assemble_student_features(db, student, request.override_features)

        # 2. Validate feature sanity
        is_valid, validation_errors = MLPreprocessor.validate_raw_features(raw_features)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"message": "Feature validation failed", "errors": validation_errors}
            )

        # 3. Transform features into ML-ready DataFrame
        features_df = MLPreprocessor.transform(raw_features)

        # 4. Invoke Predictor
        predictor = get_predictor()
        inference = predictor.predict(features_df)

        # 5. Check if model is still a placeholder (Phase 1-4)
        if not predictor.is_ready():
            return PredictionResponse(
                success=False,
                prediction=PredictionResult(
                    predicted_gpa=None,
                    performance_category=None,
                    confidence_score=None,
                    model_version=inference["model_version"],
                    model_name=inference["model_name"],
                    status="model_unavailable",
                    message=inference["message"]
                )
            )

        # 6. Model is ready (Phase 5 production) -> Persist prediction and audit history
        saved_prediction = PredictionRepository.save_prediction(
            db=db,
            student_id=student.id,
            model_name=inference["model_name"],
            model_version=inference["model_version"],
            predicted_gpa=inference["predicted_gpa"],
            performance_category=inference["performance_category"],
            confidence_score=inference.get("confidence_score"),
            features_snapshot=raw_features,
            change_reason="Automated ML Inference via Prediction API"
        )

        return PredictionResponse(
            success=True,
            prediction=PredictionResult(
                predicted_gpa=saved_prediction.predicted_gpa,
                performance_category=saved_prediction.performance_category,
                confidence_score=saved_prediction.confidence_score,
                model_version=saved_prediction.model_version,
                model_name=saved_prediction.model_name,
                status="success",
                message="Prediction successfully generated and recorded."
            )
        )

    @classmethod
    def get_latest_prediction(cls, db: Session, student_id: uuid.UUID):
        """
        Retrieves the latest prediction for a student.
        """
        prediction = PredictionRepository.get_latest_by_student(db, student_id)
        if not prediction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No predictions found for this student."
            )
        return prediction

    @classmethod
    def get_prediction_history(cls, db: Session, student_id: uuid.UUID, skip: int = 0, limit: int = 50):
        """
        Retrieves the prediction history timeline for a student.
        """
        return PredictionRepository.list_history(db, student_id, skip=skip, limit=limit)

    @classmethod
    def get_model_info(cls) -> ModelInfoResponse:
        """
        Returns metadata on the active ML model.
        """
        predictor = get_predictor()
        info = predictor.get_model_info()
        return ModelInfoResponse(**info)
