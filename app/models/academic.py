"""
Academic record and course enrollment models.
Stores historical semester performance, grades, and cumulative GPA.
"""

from datetime import datetime
from typing import List
import uuid
from sqlalchemy import (
    String,
    Integer,
    Float,
    DateTime,
    func,
    ForeignKey,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class AcademicRecord(Base):
    """
    Semester-level academic performance record for a student.
    """
    __tablename__ = "academic_records"
    __table_args__ = (
        UniqueConstraint("student_id", "academic_year", "semester", name="uq_student_academic_semester"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    academic_year: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="e.g. '2023/2024'"
    )
    semester: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Semester 1 or 2"
    )
    semester_gpa: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="GPA earned in this specific semester (0.00 - 5.00)"
    )
    cumulative_gpa: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Cumulative GPA up to and including this semester (0.00 - 5.00)"
    )
    total_credits_registered: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    total_credits_earned: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    student = relationship("Student", back_populates="academic_records")
    courses = relationship(
        "CourseEnrollment",
        back_populates="academic_record",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<AcademicRecord(id={self.id}, student_id={self.student_id}, year='{self.academic_year}', sem={self.semester}, CGPA={self.cumulative_gpa})>"


class CourseEnrollment(Base):
    """
    Granular course-level grade and credit units within a semester record.
    """
    __tablename__ = "course_enrollments"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    academic_record_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("academic_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    course_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Course code e.g. CSC301"
    )
    course_title: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )
    credit_units: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Number of credit hours/units"
    )
    grade_point: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Numeric grade point (e.g. 5.0 for A, 4.0 for B, etc.)"
    )
    letter_grade: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        comment="Letter grade (A, B, C, D, E, F)"
    )

    # Relationships
    academic_record = relationship("AcademicRecord", back_populates="courses")

    def __repr__(self) -> str:
        return f"<CourseEnrollment(code='{self.course_code}', grade='{self.letter_grade}', units={self.credit_units})>"
