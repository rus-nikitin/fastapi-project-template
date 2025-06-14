from fastapi import APIRouter, HTTPException, status
from typing import List

from src.core.dependencies import RequestId
from src.domains.user.schemas import UserResponse, UserCreate, UserUpdate
from src.domains.user.dependencies import (
    UserServiceDep,
    CurrentUserDep,
    CurrentAdminUserDep
)

router = APIRouter(
    # prefix="/users",
    # tags=["users"],
    # responses={
    #     404: {"description": "User not found"},
    #     400: {"description": "Bad request"},
    #     409: {"description": "User already exists"}
    # }
)


@router.get("/", response_model=List[UserResponse])
async def get_users(
    # pagination: Pagination,
    user_service: UserServiceDep,
    current_user: CurrentAdminUserDep,  # Only admins can list all users
    request_id: RequestId
):
    """Get all users with pagination (admin only)"""
    pass


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: CurrentUserDep,
    request_id: RequestId
):
    """Get current user profile"""
    pass


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    user_service: UserServiceDep,
    request_id: RequestId
):
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A user with this id does not exist."}],
        )
    return user


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreate,
    user_service: UserServiceDep,
    request_id: RequestId
):
    """Create new user (public endpoint)"""
    pass


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: CurrentUserDep,
    user_service: UserServiceDep,
    request_id: RequestId
):
    """Update current user profile"""
    pass


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    user_service: UserServiceDep,
    current_admin: CurrentAdminUserDep,  # Only admins can update other users
    request_id: RequestId
):
    """Update user (admin only)"""
    pass


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    user_service: UserServiceDep,
    current_admin: CurrentAdminUserDep,  # Only admins can delete users
    request_id: RequestId
):
    """Delete user (admin only)"""
    pass
