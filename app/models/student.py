"""
Student model representing academic and demographic profiles.
"""

from datetime import date, datetime
from typing import List, Optional
import uuid
from sqlalchemy import String, Integer, Date, DateTime, func, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class Student(Base):
    """
    Student profile entity mapped to the 'students' table.
    Can be associated with an authenticated User account or exist as an anonymized roster record.
    """
    __tablename__ = "students"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="SET NULL"),
        unique=True,
        nullable=True,
        comment="Optional foreign key link to active User account"
    )
    matric_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
        comment="Institutional matriculation or registration number"
    )
    department: Mapped[str] = mapped_column(
        String(100),
        index=True,
        nullable=False,
        comment="Academic department e.g. Computer Science"
    )
    programme: Mapped[str] = mapped_column(
        String(150),
        index=True,
        nullable=False,
        comment="Degree programme e.g. B.Sc. Software Engineering"
    )
    current_level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Academic level (100, 200, 300, 400, 500)"
    )
    gender: Mapped[str] = mapped_column(
        String(20),
        default="undisclosed",
        nullable=False
    )
    enrollment_date: Mapped[date] = mapped_column(
        Date,
        default=date.today,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="student_profile")
    academic_records = relationship(
        "AcademicRecord",
        back_populates="student",
        cascade="all, delete-orphan",
        order_by="AcademicRecord.academic_year.desc(), AcademicRecord.semester.desc()"
    )
    survey_responses = relationship(
        "SurveyResponse",
        back_populates="student",
        cascade="all, delete-orphan",
        order_by="SurveyResponse.submitted_at.desc()"
    )
    predictions = relationship(
        "Prediction",
        back_populates="student",
        cascade="all, delete-orphan",
        order_by="Prediction.created_at.desc()"
    )

    def __repr__(self) -> str:
        return f"<Student(id={self.id}, matric='{self.matric_number}', dept='{self.department}')>"
