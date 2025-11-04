from typing import List
from litestar import Controller, get, post, delete, put
from litestar.params import Parameter
from litestar.exceptions import NotFoundException
from sqlalchemy.ext.asyncio import AsyncSession

from app.User_schem import UserCreate, UserUpdate, UserResponse
from app.services.user_service import UserService


class UserController(Controller):
    path = "/users"

    @get()
    async def get_all_users(
            self,
            user_service: UserService,
            session: AsyncSession,
            count: int = Parameter(default=10, gt=0, le=100),
            page: int = Parameter(default=1, gt=0),
    ) -> List[UserResponse]:
        users = await user_service.get_by_filter(session, count=count, page=page)
        return [UserResponse.model_validate(user) for user in users]

    @get("/{user_id:str}")
    async def get_user_by_id(
            self,
            user_service: UserService,
            session: AsyncSession,
            user_id: str,
    ) -> UserResponse:
        user = await user_service.get_by_id(session, user_id)
        if not user:
            raise NotFoundException(detail=f"User with ID {user_id} not found")
        return UserResponse.model_validate(user)

    @post()
    async def create_user(
            self,
            user_service: UserService,
            session: AsyncSession,
            data: UserCreate,  # ← ИМЯ "data" для тела запроса
    ) -> UserResponse:
        user = await user_service.create(session, data)
        return UserResponse.model_validate(user)

    @delete("/{user_id:str}")
    async def delete_user(
            self,
            user_service: UserService,
            session: AsyncSession,
            user_id: str,
    ) -> None:
        await user_service.delete(session, user_id)

    @put("/{user_id:str}")
    async def update_user(
            self,
            user_service: UserService,
            session: AsyncSession,
            user_id: str,
            data: UserUpdate,  # ← ИМЯ "data"
    ) -> UserResponse:
        user = await user_service.update(session, user_id, data)
        return UserResponse.model_validate(user)