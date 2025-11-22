from typing import Any, List, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.Product import Product
from app.User_schem import ProductCreate, ProductUpdate


class ProductRepository:
    def __init__(self):
        pass

    async def get_by_id(
        self, session: AsyncSession, product_id: str
    ) -> Optional[Product]:
        """
        Получить продукт по ID.
        """
        result = await session.execute(select(Product).where(Product.id == product_id))
        return result.scalar_one_or_none()

    async def get_by_filter(
        self, session: AsyncSession, count: int, page: int, **kwargs: Any
    ) -> List[Product]:
        """
        Получить продукты по фильтрам (пагинация).
        """
        query = select(Product)

        filters = []
        for key, value in kwargs.items():
            if not hasattr(Product, key):
                continue
            column = getattr(Product, key)
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

    async def create(
        self, session: AsyncSession, product_data: ProductCreate
    ) -> Product:
        """
        Создать продукт.
        """
        product_dict = product_data.model_dump(exclude_unset=True)
        db_product = Product(**product_dict)
        session.add(db_product)
        await session.commit()
        await session.refresh(db_product)
        return db_product

    async def update(
        self, session: AsyncSession, product_id: str, product_data: ProductUpdate
    ) -> Product:
        """
        Обновить продукт.
        """
        db_product = await self.get_by_id(session, product_id)
        if db_product is None:
            raise ValueError(f"Product with id {product_id} not found")

        update_data = product_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_product, field):
                setattr(db_product, field, value)

        session.add(db_product)
        await session.commit()
        await session.refresh(db_product)
        return db_product

    async def delete(self, session: AsyncSession, product_id: str) -> None:
        """
        Удалить продукт.
        """
        db_product = await self.get_by_id(session, product_id)
        if db_product is not None:
            await session.delete(db_product)
            await session.commit()

    # === НОВОЕ: Метод для уменьшения stock_quantity ===
    async def decrease_stock(
        self, session: AsyncSession, product_id: str, quantity: int
    ) -> bool:
        """
        Уменьшает stock_quantity на указанное количество.
        Возвращает True, если успешно, False, если недостаточно товара.
        """
        db_product = await self.get_by_id(session, product_id)
        if db_product is None:
            raise ValueError(f"Product with id {product_id} not found")

        if db_product.stock_quantity < quantity:
            return False  # Недостаточно товара

        db_product.stock_quantity -= quantity
        session.add(db_product)
        await session.commit()
        await session.refresh(db_product)
        return True

    async def get_total_count(self, session: AsyncSession) -> int:
        """
        Получить общее количество продуктов.
        """
        result = await session.execute(select(func.count(Product.id)))
        return result.scalar_one()
