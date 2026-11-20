"""
Pydantic schemas for Student profile management and data validation.
"""

from datetime import date, datetime
import uuid
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class StudentBase(BaseModel):
    """
    Base student attributes.
    """
    matric_number: str = Field(..., min_length=3, max_length=50, description="Unique matriculation number")
    department: str = Field(..., min_length=2, max_length=100, description="Academic department")
    programme: str = Field(..., min_length=2, max_length=150, description="Degree programme")
    current_level: int = Field(..., ge=100, le=500, description="Academic level (100, 200, 300, 400, 500)")
    gender: Optional[str] = Field("undisclosed", description="Gender: male, female, other, undisclosed")
    enrollment_date: Optional[date] = Field(default_factory=date.today)


class StudentCreate(StudentBase):
    """
    Schema for creating a student profile.
    Can optionally bind to a user_id.
    """
    user_id: Optional[uuid.UUID] = Field(None, description="Optional associated user account ID")


class StudentUpdate(BaseModel):
    """
    Schema for updating student demographic or programme attributes.
    """
    department: Optional[str] = Field(None, min_length=2, max_length=100)
    programme: Optional[str] = Field(None, min_length=2, max_length=150)
    current_level: Optional[int] = Field(None, ge=100, le=500)
    gender: Optional[str] = None


class StudentResponse(StudentBase):
    """
    Public student profile response schema.
    """
    id: uuid.UUID
    user_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
