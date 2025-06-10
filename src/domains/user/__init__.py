"""
Users domain module

This module contains all user-related business logic, including:
- User domain model
- User repository interface and implementation
- User service (business logic)
- User API routes and schemas
- User-specific dependencies and exceptions

routes (schemas)   → service → repository (models) → Database
      ↓               ↓          ↓
HTTP handling       Business  Data access
Validation          Logic     Storage
Serialization       Rules     Queries
"""

from src.domains.user.models import User
from src.domains.user.repository import UserRepository, UserRepositorySQLAlchemy
from src.domains.user.service import UserService
from src.domains.user.schemas import UserCreate, UserUpdate, UserResponse
from src.domains.user.routes import router as user_router
from src.domains.user.dependencies import (
    CurrentUserDep
)
from src.domains.user.exceptions import (
    UserNotFoundError,
    UserAlreadyExistsError,
    UserValidationError,
    UserPermissionError
)

__all__ = [
    # Models
    "User",

    # Repository
    "UserRepository",
    "UserRepositorySQLAlchemy",

    # Service
    "UserService",

    # Schemas
    "UserCreate",
    "UserUpdate",
    "UserResponse",

    # Router
    "user_router",

    # Dependencies
    "CurrentUserDep",

    # Exceptions
    "UserNotFoundError",
    "UserAlreadyExistsError",
    "UserValidationError",
    "UserPermissionError"
]
