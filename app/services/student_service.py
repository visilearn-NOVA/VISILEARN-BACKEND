"""
Student Service containing business workflows for student profiles and validation.
"""

from typing import Dict, List, Optional
import uuid
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.student import Student
from app.repositories.student_repository import StudentRepository
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse


class StudentService:
    """
    Business logic layer for student profile management.
    """

    @staticmethod
    def create_student(db: Session, student_in: StudentCreate) -> Student:
        """
        Creates a new student profile after verifying matriculation number uniqueness.
        """
        existing = StudentRepository.get_by_matric(db, student_in.matric_number)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A student with matriculation number '{student_in.matric_number}' is already registered."
            )

        if student_in.user_id:
            existing_user_link = StudentRepository.get_by_user_id(db, student_in.user_id)
            if existing_user_link:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="This user account is already linked to another student profile."
                )

        return StudentRepository.create(db, student_in)

    @staticmethod
    def get_student(db: Session, student_id: uuid.UUID) -> Student:
        """
        Retrieves a student by ID or raises 404 Not Found.
        """
        student = StudentRepository.get_by_id(db, student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found."
            )
        return student

    @staticmethod
    def get_student_by_matric(db: Session, matric_number: str) -> Student:
        """
        Retrieves a student by matric number or raises 404 Not Found.
        """
        student = StudentRepository.get_by_matric(db, matric_number)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No student found with matriculation number '{matric_number}'."
            )
        return student

    @staticmethod
    def update_student(db: Session, student_id: uuid.UUID, student_in: StudentUpdate) -> Student:
        """
        Updates student profile details.
        """
        student = StudentService.get_student(db, student_id)
        return StudentRepository.update(db, student, student_in)

    @staticmethod
    def list_students(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        department: Optional[str] = None,
        level: Optional[int] = None
    ) -> Dict:
        """
        Returns a paginated listing of students matching filter parameters.
        """
        skip = (page - 1) * page_size
        students = StudentRepository.list_students(
            db, skip=skip, limit=page_size, department=department, level=level
        )
        total = StudentRepository.count(db, department=department, level=level)

        return {
            "items": [StudentResponse.model_validate(s) for s in students],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if total > 0 else 0,
        }
