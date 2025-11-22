from typing import Any, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.repositories.user_repository import UserRepository
from app.User_schem import UserCreate, UserUpdate


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get_by_id(self, session: AsyncSession, user_id: str) -> Optional[User]:
        return await self.repo.get_by_id(session, user_id)

    async def get_by_filter(
        self, session: AsyncSession, count: int, page: int, **kwargs: Any
    ) -> List[User]:
        return await self.repo.get_by_filter(session, count=count, page=page, **kwargs)

    async def create(self, session: AsyncSession, user_data: UserCreate) -> User:
        return await self.repo.create(session, user_data)

    async def update(
        self, session: AsyncSession, user_id: str, user_data: UserUpdate
    ) -> User:
        return await self.repo.update(session, user_id, user_data)

    async def delete(self, session: AsyncSession, user_id: str) -> None:
        await self.repo.delete(session, user_id)

    async def get_total_count(self, session: AsyncSession) -> int:
        return await self.repo.get_total_count(session)
