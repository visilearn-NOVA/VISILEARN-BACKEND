"""
Pydantic schemas for Academic Records and Course Enrollments.
"""

from datetime import datetime
from typing import List, Optional
import uuid
from pydantic import BaseModel, Field, ConfigDict


class CourseEnrollmentBase(BaseModel):
    """
    Base course enrollment information.
    """
    course_code: str = Field(..., min_length=2, max_length=20, description="Course code e.g. CSC301")
    course_title: str = Field(..., min_length=2, max_length=150, description="Course title")
    credit_units: int = Field(..., ge=1, le=12, description="Course credit unit value")
    grade_point: float = Field(..., ge=0.0, le=5.0, description="Numerical grade point (0.00 to 5.00)")
    letter_grade: str = Field(..., min_length=1, max_length=2, description="Letter grade (A, B, C, D, E, F)")


class CourseEnrollmentCreate(CourseEnrollmentBase):
    """
    Schema for enrolling and recording a course result.
    """
    pass


class CourseEnrollmentResponse(CourseEnrollmentBase):
    """
    Course enrollment output schema.
    """
    id: uuid.UUID
    academic_record_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class AcademicRecordBase(BaseModel):
    """
    Base semester academic performance metrics.
    """
    academic_year: str = Field(..., pattern=r"^\d{4}/\d{4}$", description="Academic session e.g. '2023/2024'")
    semester: int = Field(..., ge=1, le=2, description="Semester term (1 or 2)")
    semester_gpa: float = Field(..., ge=0.0, le=5.0, description="Semester GPA (0.00 to 5.00)")
    cumulative_gpa: float = Field(..., ge=0.0, le=5.0, description="Cumulative GPA / CGPA (0.00 to 5.00)")
    total_credits_registered: int = Field(..., ge=1, le=40, description="Total credits registered in session")
    total_credits_earned: int = Field(..., ge=0, le=40, description="Total credits passed/earned")


class AcademicRecordCreate(AcademicRecordBase):
    """
    Schema for creating a semester academic record.
    """
    student_id: uuid.UUID
    courses: Optional[List[CourseEnrollmentCreate]] = Field(default_factory=list)


class AcademicRecordResponse(AcademicRecordBase):
    """
    Complete academic record output schema including courses.
    """
    id: uuid.UUID
    student_id: uuid.UUID
    created_at: datetime
    courses: List[CourseEnrollmentResponse] = []

    model_config = ConfigDict(from_attributes=True)
