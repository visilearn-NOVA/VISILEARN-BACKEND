"""
Prediction Repository managing persistence of ML inferences and longitudinal history logs.
"""

from typing import List, Optional
import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.prediction import Prediction, PredictionHistory


class PredictionRepository:
    """
    Data access layer for Predictions and Prediction History.
    """

    @staticmethod
    def get_latest_by_student(db: Session, student_id: uuid.UUID) -> Optional[Prediction]:
        """
        Retrieves the most recent prediction generated for a student.
        """
        statement = (
            select(Prediction)
            .where(Prediction.student_id == student_id)
            .order_by(Prediction.created_at.desc())
        )
        return db.scalars(statement).first()

    @staticmethod
    def list_history(
        db: Session,
        student_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[PredictionHistory]:
        """
        Retrieves historical prediction entries for a student ordered chronologically.
        """
        statement = (
            select(PredictionHistory)
            .where(PredictionHistory.student_id == student_id)
            .order_by(PredictionHistory.recorded_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(db.scalars(statement).all())

    @staticmethod
    def save_prediction(
        db: Session,
        student_id: uuid.UUID,
        model_name: str,
        model_version: str,
        predicted_gpa: float,
        performance_category: str,
        confidence_score: Optional[float],
        features_snapshot: dict,
        change_reason: str = "Automated Model Inference"
    ) -> Prediction:
        """
        Saves a prediction and generates a companion historical log entry atomically.
        """
        # 1. Fetch prior prediction for historical delta tracking
        prior = PredictionRepository.get_latest_by_student(db, student_id)
        prior_gpa = prior.predicted_gpa if prior else None

        # 2. Persist new prediction
        prediction = Prediction(
            student_id=student_id,
            model_name=model_name,
            model_version=model_version,
            predicted_gpa=predicted_gpa,
            performance_category=performance_category,
            confidence_score=confidence_score,
            input_features_snapshot=features_snapshot,
        )
        db.add(prediction)
        db.flush()

        # 3. Persist history audit record
        history = PredictionHistory(
            prediction_id=prediction.id,
            student_id=student_id,
            change_reason=change_reason,
            prior_predicted_gpa=prior_gpa,
            new_predicted_gpa=predicted_gpa,
            model_version=model_version,
        )
        db.add(history)

        db.commit()
        db.refresh(prediction)
        return prediction
