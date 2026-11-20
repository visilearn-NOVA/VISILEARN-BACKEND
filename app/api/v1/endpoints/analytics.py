"""
Analytics REST Endpoints.
Serves statistical distributions, cohort breakdowns, and behavioral correlations for frontend visualization dashboards.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, require_roles
from app.models.user import User, UserRole
from app.schemas.analytics import (
    PerformanceOverviewResponse,
    GpaDistributionResponse,
    LevelPerformanceItem,
    DepartmentPerformanceItem,
    HabitVsPerformanceResponse,
    AtRiskStudentItem,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics & Visualizations"])


@router.get(
    "/overview",
    response_model=PerformanceOverviewResponse,
    summary="Get overall student performance metrics"
)
def get_performance_overview(
    department: Optional[str] = Query(None, description="Filter by department"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.FACULTY))
):
    """
    Returns executive metrics: total students, average CGPA, high/low GPA, at-risk count.
    """
    return AnalyticsService.get_performance_overview(db, department=department)


@router.get(
    "/gpa-distribution",
    response_model=GpaDistributionResponse,
    summary="Get GPA frequency distribution for histogram charts"
)
def get_gpa_distribution(
    department: Optional[str] = Query(None, description="Filter by department"),
    level: Optional[int] = Query(None, ge=100, le=500, description="Filter by academic level"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.FACULTY))
):
    """
    Returns frequency distribution across 5 standard GPA class divisions.
    """
    return AnalyticsService.get_gpa_distribution(db, department=department, level=level)


@router.get(
    "/performance-by-level",
    response_model=List[LevelPerformanceItem],
    summary="Get average CGPA across academic levels (100L - 500L)"
)
def get_performance_by_level(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.FACULTY))
):
    """
    Returns average GPA and student enrollment counts broken down by academic level.
    """
    return AnalyticsService.get_performance_by_level(db)


@router.get(
    "/performance-by-department",
    response_model=List[DepartmentPerformanceItem],
    summary="Get average CGPA across departments"
)
def get_performance_by_department(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.FACULTY))
):
    """
    Returns comparative departmental CGPA averages.
    """
    return AnalyticsService.get_performance_by_department(db)


@router.get(
    "/habits-vs-performance",
    response_model=HabitVsPerformanceResponse,
    summary="Get behavioral habit correlation data for scatter plots / trendlines"
)
def get_habits_vs_performance(
    factor: str = Query(
        "study_hours",
        description="Behavioral factor: 'study_hours', 'attendance', 'social_media', 'stress'"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.FACULTY))
):
    """
    Aggregates survey responses against cumulative GPAs by discrete habit brackets.
    """
    return AnalyticsService.get_habits_vs_performance(db, factor=factor)


@router.get(
    "/at-risk-students",
    response_model=List[AtRiskStudentItem],
    summary="Identify students below academic threshold"
)
def get_at_risk_students(
    threshold: float = Query(2.40, ge=1.0, le=5.0, description="CGPA threshold"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.FACULTY))
):
    """
    Returns roster of students flagged for academic intervention based on CGPA threshold.
    """
    return AnalyticsService.get_at_risk_students(db, threshold=threshold)
