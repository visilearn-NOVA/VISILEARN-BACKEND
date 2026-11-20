"""
Automated tests for Analytics Endpoints:
- Performance overview
- GPA distribution bins
- Performance across academic levels
- Study habits vs GPA correlations
- At-risk student identification
- RBAC permissions (Faculty/Admin only)
"""

import uuid
import pytest


def test_analytics_rbac_protection(client, auth_headers):
    """
    Ensures student accounts are denied access to faculty/admin cohort analytics.
    """
    student_id = uuid.uuid4()
    headers = auth_headers(student_id, role="student")

    res = client.get("/api/v1/analytics/overview", headers=headers)
    assert res.status_code == 403


def test_analytics_overview_and_distribution(client, auth_headers):
    """
    Validates aggregate statistical calculations.
    """
    admin_id = uuid.uuid4()
    headers = auth_headers(admin_id, role="admin")

    # 1. Create 2 test students
    s1 = client.post("/api/v1/students", json={
        "matric_number": "ANA/2021/001",
        "department": "Computer Science",
        "programme": "B.Sc. Computer Science",
        "current_level": 300,
        "gender": "male"
    }, headers=headers).json()

    s2 = client.post("/api/v1/students", json={
        "matric_number": "ANA/2021/002",
        "department": "Computer Science",
        "programme": "B.Sc. Computer Science",
        "current_level": 300,
        "gender": "female"
    }, headers=headers).json()

    # 2. Add academic records
    client.post("/api/v1/academics/records", json={
        "student_id": s1["id"],
        "academic_year": "2023/2024",
        "semester": 1,
        "semester_gpa": 4.60,
        "cumulative_gpa": 4.60,
        "total_credits_registered": 18,
        "total_credits_earned": 18,
        "courses": []
    }, headers=headers)

    client.post("/api/v1/academics/records", json={
        "student_id": s2["id"],
        "academic_year": "2023/2024",
        "semester": 1,
        "semester_gpa": 2.10,
        "cumulative_gpa": 2.10,
        "total_credits_registered": 18,
        "total_credits_earned": 12,
        "courses": []
    }, headers=headers)

    # 3. Test overview
    res_overview = client.get("/api/v1/analytics/overview", headers=headers)
    assert res_overview.status_code == 200
    overview_data = res_overview.json()
    assert overview_data["total_students"] >= 2
    assert overview_data["highest_cgpa"] >= 4.60
    assert overview_data["at_risk_students_count"] >= 1
    assert overview_data["first_class_count"] >= 1

    # 4. Test GPA distribution
    res_dist = client.get("/api/v1/analytics/gpa-distribution", headers=headers)
    assert res_dist.status_code == 200
    dist_data = res_dist.json()
    assert len(dist_data["bins"]) == 5
    assert dist_data["total_analyzed"] >= 2


def test_habits_vs_performance_analytics(client, auth_headers):
    """
    Tests habit correlation aggregation.
    """
    headers = auth_headers(uuid.uuid4(), role="faculty")

    res = client.get("/api/v1/analytics/habits-vs-performance?factor=study_hours", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["factor_name"] == "study_hours"
    assert len(data["points"]) == 5
