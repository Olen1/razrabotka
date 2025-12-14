from typing import List

from litestar import Controller, delete, get, post, put
from litestar.exceptions import NotFoundException
from litestar.params import Parameter
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.product_service import ProductService
from app.User_schem import (
    ProductCreate,
    ProductResponse,
    ProductsListResponse,
    ProductUpdate,
)


class ProductController(Controller):
    path = "/products"


    @get("/")
    async def get_all_products(
        self,
        product_service: ProductService,
        session: AsyncSession,
        count: int = Parameter(default=10, gt=0, le=100),
        page: int = Parameter(default=1, gt=0),
    ) -> ProductsListResponse:
        products = await product_service.get_by_filter(session, count=count, page=page)
        total_count = await product_service.get_total_count(session)
        return ProductsListResponse(
            products=[ProductResponse.model_validate(product) for product in products],
            total_count=total_count,
        )

    @get("/{product_id:str}")
    async def get_product_by_id(
        self,
        product_service: ProductService,
        session: AsyncSession,
        product_id: str,
    ) -> ProductResponse:
        product = await product_service.get_by_id(session, product_id)
        if not product:
            raise NotFoundException(detail=f"Product with ID {product_id} not found")
        return ProductResponse.model_validate(product)

    @post("/")
    async def create_product(
        self,
        product_service: ProductService,
        session: AsyncSession,
        data: ProductCreate,
    ) -> ProductResponse:
        product = await product_service.create(session, data)
        return ProductResponse.model_validate(product)

    @put("/{product_id:str}")
    async def update_product(
        self,
        product_service: ProductService,
        session: AsyncSession,
        product_id: str,
        data: ProductUpdate,
    ) -> ProductResponse:
        product = await product_service.update(session, product_id, data)
        return ProductResponse.model_validate(product)

    @delete("/{product_id:str}")
    async def delete_product(
        self,
        product_service: ProductService,
        session: AsyncSession,
        product_id: str,
    ) -> None:
        await product_service.delete(session, product_id)
