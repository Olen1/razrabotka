# app/main.py
from litestar import Litestar
from litestar.di import Provide
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.controllers.user_controller import UserController
from app.controllers.product_controller import ProductController
from app.controllers.order_controller import OrderController
from app.repositories.OrderRepository import OrderRepository

from app.repositories.productReposutory import ProductRepository
from app.repositories.user_repository import UserRepository


from app.services.user_service import UserService
from app.services.product_service import ProductService
from app.services.order_service import OrderService

from app.models.User import User
from app.models.Product import Product
from app.models.Order import Order
from app.models.OrderItem import OrderItem
from app.models.Address import Address
from app.models.Base import Base


DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(DATABASE_URL)
async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def provide_db_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session


def provide_user_repo() -> UserRepository:
    return UserRepository()


def provide_product_repo() -> ProductRepository:
    return ProductRepository()


def provide_order_repo() -> OrderRepository:
    return OrderRepository()


def provide_user_service(user_repo: UserRepository) -> UserService:
    return UserService(repo=user_repo)


def provide_product_service(product_repo: ProductRepository) -> ProductService:
    return ProductService(repo=product_repo)


def provide_order_service(
        order_repo: OrderRepository,
        product_repo: ProductRepository,
        user_repo: UserRepository
) -> OrderService:
    return OrderService(
        order_repository=order_repo,
        product_repository=product_repo,
        user_repository=user_repo
    )


app = Litestar(
    route_handlers=[UserController, ProductController, OrderController],
    dependencies={
        "session": Provide(provide_db_session),
        "user_repo": Provide(provide_user_repo),
        "product_repo": Provide(provide_product_repo),
        "order_repo": Provide(provide_order_repo),
        "user_service": Provide(provide_user_service),
        "product_service": Provide(provide_product_service),
        "order_service": Provide(provide_order_service),
    },
)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    import asyncio
    import uvicorn

    asyncio.run(create_tables())

    uvicorn.run(app, host="0.0.0.0", port=8000)