"""
User Repository providing isolated database operations for the User entity.
"""

from typing import List, Optional
import uuid
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate


class UserRepository:
    """
    Data access layer for User operations.
    """

    @staticmethod
    def get_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
        """
        Retrieves a user by their primary key UUID.
        """
        statement = select(User).where(User.id == user_id)
        return db.scalars(statement).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """
        Retrieves a user by exact email match (case-insensitive).
        """
        statement = select(User).where(func.lower(User.email) == func.lower(email))
        return db.scalars(statement).first()

    @staticmethod
    def create(db: Session, user_in: UserCreate, hashed_password: str) -> User:
        """
        Persists a new User record to PostgreSQL.
        """
        db_user = User(
            email=user_in.email.lower(),
            password_hash=hashed_password,
            full_name=user_in.full_name,
            role=user_in.role or UserRole.STUDENT,
            is_active=True,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def update(db: Session, db_user: User, user_in: UserUpdate) -> User:
        """
        Applies partial updates to an existing User record.
        """
        update_data = user_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "email" and value:
                setattr(db_user, field, value.lower())
            else:
                setattr(db_user, field, value)

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def list_users(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        role: Optional[UserRole] = None
    ) -> List[User]:
        """
        Retrieves a paginated list of users with optional role filtering.
        """
        statement = select(User)
        if role:
            statement = statement.where(User.role == role)
        statement = statement.offset(skip).limit(limit).order_by(User.created_at.desc())
        return list(db.scalars(statement).all())

    @staticmethod
    def count(db: Session, role: Optional[UserRole] = None) -> int:
        """
        Returns the total count of users matching criteria.
        """
        statement = select(func.count(User.id))
        if role:
            statement = statement.where(User.role == role)
        return db.scalar(statement) or 0

    @staticmethod
    def delete(db: Session, db_user: User) -> None:
        """
        Removes a user record. Cascading deletes will remove attached student profile.
        """
        db.delete(db_user)
        db.commit()
