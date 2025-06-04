from fastapi import Depends, HTTPException, status
from typing import Annotated

from core.dependencies import DbProvider
from .repository import UserRepositorySQLAlchemy
from .service import UserService
from .models import User


def get_user_repository(db_provider: DbProvider) -> UserRepositorySQLAlchemy:
    """Get user repository implementation"""
    if db_provider is None:
        raise HTTPException(500, "Database not configured")
    return UserRepositorySQLAlchemy(db_provider)


def get_user_service(
    repository: UserRepositorySQLAlchemy = Depends(get_user_repository)
) -> UserService:
    """Get user service with injected repository"""
    return UserService(repository)


async def get_user_by_id(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
) -> User:
    """Dependency to get user by ID with validation"""
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A user with this id does not exist."}],
        )
    return user


async def get_current_user(
    # TODO: Add JWT token validation
    # token: str = Depends(oauth2_scheme)
) -> User:
    """Get current authenticated user"""
    # Placeholder - will implement with JWT
    raise HTTPException(401, "Authentication not implemented yet")


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(403, "Inactive user")
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current admin user"""
    if not current_user.is_admin:
        raise HTTPException(403, "Admin access required")
    return current_user


# Dependency aliases
UserByIdDep = Annotated[User, Depends(get_user_by_id)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
CurrentActiveUserDep = Annotated[User, Depends(get_current_active_user)]
CurrentAdminUserDep = Annotated[User, Depends(get_current_admin_user)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
