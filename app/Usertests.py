import pytest
from app.models.User import User
from app.repositories.user_repository import UserRepository
from app.User_schem import UserCreate, UserResponse


class TestUserRepository:
    @pytest.mark.asyncio
    async def test_create_user(self, session, user_repository: UserRepository):
        """Тест создания пользователя в репозитории"""
        user_data = {
            "email": "test@example.com",
            "username": "john_doe",
            "firstname": "John",
            "lastname": "Doe",
        }


        user_create_schema = UserCreate(**user_data)


        user = await user_repository.create(session, user_create_schema)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "john_doe"
        assert user.firstname == "John"
        assert user.lastname == "Doe"



        fetched_user = await session.get(User, user.id)
        assert fetched_user is not None
        assert fetched_user.id == user.id