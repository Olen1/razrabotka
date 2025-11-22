from models.Base import Base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Используем aiosqlite для SQLite в асинхронном режиме
DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(DATABASE_URL, echo=False, future=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def init_db():
    """Создаёт таблицы при первом запуске (только для разработки!)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
