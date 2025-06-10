from abc import abstractmethod
from typing import Protocol, Optional, List

from src.domains.user.models import User
from src.core.dependencies import DbProvider


class UserRepository(Protocol):
    """User repository interface"""

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    async def create(self, email: str, name: str, **kwargs) -> User:
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        pass

    @abstractmethod
    async def delete(self, user: User) -> bool:
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        pass

    @abstractmethod
    async def count(self) -> int:
        pass


"""sqlalchemy specified"""
class UserRepositorySQLAlchemy(UserRepository):
    """SQLAlchemy implementation of user repository"""

    def __init__(self, session: DbProvider):
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

    async def get_by_email(self, email: str) -> Optional[User]:
        pass

    async def create(self, email: str, name: str, **kwargs) -> User:
        pass

    async def update(self, user: User) -> User:
        pass

    async def delete(self, user: User) -> bool:
        pass

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        pass

    async def count(self) -> int:
        pass
