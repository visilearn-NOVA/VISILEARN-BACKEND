"""
Survey Response model representing questionnaire features gathered from Google Forms.
Stores student study habits, attendance, socio-environmental factors, and flexible JSON extensions.
"""

from datetime import datetime
from typing import Any, Dict, Optional
import uuid
from sqlalchemy import (
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    JSON,
    func,
    ForeignKey,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class SurveyResponse(Base):
    """
    Questionnaire response entity mapped to the 'survey_responses' table.
    """
    __tablename__ = "survey_responses"

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
    survey_version: Mapped[str] = mapped_column(
        String(20),
        default="v1.0",
        nullable=False
    )
    study_hours_per_week: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Weekly independent study hours"
    )
    attendance_rate_pct: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Lecture attendance percentage (0.00 to 100.00)"
    )
    sleep_hours_per_night: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Average daily sleep hours"
    )
    travel_time_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Commute time to campus in minutes"
    )
    internet_access: Mapped[str] = mapped_column(
        String(20),
        default="good",
        nullable=False,
        comment="Internet availability: none, poor, moderate, good"
    )
    class_participation: Mapped[str] = mapped_column(
        String(20),
        default="medium",
        nullable=False,
        comment="Active participation: low, medium, high"
    )
    parental_education: Mapped[str] = mapped_column(
        String(30),
        default="secondary",
        nullable=False,
        comment="Highest parental level: primary, secondary, tertiary, postgraduate"
    )
    social_media_hours_per_day: Mapped[float] = mapped_column(
        Float,
        default=2.0,
        nullable=False,
        comment="Daily social media usage hours"
    )
    participates_extracurricular: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Active participation in clubs/sports/societies"
    )
    stress_level: Mapped[str] = mapped_column(
        String(20),
        default="moderate",
        nullable=False,
        comment="Perceived academic stress: low, moderate, high, extreme"
    )
    financial_support: Mapped[str] = mapped_column(
        String(20),
        default="adequate",
        nullable=False,
        comment="Financial adequacy: inadequate, adequate, abundant"
    )
    additional_attributes: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        default=dict,
        nullable=True,
        comment="Dynamic key-value storage for extra Google Forms survey fields"
    )
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    student = relationship("Student", back_populates="survey_responses")

    def __repr__(self) -> str:
        return f"<SurveyResponse(id={self.id}, student_id={self.student_id}, study_hours={self.study_hours_per_week}, attendance={self.attendance_rate_pct}%)>"
