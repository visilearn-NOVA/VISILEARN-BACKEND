"""
Academic Service handling validation and management of semester grades and course enrollments.
"""

from typing import List
import uuid
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.academic import AcademicRecord
from app.repositories.academic_repository import AcademicRepository
from app.repositories.student_repository import StudentRepository
from app.schemas.academic import AcademicRecordCreate


class AcademicService:
    """
    Business logic layer for academic records.
    """

    @staticmethod
    def create_academic_record(db: Session, record_in: AcademicRecordCreate) -> AcademicRecord:
        """
        Creates a semester academic record for a student.
        Validates student existence and duplicate semester prevention.
        """
        student = StudentRepository.get_by_id(db, record_in.student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cannot create academic record: Target student not found."
            )

        existing = AcademicRepository.get_by_student_and_term(
            db,
            student_id=record_in.student_id,
            academic_year=record_in.academic_year,
            semester=record_in.semester
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"An academic record already exists for {record_in.academic_year} Semester {record_in.semester}."
            )

        return AcademicRepository.create(db, record_in)

    @staticmethod
    def get_student_academic_records(db: Session, student_id: uuid.UUID) -> List[AcademicRecord]:
        """
        Retrieves all historical academic records for a student.
        """
        student = StudentRepository.get_by_id(db, student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found."
            )
        return AcademicRepository.list_by_student(db, student_id)

    @staticmethod
    def delete_academic_record(db: Session, record_id: uuid.UUID) -> None:
        """
        Deletes a specific semester record by ID.
        """
        record = AcademicRepository.get_by_id(db, record_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Academic record not found."
            )
        AcademicRepository.delete(db, record)
