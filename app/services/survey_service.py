"""
Survey Service handling questionnaire submissions and validation.
"""

from typing import List
import uuid
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.survey import SurveyResponse
from app.repositories.student_repository import StudentRepository
from app.repositories.survey_repository import SurveyRepository
from app.schemas.survey import SurveyResponseCreate


class SurveyService:
    """
    Business logic layer for student survey responses.
    """

    @staticmethod
    def submit_survey(db: Session, survey_in: SurveyResponseCreate) -> SurveyResponse:
        """
        Submits and persists a student survey response.
        """
        student = StudentRepository.get_by_id(db, survey_in.student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cannot submit survey: Target student profile not found."
            )

        return SurveyRepository.create(db, survey_in)

    @staticmethod
    def get_latest_survey(db: Session, student_id: uuid.UUID) -> SurveyResponse:
        """
        Retrieves the latest survey response for a student or raises 404.
        """
        survey = SurveyRepository.get_latest_by_student(db, student_id)
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No survey responses recorded for this student."
            )
        return survey

    @staticmethod
    def list_student_surveys(db: Session, student_id: uuid.UUID) -> List[SurveyResponse]:
        """
        Retrieves all survey responses for a student.
        """
        return SurveyRepository.list_by_student(db, student_id)
