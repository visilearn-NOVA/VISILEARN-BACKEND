"""
Pydantic schemas for Student Survey Responses (Google Forms Questionnaire Ingestion).
"""

from datetime import datetime
from typing import Any, Dict, Optional
import uuid
from pydantic import BaseModel, Field, ConfigDict


class SurveyResponseBase(BaseModel):
    """
    Survey behavioral, environmental, and habit features.
    """
    survey_version: Optional[str] = Field("v1.0", description="Survey instrument version identifier")
    study_hours_per_week: float = Field(..., ge=0.0, le=168.0, description="Self-study hours per week")
    attendance_rate_pct: float = Field(..., ge=0.0, le=100.0, description="Lecture attendance percentage")
    sleep_hours_per_night: float = Field(..., ge=0.0, le=24.0, description="Average sleep per night in hours")
    travel_time_minutes: int = Field(..., ge=0, le=360, description="Daily travel time to campus in minutes")
    internet_access: str = Field(..., description="Internet quality: 'none', 'poor', 'moderate', 'good'")
    class_participation: str = Field(..., description="Active class engagement: 'low', 'medium', 'high'")
    parental_education: str = Field(..., description="Parental education level: 'primary', 'secondary', 'tertiary', 'postgraduate'")
    social_media_hours_per_day: float = Field(default=2.0, ge=0.0, le=24.0, description="Hours spent daily on social media")
    participates_extracurricular: bool = Field(default=False, description="Whether student is involved in clubs or sports")
    stress_level: str = Field(..., description="Perceived academic stress: 'low', 'moderate', 'high', 'extreme'")
    financial_support: str = Field(..., description="Financial security: 'inadequate', 'adequate', 'abundant'")
    additional_attributes: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Dynamic dictionary for extra Google Forms questionnaire items"
    )


class SurveyResponseCreate(SurveyResponseBase):
    """
    Schema for submitting a completed survey.
    """
    student_id: uuid.UUID


class SurveyResponseResponse(SurveyResponseBase):
    """
    Schema for reading a recorded survey response.
    """
    id: uuid.UUID
    student_id: uuid.UUID
    submitted_at: datetime

    model_config = ConfigDict(from_attributes=True)
