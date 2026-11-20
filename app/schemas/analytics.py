"""
Pydantic schemas for Frontend Analytics and Visualizations.
Formats aggregate data for frontend charting libraries (Chart.js, Recharts, Plotly).
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class PerformanceOverviewResponse(BaseModel):
    """
    High-level executive metrics for departmental dashboards.
    """
    total_students: int
    average_cgpa: float
    highest_cgpa: float
    lowest_cgpa: float
    at_risk_students_count: int
    first_class_count: int
    survey_response_count: int


class GpaDistributionItem(BaseModel):
    """
    Histogram bin representation for GPA distribution chart.
    """
    range_label: str = Field(..., description="e.g. '3.50 - 4.49'")
    category: str = Field(..., description="e.g. 'Second Class Upper'")
    count: int
    percentage: float


class GpaDistributionResponse(BaseModel):
    """
    Complete GPA histogram payload.
    """
    bins: List[GpaDistributionItem]
    total_analyzed: int


class LevelPerformanceItem(BaseModel):
    """
    Comparative CGPA averages by university level.
    """
    level: int = Field(..., description="Level e.g. 100, 200, 300, 400, 500")
    level_label: str = Field(..., description="e.g. '100 Level'")
    average_cgpa: float
    student_count: int


class DepartmentPerformanceItem(BaseModel):
    """
    Comparative CGPA averages across academic departments.
    """
    department: str
    average_cgpa: float
    student_count: int


class HabitCorrelationItem(BaseModel):
    """
    Data point mapping a behavioral/habit bracket to average GPA.
    """
    bracket: str = Field(..., description="e.g. '0-5 hrs', '5-10 hrs'")
    average_cgpa: float
    sample_size: int


class HabitVsPerformanceResponse(BaseModel):
    """
    Correlation payload ready for scatter plots and trendlines.
    """
    factor_name: str
    description: str
    points: List[HabitCorrelationItem]


class AtRiskStudentItem(BaseModel):
    """
    Anonymized or identifiable roster summary for academic intervention.
    """
    matric_number: str
    department: str
    current_level: int
    latest_gpa: float
    risk_level: str
    attendance_rate_pct: Optional[float] = None
    study_hours_per_week: Optional[float] = None
