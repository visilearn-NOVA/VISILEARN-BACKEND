"""
Prediction and Prediction History models.
Tracks ML model inferences, prediction confidence, feature snapshots, and longitudinal trajectory shifts.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid
from sqlalchemy import (
    String,
    Float,
    DateTime,
    JSON,
    func,
    ForeignKey,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class Prediction(Base):
    """
    Generated ML inference record for a student.
    """
    __tablename__ = "predictions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    model_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Algorithm name e.g. RandomForestRegressor, GradientBoosting"
    )
    model_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Semantic model version e.g. v1.0.0"
    )
    predicted_gpa: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Predicted numerical GPA (e.g. 3.45)"
    )
    performance_category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Classification tier e.g. 'First Class', 'Second Class Upper', 'At-Risk'"
    )
    confidence_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Confidence metric or uncertainty interval (0.0 to 1.0)"
    )
    input_features_snapshot: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        comment="Immutable snapshot of raw input features passed to the model"
    )
    feature_importances_snapshot: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="Optional feature attribution / SHAP value breakdown"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    student = relationship("Student", back_populates="predictions")
    history_entries = relationship(
        "PredictionHistory",
        back_populates="prediction",
        cascade="all, delete-orphan",
        order_by="PredictionHistory.recorded_at.desc()"
    )

    def __repr__(self) -> str:
        return f"<Prediction(id={self.id}, student_id={self.student_id}, gpa={self.predicted_gpa}, version='{self.model_version}')>"


class PredictionHistory(Base):
    """
    Historical log of prediction updates across academic semesters.
    """
    __tablename__ = "prediction_history"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    prediction_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("predictions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    change_reason: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Reason for re-prediction (e.g. 'New semester grades submitted', 'Updated study survey')"
    )
    prior_predicted_gpa: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )
    new_predicted_gpa: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )
    model_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    prediction = relationship("Prediction", back_populates="history_entries")

    def __repr__(self) -> str:
        return f"<PredictionHistory(id={self.id}, prior={self.prior_predicted_gpa}, new={self.new_predicted_gpa})>"
