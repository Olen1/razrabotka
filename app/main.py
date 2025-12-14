# app/main.py (исправленная версия)
from datetime import datetime
import os

from litestar import Litestar, get, post
from litestar.di import Provide
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import asyncio

# Отключаем предупреждения
os.environ["LITESTAR_WARN_SYNC_TO_THREAD_WITH_GENERATOR"] = "0"

DATABASE_URL = "sqlite+aiosqlite:///./data/test.db"
engine = create_async_engine(DATABASE_URL)
async_session_factory = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

@get("/")
async def root() -> dict:
    """Корневой эндпоинт"""
    return {
        "message": "API работает успешно!",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "GET /api/reports": "Получить отчеты",
            "GET /api/users": "Получить пользователей",
            "GET /api/products": "Получить продукты",
            "GET /api/orders": "Получить заказы",
            "GET /health": "Health check",
            "GET /schema": "Документация"
        }
    }

@get("/health")
async def health_check() -> dict:
    """Health check"""
    return {
        "status": "healthy",
        "service": "Order Management API",
        "timestamp": datetime.now().isoformat()
    }

# ========== ПРОСТЫЕ ЭНДПОИНТЫ ДЛЯ ТЕСТА ==========

@get("/api/reports")
async def get_reports(date: str = "2024-01-01") -> dict:
    """GET: Получить отчеты"""
    return {
        "endpoint": "/api/reports",
        "method": "GET",
        "date": date,
        "data": [
            {"id": 1, "report_date": date, "amount": 1000.50, "status": "completed"},
            {"id": 2, "report_date": date, "amount": 2000.75, "status": "pending"}
        ],
        "total": 3001.25
    }

@get("/api/users")
async def get_users(limit: int = 10) -> dict:
    """GET: Получить пользователей"""
    return {
        "endpoint": "/api/users",
        "method": "GET",
        "users": [
            {"id": 1, "name": "Иван Иванов", "email": "ivan@example.com"},
            {"id": 2, "name": "Мария Петрова", "email": "maria@example.com"},
            {"id": 3, "name": "Алексей Сидоров", "email": "alex@example.com"}
        ][:limit]
    }

@get("/api/products")
async def get_products() -> dict:
    """GET: Получить продукты"""
    return {
        "endpoint": "/api/products",
        "method": "GET",
        "products": [
            {"id": 1, "name": "Ноутбук", "price": 50000.0, "category": "электроника"},
            {"id": 2, "name": "Смартфон", "price": 30000.0, "category": "электроника"},
            {"id": 3, "name": "Книга", "price": 500.0, "category": "литература"}
        ]
    }

@get("/api/orders")
async def get_orders() -> dict:
    """GET: Получить заказы"""
    return {
        "endpoint": "/api/orders",
        "method": "GET",
        "orders": [
            {"id": 1, "user_id": 1, "total": 50500.0, "status": "completed"},
            {"id": 2, "user_id": 2, "total": 30000.0, "status": "processing"}
        ]
    }

async def provide_db_session() -> AsyncSession:
    """Dependency для сессии базы данных"""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()

async def create_tables():
    """Создание таблиц"""
    try:
        # Создаем папку data если её нет
        os.makedirs("./data", exist_ok=True)

        # Импортируем Base только когда нужно
        from app.models.Base import Base

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Таблицы базы данных созданы")
    except Exception as e:
        print(f"Не удалось создать таблицы: {e}")

# Создаем приложение
app = Litestar(
    route_handlers=[
        root,
        health_check,
        get_reports,
        get_users,
        get_products,
        get_orders
    ],
    dependencies={
        "session": Provide(provide_db_session),
    },
    debug=True
)

if __name__ == "__main__":
    # Создаем таблицы
    asyncio.run(create_tables())


    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8080,
        reload=True
    )