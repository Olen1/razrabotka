from typing import Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.User_schem import UserCreate, UserUpdate
from app.models import User
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_by_id(self, session: AsyncSession, user_id: str) -> Optional[User]:
        return await self.user_repository.get_by_id(session, user_id)

    async def get_by_filter(
            self,
            session: AsyncSession,
            count: int,
            page: int,
            **kwargs: Any
    ) -> List[User]:
        return await self.user_repository.get_by_filter(session, count=count, page=page, **kwargs)

    async def create(self, session: AsyncSession, user_data: UserCreate) -> User:
        return await self.user_repository.create(session, user_data)

    async def update(
            self,
            session: AsyncSession,
            user_id: str,
            user_data: UserUpdate
    ) -> User:
        return await self.user_repository.update(session, user_id, user_data)

    async def delete(self, session: AsyncSession, user_id: str) -> None:
        await self.user_repository.delete(session, user_id)  # убрали 'return' — функция возвращает None

    async def get_total_count(self, session: AsyncSession) -> int:
        return await self.user_repository.get_total_count(session)