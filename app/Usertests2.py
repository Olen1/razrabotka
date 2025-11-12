import pytest
from app.models.User import User
from app.repositories.user_repository import UserRepository
from app.User_schem import UserCreate, UserUpdate


class TestUserRepository:
    @pytest.mark.asyncio
    async def test_create_user(self, session, user_repository: UserRepository):
        """Тест создания пользователя в репозитории"""
        user_data = {
            "email": "Leon@example.com",
            "username": "Leon_duren",
            "firstname": "Leon",
            "lastname": "Duren",
        }


        user_create_schema = UserCreate(**user_data)


        user = await user_repository.create(session, user_create_schema)

        assert user.id is not None
        assert user.email == "Leon@example.com"
        assert user.username == "Leon_duren"
        assert user.firstname == "Leon"
        assert user.lastname == "Duren"

        # Проверим, что пользователь действительно в БД
        fetched_user = await session.get(User, user.id)
        assert fetched_user is not None
        assert fetched_user.id == user.id

    @pytest.mark.asyncio
    async def test_delete_user(self, session, user_repository: UserRepository):
        """Тест удаления пользователя"""
        # Сначала создаём пользователя
        user_data = {
            "email": "delete@example.com",
            "username": "delete_user",
            "firstname": "Delete",
            "lastname": "Me",
        }
        user_create_schema = UserCreate(**user_data)
        user = await user_repository.create(session, user_create_schema)

        # Проверим, что он существует
        fetched_user = await session.get(User, user.id)
        assert fetched_user is not None

        # Удаляем
        await user_repository.delete(session, user.id)

        # Проверим, что его больше нет
        deleted_user = await session.get(User, user.id)
        assert deleted_user is None

    @pytest.mark.asyncio
    async def test_get_all_users(self, session, user_repository: UserRepository):
        """Тест получения списка пользователей"""
        # Сначала создаём несколько пользователей
        users_data = [
            {
                "email": "list1@example.com",
                "username": "list_user1",
                "firstname": "List",
                "lastname": "One",
            },
            {
                "email": "list2@example.com",
                "username": "list_user2",
                "firstname": "List",
                "lastname": "Two",
            },
        ]

        created_users = []
        for data in users_data:
            user_create_schema = UserCreate(**data)
            user = await user_repository.create(session, user_create_schema)
            created_users.append(user)

        # Получаем список
        users_list = await user_repository.get_by_filter(session, count=10, page=1)

        # Проверяем, что все созданные пользователи есть в списке
        assert len(users_list) >= 2
        user_ids = {u.id for u in users_list}
        for user in created_users:
            assert user.id in user_ids
