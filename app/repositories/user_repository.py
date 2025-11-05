from typing import Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select, func
from sqlalchemy.sql import expression
from app.models.User import User
from app.User_schem import UserCreate, UserUpdate


class UserRepository:
    async def get_by_id(self, session: AsyncSession, user_id: str) -> Optional[User]:
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_filter(
            self,
            session: AsyncSession,
            count: int,
            page: int,
            **kwargs: Any
    ) -> List[User]:
        query = select(User).order_by(User.created_at)  # ✅ Стабильный порядок для пагинации

        filters = []
        for key, value in kwargs.items():
            if not hasattr(User, key):
                continue
            column = getattr(User, key)
            if isinstance(value, str) and "%" in value:
                filters.append(column.like(value))
            else:
                filters.append(column == value)

        if filters:
            query = query.where(and_(*filters))

        offset = (page - 1) * count
        query = query.offset(offset).limit(count)

        result = await session.execute(query)
        return list(result.scalars().all())

    async def create(self, session: AsyncSession, user_data: UserCreate) -> User:
        user_dict = user_data.model_dump()
        db_user = User(**user_dict)
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        return db_user

    async def update(
            self,
            session: AsyncSession,
            user_id: str,
            user_data: UserUpdate
    ) -> User:
        db_user = await self.get_by_id(session, user_id)
        if db_user is None:
            raise ValueError(f"User with id {user_id} not found")

        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_user, field):
                setattr(db_user, field, value)

        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        return db_user

    async def delete(self, session: AsyncSession, user_id: str) -> None:
        db_user = await self.get_by_id(session, user_id)
        if db_user is not None:
            await session.delete(db_user)
            await session.commit()

    async def get_total_count(self, session: AsyncSession) -> int:
        result = await session.execute(select(func.count(User.id)))
        return result.scalar_one()