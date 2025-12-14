import pytest
import httpx
import asyncio
from typing import AsyncGenerator, Dict, Any
import os

# Базовый URL API
BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8080")

@pytest.fixture(scope="session")
def event_loop():
    """Event loop для асинхронных тестов."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Асинхронный HTTP клиент для тестов."""
    async with httpx.AsyncClient(
            base_url=BASE_URL,
            timeout=30.0,
            follow_redirects=True
    ) as client:
        yield client

@pytest.fixture
def report_data() -> Dict[str, Any]:
    """Тестовые данные для отчетов."""
    return {
        "id": 1,
        "date": "2024-01-15",
        "amount": 1000.50,
        "status": "completed",
        "user_id": 123
    }

@pytest.fixture
def user_data() -> Dict[str, Any]:
    """Тестовые данные для пользователей."""
    return {
        "id": 1,
        "name": "Иван Иванов",
        "email": "ivan@example.com",
        "role": "user",
        "active": True
    }