import pytest
import uuid
from litestar.testing import AsyncTestClient
from app.main import app
from app.User_schem import UserCreate, UserUpdate, UserResponse
from app.models.User import User


@pytest.mark.asyncio
async def test_create_user(session):
    """Тест создания пользователя через API"""
    user_data = {
        "username": "test_user_api",
        "email": "test_api@example.com",
        "firstname": "Test",
        "lastname": "User",
    }

    async with AsyncTestClient(app=app) as ac:
        response = await ac.post("/users/", json=user_data)

    print("Status Code:", response.status_code)
    print("Response Body:", response.text)

    assert response.status_code == 201, f"Expected 201, got {response.status_code}. Response: {response.text}"

    user_response = response.json()
    assert user_response["username"] == "test_user_api"
    assert user_response["email"] == "test_api@example.com"
    assert user_response["firstname"] == "Test"
    assert user_response["lastname"] == "User"
    assert "id" in user_response

    # Проверим, что пользователь действительно в БД
    fetched_user = await session.get(User, user_response["id"])
    assert fetched_user is not None
    assert fetched_user.id == user_response["id"]

    return user_response["id"]  # Возвращаем ID для использования в других тестах


@pytest.mark.asyncio
async def test_get_all_users(session):
    """Тест получения списка всех пользователей"""
    # Сначала создадим несколько пользователей
    users_data = [
        {
            "username": "user1",
            "email": "user1@example.com",
            "firstname": "User",
            "lastname": "One",
        },
        {
            "username": "user2",
            "email": "user2@example.com",
            "firstname": "User",
            "lastname": "Two",
        }
    ]

    async with AsyncTestClient(app=app) as ac:
        # Создаем пользователей
        for user_data in users_data:
            await ac.post("/users/", json=user_data)

        # Получаем список пользователей
        response = await ac.get("/users/", params={"count": 10, "page": 1})

    print("Get All Users Status Code:", response.status_code)
    print("Get All Users Response:", response.text)

    assert response.status_code == 200
    response_data = response.json()

    assert "users" in response_data
    assert "total_count" in response_data
    assert isinstance(response_data["users"], list)
    assert response_data["total_count"] >= 2  # Как минимум 2 созданных пользователя

    # Проверяем структуру ответа
    if len(response_data["users"]) > 0:
        user = response_data["users"][0]
        assert "id" in user
        assert "username" in user
        assert "email" in user
        assert "firstname" in user
        assert "lastname" in user


@pytest.mark.asyncio
async def test_get_user_by_id(session):
    """Тест получения пользователя по ID"""
    # Сначала создаем пользователя
    user_data = {
        "username": "get_user_test",
        "email": "get_user@example.com",
        "firstname": "Get",
        "lastname": "User",
    }

    async with AsyncTestClient(app=app) as ac:
        create_response = await ac.post("/users/", json=user_data)
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]

        # Получаем пользователя по ID
        response = await ac.get(f"/users/{user_id}")

    print("Get User By ID Status Code:", response.status_code)
    print("Get User By ID Response:", response.text)

    assert response.status_code == 200
    user_response = response.json()

    assert user_response["id"] == user_id
    assert user_response["username"] == "get_user_test"
    assert user_response["email"] == "get_user@example.com"
    assert user_response["firstname"] == "Get"
    assert user_response["lastname"] == "User"


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(session):
    """Тест получения несуществующего пользователя"""
    non_existent_id = str(uuid.uuid4())

    async with AsyncTestClient(app=app) as ac:
        response = await ac.get(f"/users/{non_existent_id}")

    print("Get Non-existent User Status Code:", response.status_code)
    print("Get Non-existent User Response:", response.text)

    assert response.status_code == 404
    error_response = response.json()
    assert "detail" in error_response
    assert f"User with ID {non_existent_id} not found" in error_response["detail"]


@pytest.mark.asyncio
async def test_update_user(session):
    """Тест обновления пользователя"""
    # Сначала создаем пользователя
    user_data = {
        "username": "update_user_test",
        "email": "update_user@example.com",
        "firstname": "Before",
        "lastname": "Update",
    }

    async with AsyncTestClient(app=app) as ac:
        create_response = await ac.post("/users/", json=user_data)
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]

        # Обновляем пользователя
        update_data = {
            "firstname": "After",
            "lastname": "Updated",
            "email": "updated@example.com"
        }
        response = await ac.put(f"/users/{user_id}", json=update_data)

    print("Update User Status Code:", response.status_code)
    print("Update User Response:", response.text)

    assert response.status_code == 200
    user_response = response.json()

    assert user_response["id"] == user_id
    assert user_response["username"] == "update_user_test"  # username не менялся
    assert user_response["email"] == "updated@example.com"  # email обновился
    assert user_response["firstname"] == "After"  # firstname обновился
    assert user_response["lastname"] == "Updated"  # lastname обновился


@pytest.mark.asyncio
async def test_update_user_not_found(session):
    """Тест обновления несуществующего пользователя"""
    non_existent_id = str(uuid.uuid4())
    update_data = {
        "firstname": "Test",
        "lastname": "User"
    }

    async with AsyncTestClient(app=app) as ac:
        response = await ac.put(f"/users/{non_existent_id}", json=update_data)

    print("Update Non-existent User Status Code:", response.status_code)
    print("Update Non-existent User Response:", response.text)

    assert response.status_code == 404
    error_response = response.json()
    assert "detail" in error_response


@pytest.mark.asyncio
async def test_delete_user(session):
    """Тест удаления пользователя"""
    # Сначала создаем пользователя
    user_data = {
        "username": "delete_user_test",
        "email": "delete_user@example.com",
        "firstname": "Delete",
        "lastname": "User",
    }

    async with AsyncTestClient(app=app) as ac:
        create_response = await ac.post("/users/", json=user_data)
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]

        # Удаляем пользователя
        response = await ac.delete(f"/users/{user_id}")

    print("Delete User Status Code:", response.status_code)

    assert response.status_code == 204  # No Content

    # Проверяем, что пользователь действительно удален из БД
    deleted_user = await session.get(User, user_id)
    assert deleted_user is None


@pytest.mark.asyncio
async def test_delete_user_not_found(session):
    """Тест удаления несуществующего пользователя"""
    non_existent_id = str(uuid.uuid4())

    async with AsyncTestClient(app=app) as ac:
        response = await ac.delete(f"/users/{non_existent_id}")

    print("Delete Non-existent User Status Code:", response.status_code)
    print("Delete Non-existent User Response:", response.text)

    assert response.status_code == 404
    error_response = response.json()
    assert "detail" in error_response




