import pytest

from app.models.User import User
from app.repositories.user_repository import UserRepository
from app.User_schem import UserCreate, UserUpdate


class TestUserRepository:
    @pytest.mark.asyncio
    async def test_get_user_by_email(self, session, user_repository: UserRepository):
        """Тест получения пользователя по email"""
        # Подготовим данные для создания
        user_data = {
            "email": "unique@example.com",
            "username": "user_test",
            "firstname": "Test",
            "lastname": "User",
        }

        user_create_schema = UserCreate(**user_data)

        user = await user_repository.create(session, user_create_schema)

        found_user = await user_repository.get_by_id(session, user.id)

        assert found_user is not None
        assert found_user.id == user.id
        assert found_user.email == "unique@example.com"
        # --- Проверим новые поля ---
        assert found_user.firstname == "Test"
        assert found_user.lastname == "User"
        # ---

    @pytest.mark.asyncio
    async def test_update_user(self, session, user_repository: UserRepository):
        """Тест обновления пользователя"""
        # Подготовим данные для создания
        user_data = {
            "email": "update@example.com",
            "username": "test",
            "firstname": "Original",
            "lastname": "Name",
        }

        user_create_schema = UserCreate(**user_data)
        user = await user_repository.create(session, user_create_schema)

        user_update_data = {"firstname": "Updated"}
        user_update_schema = UserUpdate(**user_update_data)

        updated_user = await user_repository.update(
            session, user.id, user_update_schema
        )

        assert updated_user.username == "test"
        assert updated_user.firstname == "Updated"
        assert updated_user.lastname == "Name"
