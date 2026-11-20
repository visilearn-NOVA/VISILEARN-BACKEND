"""
Survey Ingestion REST Endpoints.
Handles recording and retrieval of student behavioral and environmental questionnaires.
"""

from typing import List
import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.dependencies import (
    get_db,
    get_current_user,
    check_student_record_access,
)
from app.models.user import User
from app.schemas.survey import (
    SurveyResponseCreate,
    SurveyResponseResponse,
)
from app.services.survey_service import SurveyService

router = APIRouter(prefix="/surveys", tags=["Survey Ingestion"])


@router.post(
    "/responses",
    response_model=SurveyResponseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit student questionnaire response"
)
def submit_survey(
    survey_in: SurveyResponseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Ingests study habits, attendance, and environmental factors collected from Google Forms survey.
    Students may submit for their own profile; Faculty/Admins can submit on behalf of students.
    """
    check_student_record_access(survey_in.student_id, current_user)
    return SurveyService.submit_survey(db, survey_in)


@router.get(
    "/students/{student_id}",
    response_model=SurveyResponseResponse,
    summary="Get latest survey response for a student"
)
def get_latest_survey(
    student_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves the most recent survey submission for the specified student.
    """
    check_student_record_access(student_id, current_user)
    return SurveyService.get_latest_survey(db, student_id)


@router.get(
    "/students/{student_id}/all",
    response_model=List[SurveyResponseResponse],
    summary="Get all survey responses for a student"
)
def list_student_surveys(
    student_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lists all survey submissions for the specified student.
    """
    check_student_record_access(student_id, current_user)
    return SurveyService.list_student_surveys(db, student_id)
