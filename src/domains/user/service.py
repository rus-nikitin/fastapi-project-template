from typing import List, Optional

from src.domains.user.models import User
from src.domains.user.repository import UserRepository
from src.domains.user.schemas import UserCreate, UserUpdate


class UserService:
    """User business logic service"""

    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self.repository.get_by_id(user_id)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        pass

    async def create_user(self, user_data: UserCreate) -> User:
        """Create new user with business validation"""
        pass

    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Update existing user"""
        pass

    async def delete_user(self, user_id: int) -> bool:
        """Delete user by ID"""
        pass

    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get paginated list of users"""
        pass

    async def get_users_count(self) -> int:
        """Get total number of users"""
        pass

    def _validate_user_data(self, user_data: UserCreate) -> None:
        """Validate business rules for user creation"""
        pass
