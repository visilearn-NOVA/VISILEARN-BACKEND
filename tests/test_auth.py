"""
Automated tests for Authentication and Security:
- Password hashing & verification
- JWT token generation and lifecycle
- Registration and duplicate prevention
- Login, token refresh, and protected endpoints
"""

import uuid
import pytest
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.user import User, UserRole


def test_password_hashing():
    """
    Ensures passwords are cryptographically hashed and never stored or matched in plaintext.
    """
    raw_password = "SecurePassword123!"
    hashed = hash_password(raw_password)

    assert hashed != raw_password
    assert verify_password(raw_password, hashed) is True
    assert verify_password("WrongPassword999!", hashed) is False


def test_jwt_token_lifecycle():
    """
    Validates token encoding, payload decoding, and role embedding.
    """
    user_id = uuid.uuid4()
    access_token = create_access_token(subject=user_id, role="student")
    payload = decode_token(access_token)

    assert payload["sub"] == str(user_id)
    assert payload["role"] == "student"
    assert payload["type"] == "access"
    assert "exp" in payload


def test_user_registration_success(client):
    """
    Tests successful registration of a student user.
    """
    payload = {
        "email": "student1@university.edu",
        "full_name": "Ada Lovelace",
        "password": "StrongPassword123!",
        "role": "student"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "student1@university.edu"
    assert data["full_name"] == "Ada Lovelace"
    assert data["role"] == "student"
    assert data["is_active"] is True
    assert "password" not in data
    assert "password_hash" not in data


def test_user_registration_duplicate_email(client):
    """
    Tests that registering with an already existing email is rejected.
    """
    payload = {
        "email": "duplicate@university.edu",
        "full_name": "Original User",
        "password": "Password123!",
        "role": "student"
    }
    res1 = client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


def test_user_registration_weak_password(client):
    """
    Tests that passwords failing strength validation are rejected by Pydantic.
    """
    payload = {
        "email": "weak@university.edu",
        "full_name": "Weak User",
        "password": "short",
        "role": "student"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


def test_user_login_success(client):
    """
    Tests user login yielding valid access and refresh tokens.
    """
    reg_payload = {
        "email": "loginuser@university.edu",
        "full_name": "John von Neumann",
        "password": "CorrectPassword123!",
        "role": "student"
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    login_payload = {
        "email": "loginuser@university.edu",
        "password": "CorrectPassword123!"
    }
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "loginuser@university.edu"


def test_user_login_invalid_password(client):
    """
    Tests login failure with wrong password.
    """
    reg_payload = {
        "email": "security@university.edu",
        "full_name": "Security Tester",
        "password": "ValidPassword123!",
        "role": "student"
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    response = client.post("/api/v1/auth/login", json={
        "email": "security@university.edu",
        "password": "TotallyWrongPassword!"
    })
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_get_current_user_profile(client):
    """
    Tests accessing protected /auth/me route with Bearer token.
    """
    reg_payload = {
        "email": "profile@university.edu",
        "full_name": "Alan Turing",
        "password": "TuringMachine123!",
        "role": "faculty"
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    login_res = client.post("/api/v1/auth/login", json={
        "email": "profile@university.edu",
        "password": "TuringMachine123!"
    })
    token = login_res.json()["access_token"]

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "profile@university.edu"
    assert data["full_name"] == "Alan Turing"
    assert data["role"] == "faculty"


def test_unauthenticated_request_rejected(client):
    """
    Tests that requests without Bearer token are rejected with 401 Unauthorized.
    """
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
