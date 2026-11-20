"""
Authentication REST Endpoints.
Handles registration, JSON login, OAuth2 form login for Swagger docs, token refresh, and profile inspection.
"""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    RefreshTokenRequest,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account"
)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user with validated email and password.
    Password is automatically hashed with cryptographic protection before database storage.
    """
    user = AuthService.register_user(db, user_in)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User login with JSON credentials"
)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user via JSON payload (email and password).
    Returns JWT access and refresh tokens along with user profile information.
    """
    user = AuthService.authenticate_user(db, credentials)
    return AuthService.create_tokens_for_user(user)


@router.post(
    "/token",
    summary="OAuth2 compatible token login (for Swagger UI Authorize button)"
)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 standard password form endpoint allowing Swagger UI interactive authentication.
    """
    login_data = UserLogin(email=form_data.username, password=form_data.password)
    user = AuthService.authenticate_user(db, login_data)
    token_response = AuthService.create_tokens_for_user(user)
    return {
        "access_token": token_response.access_token,
        "token_type": "bearer",
        "refresh_token": token_response.refresh_token,
    }


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token"
)
def refresh_token(
    refresh_in: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Submit a valid refresh token to obtain a fresh access token without re-entering credentials.
    """
    return AuthService.refresh_access_token(db, refresh_in.refresh_token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user profile"
)
def read_current_user(
    current_user: User = Depends(get_current_user)
):
    """
    Returns the authenticated user's profile based on the supplied Bearer token.
    """
    return current_user
