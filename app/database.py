
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# Используем aiosqlite для асинхронной работы с SQLite
DATABASE_URL = "sqlite+aiosqlite:///./app.db"

# Создаем асинхронный движок
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Логирование SQL запросов
    future=True,
    connect_args={"check_same_thread": False},  # Важно для SQLite
)

# Создаем фабрику сессий
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def create_tables():
    """Создание таблиц в базе данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db_session() -> AsyncSession:
    """
    Генератор сессий базы данных.
    Используется как dependency в Litestar.
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


provide_db_session = get_db_session
