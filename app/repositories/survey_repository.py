"""
Survey Repository managing persistence for student Google Forms questionnaire data.
"""

from typing import List, Optional
import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.survey import SurveyResponse
from app.schemas.survey import SurveyResponseCreate


class SurveyRepository:
    """
    Data access layer for Survey Responses.
    """

    @staticmethod
    def get_by_id(db: Session, survey_id: uuid.UUID) -> Optional[SurveyResponse]:
        """
        Retrieves a survey response by ID.
        """
        statement = select(SurveyResponse).where(SurveyResponse.id == survey_id)
        return db.scalars(statement).first()

    @staticmethod
    def get_latest_by_student(db: Session, student_id: uuid.UUID) -> Optional[SurveyResponse]:
        """
        Returns the most recently submitted survey response for a student.
        """
        statement = (
            select(SurveyResponse)
            .where(SurveyResponse.student_id == student_id)
            .order_by(SurveyResponse.submitted_at.desc())
        )
        return db.scalars(statement).first()

    @staticmethod
    def list_by_student(db: Session, student_id: uuid.UUID) -> List[SurveyResponse]:
        """
        Retrieves all survey responses recorded for a student.
        """
        statement = (
            select(SurveyResponse)
            .where(SurveyResponse.student_id == student_id)
            .order_by(SurveyResponse.submitted_at.desc())
        )
        return list(db.scalars(statement).all())

    @staticmethod
    def create(db: Session, survey_in: SurveyResponseCreate) -> SurveyResponse:
        """
        Persists a student questionnaire response.
        """
        db_survey = SurveyResponse(
            student_id=survey_in.student_id,
            survey_version=survey_in.survey_version or "v1.0",
            study_hours_per_week=survey_in.study_hours_per_week,
            attendance_rate_pct=survey_in.attendance_rate_pct,
            sleep_hours_per_night=survey_in.sleep_hours_per_night,
            travel_time_minutes=survey_in.travel_time_minutes,
            internet_access=survey_in.internet_access.lower(),
            class_participation=survey_in.class_participation.lower(),
            parental_education=survey_in.parental_education.lower(),
            social_media_hours_per_day=survey_in.social_media_hours_per_day,
            participates_extracurricular=survey_in.participates_extracurricular,
            stress_level=survey_in.stress_level.lower(),
            financial_support=survey_in.financial_support.lower(),
            additional_attributes=survey_in.additional_attributes or {},
        )
        db.add(db_survey)
        db.commit()
        db.refresh(db_survey)
        return db_survey

    @staticmethod
    def list_all_responses(db: Session, limit: int = 500) -> List[SurveyResponse]:
        """
        Fetches survey responses for aggregate analytics.
        """
        statement = select(SurveyResponse).limit(limit)
        return list(db.scalars(statement).all())
