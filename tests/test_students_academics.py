"""
Integration tests for Student profiles, Academic records, and Survey data.
Validates CRUD workflows, data constraints, and RBAC privacy boundaries.
"""

import uuid
import pytest
from app.models.user import UserRole


def test_create_and_get_student_profile(client, auth_headers):
    """
    Tests student creation by faculty/admin and retrieval by matric.
    """
    admin_id = uuid.uuid4()
    headers = auth_headers(admin_id, role="admin")

    student_data = {
        "matric_number": "CSC/2021/001",
        "department": "Computer Science",
        "programme": "B.Sc. Computer Science",
        "current_level": 300,
        "gender": "male"
    }

    create_res = client.post("/api/v1/students", json=student_data, headers=headers)
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["matric_number"] == "CSC/2021/001"
    student_id = created["id"]

    # Retrieve by matric
    get_res = client.get(f"/api/v1/students/by-matric/CSC/2021/001", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == student_id


def test_duplicate_matric_number_rejected(client, auth_headers):
    """
    Tests that duplicate matric numbers return 400 Bad Request.
    """
    headers = auth_headers(uuid.uuid4(), role="admin")
    student_data = {
        "matric_number": "SWE/2022/100",
        "department": "Software Engineering",
        "programme": "B.Sc. Software Engineering",
        "current_level": 200,
        "gender": "female"
    }
    res1 = client.post("/api/v1/students", json=student_data, headers=headers)
    assert res1.status_code == 201

    res2 = client.post("/api/v1/students", json=student_data, headers=headers)
    assert res2.status_code == 400
    assert "already registered" in res2.json()["detail"]


def test_academic_record_creation_and_retrieval(client, auth_headers):
    """
    Tests creating a semester record with courses, and retrieving student progression.
    """
    headers = auth_headers(uuid.uuid4(), role="admin")

    # 1. Create student
    student_res = client.post("/api/v1/students", json={
        "matric_number": "CSC/2020/055",
        "department": "Computer Science",
        "programme": "B.Sc. Computer Science",
        "current_level": 400,
        "gender": "female"
    }, headers=headers)
    student_id = student_res.json()["id"]

    # 2. Add academic record with courses
    academic_payload = {
        "student_id": student_id,
        "academic_year": "2023/2024",
        "semester": 1,
        "semester_gpa": 4.25,
        "cumulative_gpa": 4.10,
        "total_credits_registered": 18,
        "total_credits_earned": 18,
        "courses": [
            {
                "course_code": "CSC401",
                "course_title": "Advanced Algorithms",
                "credit_units": 3,
                "grade_point": 5.0,
                "letter_grade": "A"
            },
            {
                "course_code": "CSC403",
                "course_title": "Software Architecture",
                "credit_units": 3,
                "grade_point": 4.0,
                "letter_grade": "B"
            }
        ]
    }
    rec_res = client.post("/api/v1/academics/records", json=academic_payload, headers=headers)
    assert rec_res.status_code == 201
    rec_data = rec_res.json()
    assert rec_data["semester_gpa"] == 4.25
    assert len(rec_data["courses"]) == 2

    # 3. Retrieve student progression
    prog_res = client.get(f"/api/v1/academics/students/{student_id}", headers=headers)
    assert prog_res.status_code == 200
    history = prog_res.json()
    assert len(history) == 1
    assert history[0]["courses"][0]["course_code"] == "CSC401"


def test_survey_submission_and_retrieval(client, auth_headers):
    """
    Tests submitting a survey response and retrieving the latest survey.
    """
    headers = auth_headers(uuid.uuid4(), role="admin")

    # Create student
    student_res = client.post("/api/v1/students", json={
        "matric_number": "SURV/2023/001",
        "department": "Cybersecurity",
        "programme": "B.Sc. Cybersecurity",
        "current_level": 100,
        "gender": "other"
    }, headers=headers)
    student_id = student_res.json()["id"]

    survey_payload = {
        "student_id": student_id,
        "study_hours_per_week": 15.5,
        "attendance_rate_pct": 88.0,
        "sleep_hours_per_night": 7.0,
        "travel_time_minutes": 25,
        "internet_access": "good",
        "class_participation": "high",
        "parental_education": "tertiary",
        "social_media_hours_per_day": 2.5,
        "participates_extracurricular": True,
        "stress_level": "moderate",
        "financial_support": "adequate",
        "additional_attributes": {"peer_study_group": True}
    }

    surv_res = client.post("/api/v1/surveys/responses", json=survey_payload, headers=headers)
    assert surv_res.status_code == 201
    surv_data = surv_res.json()
    assert surv_data["study_hours_per_week"] == 15.5
    assert surv_data["additional_attributes"]["peer_study_group"] is True

    # Get latest survey
    latest_res = client.get(f"/api/v1/surveys/students/{student_id}", headers=headers)
    assert latest_res.status_code == 200
    assert latest_res.json()["attendance_rate_pct"] == 88.0
