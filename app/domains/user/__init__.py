"""
Users domain module

This module contains all user-related business logic, including:
- User domain model
- User repository interface and implementation
- User service (business logic)
- User API routes and schemas
- User-specific dependencies and exceptions
"""

from .models import User
from .repository import UserRepository, UserRepositorySQLAlchemy
from .service import UserService
from .schemas import UserCreate, UserUpdate, UserResponse
from .routes import router as user_router
from .dependencies import (
    CurrentUserDep
)
from .exceptions import (
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
