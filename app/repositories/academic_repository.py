"""
Academic Repository managing database persistence for semester records and course enrollments.
"""

from typing import List, Optional
import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from app.models.academic import AcademicRecord, CourseEnrollment
from app.schemas.academic import AcademicRecordCreate


class AcademicRepository:
    """
    Data access layer for Academic Records and Course Enrollments.
    """

    @staticmethod
    def get_by_id(db: Session, record_id: uuid.UUID) -> Optional[AcademicRecord]:
        """
        Retrieves an academic record with eager loading of its courses.
        """
        statement = (
            select(AcademicRecord)
            .options(selectinload(AcademicRecord.courses))
            .where(AcademicRecord.id == record_id)
        )
        return db.scalars(statement).first()

    @staticmethod
    def get_by_student_and_term(
        db: Session,
        student_id: uuid.UUID,
        academic_year: str,
        semester: int
    ) -> Optional[AcademicRecord]:
        """
        Checks if an academic record already exists for a student in a specific year and semester.
        """
        statement = select(AcademicRecord).where(
            AcademicRecord.student_id == student_id,
            AcademicRecord.academic_year == academic_year.strip(),
            AcademicRecord.semester == semester
        )
        return db.scalars(statement).first()

    @staticmethod
    def list_by_student(db: Session, student_id: uuid.UUID) -> List[AcademicRecord]:
        """
        Returns all academic records for a given student ordered chronologically.
        """
        statement = (
            select(AcademicRecord)
            .options(selectinload(AcademicRecord.courses))
            .where(AcademicRecord.student_id == student_id)
            .order_by(AcademicRecord.academic_year.asc(), AcademicRecord.semester.asc())
        )
        return list(db.scalars(statement).all())

    @staticmethod
    def get_latest_record(db: Session, student_id: uuid.UUID) -> Optional[AcademicRecord]:
        """
        Retrieves the most recent semester academic record for a student.
        """
        statement = (
            select(AcademicRecord)
            .options(selectinload(AcademicRecord.courses))
            .where(AcademicRecord.student_id == student_id)
            .order_by(AcademicRecord.academic_year.desc(), AcademicRecord.semester.desc())
        )
        return db.scalars(statement).first()

    @staticmethod
    def create(db: Session, record_in: AcademicRecordCreate) -> AcademicRecord:
        """
        Creates an academic record and associated course enrollments atomically.
        """
        db_record = AcademicRecord(
            student_id=record_in.student_id,
            academic_year=record_in.academic_year.strip(),
            semester=record_in.semester,
            semester_gpa=record_in.semester_gpa,
            cumulative_gpa=record_in.cumulative_gpa,
            total_credits_registered=record_in.total_credits_registered,
            total_credits_earned=record_in.total_credits_earned,
        )
        db.add(db_record)
        db.flush()  # Populates db_record.id

        if record_in.courses:
            for course_in in record_in.courses:
                db_course = CourseEnrollment(
                    academic_record_id=db_record.id,
                    course_code=course_in.course_code.strip().upper(),
                    course_title=course_in.course_title.strip(),
                    credit_units=course_in.credit_units,
                    grade_point=course_in.grade_point,
                    letter_grade=course_in.letter_grade.strip().upper(),
                )
                db.add(db_course)

        db.commit()
        db.refresh(db_record)
        return db_record

    @staticmethod
    def delete(db: Session, db_record: AcademicRecord) -> None:
        """
        Deletes an academic record. Attached course enrollments cascade delete.
        """
        db.delete(db_record)
        db.commit()
