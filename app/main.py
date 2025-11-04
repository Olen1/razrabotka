import os
import asyncio
from litestar import Litestar
from litestar.di import Provide
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.controllers.user_controller import UserController
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

from app.models.User import User
from app.models.Address import Address
from app.models.Product import Product
from app.models.Order import Order
from app.models.Base import Base


#  Настройка БД
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_async_engine(DATABASE_URL, echo=True, connect_args=connect_args)
async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Провайдеры
async def provide_db_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session

def provide_user_repository() -> UserRepository:
    return UserRepository()

def provide_user_service(user_repository: UserRepository) -> UserService:
    return UserService(user_repository=user_repository)


app = Litestar(
    route_handlers=[UserController],
    dependencies={
        "session": Provide(provide_db_session),
        "user_repository": Provide(provide_user_repository, sync_to_thread=False),
        "user_service": Provide(provide_user_service, sync_to_thread=False),
    },
)

#  Инициализация БД
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(create_tables())
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)