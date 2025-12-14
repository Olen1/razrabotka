from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.Order import Order
from app.repositories import order_repository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_reposutory import ProductRepository
from app.repositories.user_repository import UserRepository
from app.User_schem import (
    OrderCreate,
    OrderItemCreate,
    OrderItemResponse,
    OrderResponse,
    OrderUpdate,
)


class OrderService:
    def __init__(
        self,
        order_repository: OrderRepository,
        product_repository: ProductRepository,
        user_repository: UserRepository,
    ):
        self.order_repository = order_repository
        self.product_repository = product_repository
        self.user_repository = user_repository

    async def create_order(
        self, session: AsyncSession, order_data: OrderCreate
    ) -> Order:
        """
        Создаёт заказ.
        Проверяет существование пользователя и продуктов, уменьшает stock.
        """
        user_id = order_data.user_id
        items_data = order_data.items

        user = await self.user_repository.get_by_id(session, user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")

        total_amount = 0
        validated_items = []
        for item_data in items_data:
            product_id = item_data.product_id
            quantity = item_data.quantity

            if quantity <= 0:
                raise ValueError(f"Quantity must be positive for product {product_id}")

            # Получаем продукт
            product = await self.product_repository.get_by_id(session, product_id)
            if not product:
                raise ValueError(f"Product with id {product_id} not found")
            if product.stock_quantity < quantity:
                raise ValueError(
                    f"Not enough stock for product {product_id}. Required: {quantity}, Available: {product.stock_quantity}"
                )

            total_amount += product.price * quantity
            # validated_items.append(OrderItemCreate(product_id=product_id, quantity=quantity)) # OrderItemCreate не нужен, передаём как есть

        for item_data in items_data:
            success = await self.product_repository.decrease_stock(
                session, item_data.product_id, item_data.quantity
            )
            if not success:
                raise ValueError(
                    f"Failed to decrease stock for product {item_data.product_id}"
                )

        order = await self.order_repository.create(
            session, order_data, self.product_repository
        )

        return order

    async def get_order_by_id(
        self, session: AsyncSession, order_id: str
    ) -> Optional[Order]:
        """
        Получает заказ по ID.
        """
        return await self.order_repository.get_by_id(session, order_id)

    async def get_orders_by_filter(
        self, session: AsyncSession, count: int, page: int, **kwargs: Any
    ) -> List[Order]:
        """
        Получает список заказов по фильтрам (пагинация).
        """
        return await self.order_repository.get_by_filter(
            session, count=count, page=page, **kwargs
        )

    async def get_total_orders_count(self, session: AsyncSession) -> int:
        """
        Получает общее количество заказов.
        """
        return await self.order_repository.get_total_count(session)

    async def update_order(
        self, session: AsyncSession, order_id: str, order_data: OrderUpdate
    ) -> Order:
        """
        Обновляет заказ (обычно только user_id и address_id).
        """
        # Проверим, что заказ существует
        existing_order = await self.order_repository.get_by_id(session, order_id)
        if not existing_order:
            raise ValueError(f"Order with id {order_id} not found")

        # Обновим заказ
        updated_order = await self.order_repository.update(
            session, order_id, order_data
        )
        return updated_order

    async def delete_order(self, session: AsyncSession, order_id: str) -> None:
        """
        Удаляет заказ.
        """
        # Проверим, что заказ существует
        existing_order = await self.order_repository.get_by_id(session, order_id)
        if not existing_order:
            raise ValueError(f"Order with id {order_id} not found")

        # Удалим заказ
        await self.order_repository.delete(session, order_id)
