"""
Student Repository handling database operations for student profiles.
"""

from typing import List, Optional
import uuid
from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate


class StudentRepository:
    """
    Data access layer for Student profiles.
    """

    @staticmethod
    def get_by_id(db: Session, student_id: uuid.UUID) -> Optional[Student]:
        """
        Retrieves a student profile by its primary key UUID.
        """
        statement = select(Student).where(Student.id == student_id)
        return db.scalars(statement).first()

    @staticmethod
    def get_by_user_id(db: Session, user_id: uuid.UUID) -> Optional[Student]:
        """
        Retrieves a student profile associated with a user ID.
        """
        statement = select(Student).where(Student.user_id == user_id)
        return db.scalars(statement).first()

    @staticmethod
    def get_by_matric(db: Session, matric_number: str) -> Optional[Student]:
        """
        Retrieves a student profile by matriculation number (case-insensitive).
        """
        statement = select(Student).where(
            func.lower(Student.matric_number) == func.lower(matric_number.strip())
        )
        return db.scalars(statement).first()

    @staticmethod
    def create(db: Session, student_in: StudentCreate) -> Student:
        """
        Creates and persists a new Student profile.
        """
        db_student = Student(
            user_id=student_in.user_id,
            matric_number=student_in.matric_number.strip().upper(),
            department=student_in.department.strip(),
            programme=student_in.programme.strip(),
            current_level=student_in.current_level,
            gender=student_in.gender.lower() if student_in.gender else "undisclosed",
            enrollment_date=student_in.enrollment_date,
        )
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
        return db_student

    @staticmethod
    def update(db: Session, db_student: Student, student_in: StudentUpdate) -> Student:
        """
        Updates student profile metadata.
        """
        update_data = student_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field in ["department", "programme"] and value:
                setattr(db_student, field, value.strip())
            elif field == "gender" and value:
                setattr(db_student, field, value.lower())
            else:
                setattr(db_student, field, value)

        db.add(db_student)
        db.commit()
        db.refresh(db_student)
        return db_student

    @staticmethod
    def list_students(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        department: Optional[str] = None,
        level: Optional[int] = None
    ) -> List[Student]:
        """
        Lists students with optional department and level filtering.
        """
        statement = select(Student)
        if department:
            statement = statement.where(func.lower(Student.department) == func.lower(department.strip()))
        if level:
            statement = statement.where(Student.current_level == level)

        statement = statement.offset(skip).limit(limit).order_by(Student.matric_number.asc())
        return list(db.scalars(statement).all())

    @staticmethod
    def count(
        db: Session,
        department: Optional[str] = None,
        level: Optional[int] = None
    ) -> int:
        """
        Counts students matching criteria.
        """
        statement = select(func.count(Student.id))
        if department:
            statement = statement.where(func.lower(Student.department) == func.lower(department.strip()))
        if level:
            statement = statement.where(Student.current_level == level)
        return db.scalar(statement) or 0
