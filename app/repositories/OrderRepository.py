from typing import Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from app.models.Order import Order
from app.models.OrderItem import OrderItem
from app.User_schem import OrderCreate, OrderUpdate
from app.repositories.productReposutory import ProductRepository  # ← Исправлено: product_repository, а не productReposutory


class OrderRepository:
    def __init__(self):
        pass

    async def get_by_id(self, session: AsyncSession, order_id: str) -> Optional[Order]:
        """
        Получить заказ по ID (включая связанные OrderItem).
        """
        result = await session.execute(
            select(Order)
            .where(Order.id == order_id)
        )
        return result.scalar_one_or_none()

    async def get_by_filter(
            self,
            session: AsyncSession,
            count: int,
            page: int,
            **kwargs: Any
    ) -> List[Order]:
        """
        Получить заказы по фильтрам (пагинация).
        """
        query = select(Order)

        filters = []
        for key, value in kwargs.items():
            if not hasattr(Order, key):
                continue
            column = getattr(Order, key)
            if isinstance(value, str) and "%" in value:
                filters.append(column.like(value))
            else:
                filters.append(column == value)

        if filters:
            query = query.where(and_(*filters))

        offset = (page - 1) * count if page > 0 else 0
        query = query.offset(offset).limit(count)

        result = await session.execute(query)
        return list(result.scalars().all())

    async def create(self, session: AsyncSession, order_data: OrderCreate, product_repository: ProductRepository) -> Order:
        """
        Создать заказ.
        """
        # Проверяем, что все товары в заказе существуют и доступны в нужном количестве
        for item_data in order_data.items:
            product = await product_repository.get_by_id(session, item_data.product_id)
            if product is None:
                raise ValueError(f"Product with id {item_data.product_id} not found")
            if product.stock_quantity < item_data.quantity:
                raise ValueError(f"Not enough stock for product {item_data.product_id}. Required: {item_data.quantity}, Available: {product.stock_quantity}")

        # Создаём Order
        order_dict = order_data.model_dump(exclude_unset=True, exclude={'items'})
        db_order = Order(**order_dict)

        # Создаём OrderItem и привязываем к Order
        for item_data in order_data.items:
            # Уменьшаем stock_quantity в Product (опционально, можно делать в сервисе)
            success = await product_repository.decrease_stock(session, item_data.product_id, item_data.quantity)
            if not success:
                # Если не удалось уменьшить stock, откатываем транзакцию
                # (session.rollback() вызывается автоматически при исключении)
                raise ValueError(f"Stock reduction failed for product {item_data.product_id}")

            db_item = OrderItem(
                product_id=item_data.product_id,
                quantity=item_data.quantity
            )
            db_order.items.append(db_item) # Привязываем к заказу

        session.add(db_order)
        await session.commit()
        await session.refresh(db_order)
        return db_order

    async def update(
            self,
            session: AsyncSession,
            order_id: str,
            order_data: OrderUpdate
    ) -> Order:
        """
        Обновить заказ (обычно только user_id и address_id).
        """
        db_order = await self.get_by_id(session, order_id)
        if db_order is None:
            raise ValueError(f"Order with id {order_id} not found")

        update_data = order_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_order, field):
                setattr(db_order, field, value)

        session.add(db_order)
        await session.commit()
        await session.refresh(db_order)
        return db_order

    async def delete(self, session: AsyncSession, order_id: str) -> None:
        """
        Удалить заказ (и связанные OrderItem из-за cascade="all, delete-orphan").
        """
        db_order = await self.get_by_id(session, order_id)
        if db_order is not None:
            await session.delete(db_order)
            await session.commit()


    async def get_total_count(self, session: AsyncSession) -> int:
        """
        Получить общее количество заказов.
        """
        result = await session.execute(select(func.count(Order.id)))
        return result.scalar_one()