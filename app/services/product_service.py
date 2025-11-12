from typing import Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.Product import Product
from app.User_schem import ProductCreate, ProductUpdate
from app.repositories.productReposutory import ProductRepository


class ProductService:
    def __init__(self, repo: ProductRepository):
        self.repo = repo

    async def get_by_id(self, session: AsyncSession, product_id: str) -> Optional[Product]:
        return await self.repo.get_by_id(session, product_id)

    async def get_by_filter(
            self,
            session: AsyncSession,
            count: int,
            page: int,
            **kwargs: Any
    ) -> List[Product]:
        return await self.repo.get_by_filter(session, count=count, page=page, **kwargs)

    async def create(self, session: AsyncSession, product_data: ProductCreate) -> Product:
        return await self.repo.create(session, product_data)

    async def update(
            self,
            session: AsyncSession,
            product_id: str,
            product_data: ProductUpdate
    ) -> Product:
        return await self.repo.update(session, product_id, product_data)

    async def delete(self, session: AsyncSession, product_id: str) -> None:
        await self.repo.delete(session, product_id)

    async def get_total_count(self, session: AsyncSession) -> int:
        return await self.repo.get_total_count(session)