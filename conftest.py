import pytest
import pytest_asyncio
from litestar.testing import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models.Base import Base
from app.repositories.order_repository import OrderRepository
from app.repositories.product_reposutory import ProductRepository
from app.repositories.user_repository import UserRepository

# Тестовая база данных
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest_asyncio.fixture(scope="session")
def engine():
    return create_async_engine(TEST_DATABASE_URL, echo=True)


@pytest_asyncio.fixture(scope="session")
async def tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def session(engine, tables):
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
def user_repository():
    return UserRepository()


@pytest_asyncio.fixture
def product_repository():
    return ProductRepository()


@pytest_asyncio.fixture
def order_repository():
    return OrderRepository()


@pytest.fixture
def client():
    return TestClient(app=app)
