"""
Academic Records REST Endpoints.
Handles creation and listing of semester grades, CGPA progression, and course breakdowns.
"""

from typing import List
import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.dependencies import (
    get_db,
    get_current_user,
    require_roles,
    check_student_record_access,
)
from app.models.user import User, UserRole
from app.schemas.academic import (
    AcademicRecordCreate,
    AcademicRecordResponse,
)
from app.services.academic_service import AcademicService

router = APIRouter(prefix="/academics", tags=["Academic Records"])


@router.post(
    "/records",
    response_model=AcademicRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create semester academic record (Faculty or Admin only)"
)
def create_academic_record(
    record_in: AcademicRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.FACULTY))
):
    """
    Submits a student's semester GPA, CGPA, and course grades.
    """
    return AcademicService.create_academic_record(db, record_in)


@router.get(
    "/students/{student_id}",
    response_model=List[AcademicRecordResponse],
    summary="Get full academic progression for a student"
)
def get_student_academic_records(
    student_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves all recorded semesters for a student ordered chronologically.
    Enforces student self-access permissions.
    """
    check_student_record_access(student_id, current_user)
    return AcademicService.get_student_academic_records(db, student_id)


@router.delete(
    "/records/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an academic record (Admin only)"
)
def delete_academic_record(
    record_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN))
):
    """
    Permanently deletes a semester academic record.
    """
    AcademicService.delete_academic_record(db, record_id)
