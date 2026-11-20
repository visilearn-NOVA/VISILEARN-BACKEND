"""
Analytics Service delivering SQL-level aggregations and chart-ready statistical datasets.
All aggregations are anonymized and structured for modern frontend charting components.
"""

from typing import Dict, List, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session
from app.models.student import Student
from app.models.academic import AcademicRecord
from app.models.survey import SurveyResponse
from app.schemas.analytics import (
    PerformanceOverviewResponse,
    GpaDistributionResponse,
    GpaDistributionItem,
    LevelPerformanceItem,
    DepartmentPerformanceItem,
    HabitVsPerformanceResponse,
    HabitCorrelationItem,
    AtRiskStudentItem,
)


class AnalyticsService:
    """
    Business logic layer for cohort analytics and visualizations.
    """

    @staticmethod
    def get_performance_overview(
        db: Session,
        department: Optional[str] = None
    ) -> PerformanceOverviewResponse:
        """
        Calculates university/department-wide academic benchmarks.
        """
        # 1. Total students count
        student_query = select(func.count(Student.id))
        if department:
            student_query = student_query.where(func.lower(Student.department) == func.lower(department.strip()))
        total_students = db.scalar(student_query) or 0

        # 2. Total surveys submitted
        survey_query = select(func.count(SurveyResponse.id))
        if department:
            survey_query = survey_query.join(Student).where(func.lower(Student.department) == func.lower(department.strip()))
        total_surveys = db.scalar(survey_query) or 0

        # 3. CGPA Aggregates
        academic_query = select(
            func.avg(AcademicRecord.cumulative_gpa),
            func.max(AcademicRecord.cumulative_gpa),
            func.min(AcademicRecord.cumulative_gpa),
        )
        if department:
            academic_query = academic_query.join(Student).where(func.lower(Student.department) == func.lower(department.strip()))

        avg_cgpa, max_cgpa, min_cgpa = db.execute(academic_query).first() or (0.0, 0.0, 0.0)

        # 4. At-risk (< 2.40) & First class (>= 4.50) counts
        at_risk_query = select(func.count(func.distinct(AcademicRecord.student_id))).where(AcademicRecord.cumulative_gpa < 2.40)
        first_class_query = select(func.count(func.distinct(AcademicRecord.student_id))).where(AcademicRecord.cumulative_gpa >= 4.50)

        if department:
            at_risk_query = at_risk_query.join(Student).where(func.lower(Student.department) == func.lower(department.strip()))
            first_class_query = first_class_query.join(Student).where(func.lower(Student.department) == func.lower(department.strip()))

        at_risk_count = db.scalar(at_risk_query) or 0
        first_class_count = db.scalar(first_class_query) or 0

        return PerformanceOverviewResponse(
            total_students=total_students,
            average_cgpa=round(float(avg_cgpa or 0.0), 2),
            highest_cgpa=round(float(max_cgpa or 0.0), 2),
            lowest_cgpa=round(float(min_cgpa or 0.0), 2),
            at_risk_students_count=at_risk_count,
            first_class_count=first_class_count,
            survey_response_count=total_surveys,
        )

    @staticmethod
    def get_gpa_distribution(
        db: Session,
        department: Optional[str] = None,
        level: Optional[int] = None
    ) -> GpaDistributionResponse:
        """
        Categorizes student GPAs into 5 standardized frequency bins.
        """
        statement = select(AcademicRecord.cumulative_gpa).join(Student)
        if department:
            statement = statement.where(func.lower(Student.department) == func.lower(department.strip()))
        if level:
            statement = statement.where(Student.current_level == level)

        cgpa_list = [row[0] for row in db.execute(statement).all() if row[0] is not None]
        total = len(cgpa_list)

        bins_def = [
            {"range": "< 1.50", "category": "Academic Probation / At-Risk", "check": lambda x: x < 1.50},
            {"range": "1.50 - 2.39", "category": "Third Class", "check": lambda x: 1.50 <= x < 2.40},
            {"range": "2.40 - 3.49", "category": "Second Class Lower", "check": lambda x: 2.40 <= x < 3.50},
            {"range": "3.50 - 4.49", "category": "Second Class Upper", "check": lambda x: 3.50 <= x < 4.50},
            {"range": "4.50 - 5.00", "category": "First Class Honours", "check": lambda x: x >= 4.50},
        ]

        items: List[GpaDistributionItem] = []
        for b in bins_def:
            count = sum(1 for gpa in cgpa_list if b["check"](gpa))
            pct = round((count / total * 100), 1) if total > 0 else 0.0
            items.append(GpaDistributionItem(
                range_label=b["range"],
                category=b["category"],
                count=count,
                percentage=pct
            ))

        return GpaDistributionResponse(bins=items, total_analyzed=total)

    @staticmethod
    def get_performance_by_level(db: Session) -> List[LevelPerformanceItem]:
        """
        Computes comparative average CGPA across academic levels (100L - 500L).
        """
        statement = (
            select(
                Student.current_level,
                func.avg(AcademicRecord.cumulative_gpa),
                func.count(func.distinct(Student.id))
            )
            .join(AcademicRecord, AcademicRecord.student_id == Student.id)
            .group_by(Student.current_level)
            .order_by(Student.current_level.asc())
        )

        results = db.execute(statement).all()
        return [
            LevelPerformanceItem(
                level=row[0],
                level_label=f"{row[0]} Level",
                average_cgpa=round(float(row[1] or 0.0), 2),
                student_count=row[2]
            )
            for row in results
        ]

    @staticmethod
    def get_performance_by_department(db: Session) -> List[DepartmentPerformanceItem]:
        """
        Computes comparative average CGPA across academic departments.
        """
        statement = (
            select(
                Student.department,
                func.avg(AcademicRecord.cumulative_gpa),
                func.count(func.distinct(Student.id))
            )
            .join(AcademicRecord, AcademicRecord.student_id == Student.id)
            .group_by(Student.department)
            .order_by(Student.department.asc())
        )

        results = db.execute(statement).all()
        return [
            DepartmentPerformanceItem(
                department=row[0],
                average_cgpa=round(float(row[1] or 0.0), 2),
                student_count=row[2]
            )
            for row in results
        ]

    @staticmethod
    def get_habits_vs_performance(
        db: Session,
        factor: str = "study_hours"
    ) -> HabitVsPerformanceResponse:
        """
        Aggregates survey behavioral variables against recorded student CGPA.
        Supported factors: study_hours, attendance, social_media, stress.
        """
        # Fetch joined pairs of survey and academic records
        statement = (
            select(SurveyResponse, AcademicRecord.cumulative_gpa)
            .join(AcademicRecord, AcademicRecord.student_id == SurveyResponse.student_id)
        )
        pairs = db.execute(statement).all()

        factor_clean = factor.strip().lower()
        points: List[HabitCorrelationItem] = []

        if factor_clean == "study_hours":
            brackets = [
                ("0 - 5 hrs", lambda s: s.study_hours_per_week <= 5),
                ("6 - 10 hrs", lambda s: 5 < s.study_hours_per_week <= 10),
                ("11 - 15 hrs", lambda s: 10 < s.study_hours_per_week <= 15),
                ("16 - 20 hrs", lambda s: 15 < s.study_hours_per_week <= 20),
                ("21+ hrs", lambda s: s.study_hours_per_week > 20),
            ]
            desc = "Weekly self-study hours correlated with cumulative GPA."
        elif factor_clean == "attendance":
            brackets = [
                ("< 60%", lambda s: s.attendance_rate_pct < 60),
                ("60% - 74%", lambda s: 60 <= s.attendance_rate_pct < 75),
                ("75% - 89%", lambda s: 75 <= s.attendance_rate_pct < 90),
                ("90% - 100%", lambda s: s.attendance_rate_pct >= 90),
            ]
            desc = "Lecture attendance percentage correlated with cumulative GPA."
        elif factor_clean == "social_media":
            brackets = [
                ("0 - 2 hrs/day", lambda s: s.social_media_hours_per_day <= 2),
                ("2 - 4 hrs/day", lambda s: 2 < s.social_media_hours_per_day <= 4),
                ("4 - 6 hrs/day", lambda s: 4 < s.social_media_hours_per_day <= 6),
                ("6+ hrs/day", lambda s: s.social_media_hours_per_day > 6),
            ]
            desc = "Daily recreational social media screen time correlated with cumulative GPA."
        else:  # stress
            factor_clean = "stress"
            brackets = [
                ("Low Stress", lambda s: s.stress_level == "low"),
                ("Moderate Stress", lambda s: s.stress_level == "moderate"),
                ("High Stress", lambda s: s.stress_level == "high"),
                ("Extreme Stress", lambda s: s.stress_level == "extreme"),
            ]
            desc = "Perceived academic stress levels correlated with cumulative GPA."

        for label, predicate in brackets:
            matched_gpas = [gpa for s, gpa in pairs if predicate(s) and gpa is not None]
            avg_val = round(sum(matched_gpas) / len(matched_gpas), 2) if matched_gpas else 0.0
            points.append(HabitCorrelationItem(
                bracket=label,
                average_cgpa=avg_val,
                sample_size=len(matched_gpas)
            ))

        return HabitVsPerformanceResponse(
            factor_name=factor_clean,
            description=desc,
            points=points
        )

    @staticmethod
    def get_at_risk_students(
        db: Session,
        threshold: float = 2.40
    ) -> List[AtRiskStudentItem]:
        """
        Identifies students currently on or approaching academic probation.
        """
        statement = (
            select(Student, AcademicRecord.cumulative_gpa)
            .join(AcademicRecord, AcademicRecord.student_id == Student.id)
            .where(AcademicRecord.cumulative_gpa < threshold)
            .order_by(AcademicRecord.cumulative_gpa.asc())
        )
        rows = db.execute(statement).all()

        at_risk_list: List[AtRiskStudentItem] = []
        seen_students = set()

        for student, gpa in rows:
            if student.id in seen_students:
                continue
            seen_students.add(student.id)

            # Check latest survey metrics if available
            survey = student.survey_responses[0] if student.survey_responses else None

            at_risk_list.append(AtRiskStudentItem(
                matric_number=student.matric_number,
                department=student.department,
                current_level=student.current_level,
                latest_gpa=round(float(gpa), 2),
                risk_level="High Risk (Probation)" if gpa < 1.50 else "Moderate Risk",
                attendance_rate_pct=survey.attendance_rate_pct if survey else None,
                study_hours_per_week=survey.study_hours_per_week if survey else None,
            ))

        return at_risk_list
