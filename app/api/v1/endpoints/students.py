"""
Student REST Endpoints.
Provides profile creation, filtering, retrieval, and updates.
"""

from typing import Optional
import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import (
    get_db,
    get_current_user,
    require_roles,
    check_student_record_access,
)
from app.models.user import User, UserRole
from app.schemas.student import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
)
from app.services.student_service import StudentService

router = APIRouter(prefix="/students", tags=["Students"])


@router.post(
    "",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create student profile (Faculty or Admin only)"
)
def create_student(
    student_in: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.FACULTY))
):
    """
    Registers a new student profile in the system.
    """
    return StudentService.create_student(db, student_in)


@router.get(
    "",
    summary="List students with pagination & filters (Faculty or Admin only)"
)
def list_students(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    department: Optional[str] = Query(None, description="Filter by department"),
    level: Optional[int] = Query(None, ge=100, le=500, description="Filter by academic level"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.FACULTY))
):
    """
    Fetches paginated list of students with optional department and level filtering.
    """
    return StudentService.list_students(
        db, page=page, page_size=page_size, department=department, level=level
    )


@router.get(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Get student profile by ID"
)
def get_student_by_id(
    student_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves student profile by UUID.
    Students may only view their own profile.
    """
    check_student_record_access(student_id, current_user)
    return StudentService.get_student(db, student_id)


@router.get(
    "/by-matric/{matric_number}",
    response_model=StudentResponse,
    summary="Get student profile by matriculation number"
)
def get_student_by_matric(
    matric_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves student profile by institutional matric number.
    """
    student = StudentService.get_student_by_matric(db, matric_number)
    check_student_record_access(student.id, current_user)
    return student


@router.put(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Update student profile (Faculty or Admin only)"
)
def update_student(
    student_id: uuid.UUID,
    student_in: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.FACULTY))
):
    """
    Updates student academic or demographic attributes.
    """
    return StudentService.update_student(db, student_id, student_in)
