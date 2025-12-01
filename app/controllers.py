# app/controllers.py
from typing import List, Optional
from litestar import Controller, get, post, put, delete
from litestar.params import Parameter
from litestar.status_codes import HTTP_400_BAD_REQUEST
from litestar.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.product_service import ProductService
from app.services.order_service import OrderService
from app.repositories.product_reposutory import ProductRepository  # Исправлено название
from app.repositories.order_repository import OrderRepository  # Исправлено название
from app.repositories.user_repository import UserRepository  # Исправлено название
from app.queue_schemas  import (
    ProductCreate, ProductUpdate, ProductResponse,
    OrderCreate, OrderUpdate, OrderResponse,
    OrderStatus, ProductStatus, ExtendedOrderMessage, ExtendedProductMessage
)
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class ProductController(Controller):
    path = "/products"

    def __init__(self):
        super().__init__()  # Добавлен вызов super()
        self.product_service = ProductService(ProductRepository())

    @get()
    async def get_products(
            self,
            db_session: AsyncSession,
            page: int = Parameter(ge=1, default=1),
            count: int = Parameter(ge=1, le=100, default=10),
            status: Optional[ProductStatus] = None,
            name: Optional[str] = None,
    ) -> List[ProductResponse]:
        """Получить список продукции с пагинацией"""
        filters = {}
        if status:
            filters["status"] = status
        if name:
            filters["name"] = name

        products = await self.product_service.get_by_filter(
            db_session, count=count, page=page, **filters
        )
        return products

    @get("/{product_id:str}")
    async def get_product(
            self,
            db_session: AsyncSession,
            product_id: str,
    ) -> ProductResponse:
        """Получить продукт по ID"""
        product = await self.product_service.get_by_id(db_session, product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
        return product

    @post()
    async def create_product(
            self,
            db_session: AsyncSession,
            broker,
            data: ProductCreate,
    ) -> ProductResponse:
        """Создать новый продукт"""
        product = await self.product_service.create(db_session, data)

        # Отправляем сообщение в очередь
        product_msg = ExtendedProductMessage(
            id=str(product.id),
            name=product.name,
            description=product.description,
            price=int(product.price),
            stock_quantity=product.stock_quantity,
            action="create"
        )
        await broker.publish(product_msg.dict(), "product")

        logger.info("Product created and message sent: %s", product.id)
        return product

    @put("/{product_id:str}")
    async def update_product(
            self,
            db_session: AsyncSession,
            broker,
            product_id: str,
            data: ProductUpdate,
    ) -> ProductResponse:
        """Обновить продукт"""
        product = await self.product_service.update(db_session, product_id, data)

        # Отправляем сообщение в очередь
        product_msg = ExtendedProductMessage(
            id=product_id,
            name=product.name,
            description=product.description,
            price=int(product.price),
            stock_quantity=product.stock_quantity,
            action="update"
        )
        await broker.publish(product_msg.dict(), "product")

        return product

    @delete("/{product_id:str}")
    async def delete_product(
            self,
            db_session: AsyncSession,
            broker,
            product_id: str,
    ) -> None:
        """Удалить продукт"""
        product = await self.product_service.get_by_id(db_session, product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found")

        await self.product_service.delete(db_session, product_id)

        product_msg = ExtendedProductMessage(
            id=product_id,
            name=product.name,
            price=int(product.price),
            stock_quantity=0,
            action="delete"
        )
        await broker.publish(product_msg.dict(), "product")

    @post("/{product_id:str}/mark-out-of-stock")
    async def mark_product_out_of_stock(
            self,
            db_session: AsyncSession,
            broker,
            product_id: str,
    ) -> ProductResponse:
        """Пометить продукт как закончившийся"""
        product = await self.product_service.get_by_id(db_session, product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found")

        update_data = ProductUpdate(status=ProductStatus.OUT_OF_STOCK)
        product = await self.product_service.update(db_session, product_id, update_data)

        product_msg = ExtendedProductMessage(
            id=product_id,
            name=product.name,
            price=int(product.price),
            stock_quantity=product.stock_quantity,
            action="mark_out_of_stock"
        )
        await broker.publish(product_msg.dict(), "product")

        return product

    @post("/{product_id:str}/update-stock")
    async def update_product_stock(
            self,
            db_session: AsyncSession,
            broker,
            product_id: str,
            stock_quantity: int = Parameter(ge=0),
    ) -> ProductResponse:
        """Обновить количество продукта на складе"""
        product = await self.product_service.get_by_id(db_session, product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found")

        update_data = ProductUpdate(stock_quantity=stock_quantity)
        product = await self.product_service.update(db_session, product_id, update_data)

        product_msg = ExtendedProductMessage(
            id=product_id,
            name=product.name,
            price=int(product.price),
            stock_quantity=product.stock_quantity,
            action="stock_update"
        )
        await broker.publish(product_msg.dict(), "product")

        return product

class OrderController(Controller):
    path = "/orders"

    def __init__(self):
        super().__init__()  # Добавлен вызов super()
        self.order_service = OrderService(
            OrderRepository(),
            ProductRepository(),
            UserRepository()
        )

    @get()
    async def get_orders(
            self,
            db_session: AsyncSession,
            page: int = Parameter(ge=1, default=1),
            count: int = Parameter(ge=1, le=100, default=10),
            status: Optional[OrderStatus] = None,
            user_id: Optional[str] = None,
    ) -> List[OrderResponse]:
        """Получить список заказов с пагинацией"""
        filters = {}
        if status:
            filters["status"] = status
        if user_id:
            filters["user_id"] = user_id

        orders = await self.order_service.get_orders_by_filter(
            db_session, count=count, page=page, **filters  # Исправлено на get_orders_by_filter
        )
        return orders

    @get("/{order_id:str}")
    async def get_order(
            self,
            db_session: AsyncSession,
            order_id: str,
    ) -> OrderResponse:
        """Получить заказ по ID"""
        order = await self.order_service.get_order_by_id(db_session, order_id)
        if not order:
            raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
        return order

    @post()
    async def create_order(
            self,
            db_session: AsyncSession,
            broker,
            data: OrderCreate,
    ) -> OrderResponse:
        """Создать новый заказ"""
        for item in data.items:
            product = await self.order_service.product_repository.get_by_id(db_session, item.product_id)
            if not product:
                raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
            if product.status == ProductStatus.OUT_OF_STOCK:
                raise HTTPException(
                    status_code=400,
                    detail=f"Product {item.product_id} is out of stock"
                )
            if product.stock_quantity < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Not enough stock for product {item.product_id}. "
                           f"Required: {item.quantity}, Available: {product.stock_quantity}"
                )

        order = await self.order_service.create_order(db_session, data)

        order_msg = ExtendedOrderMessage(
            order_id=str(order.id),
            user_id=order.user_id,
            address_id=order.address_id,
            items=[{"product_id": item.product_id, "quantity": item.quantity} for item in data.items],
            action="create"
        )
        await broker.publish(order_msg.dict(), "order")

        logger.info("Order created and message sent: %s", order.id)
        return order

    @put("/{order_id:str}")
    async def update_order(
            self,
            db_session: AsyncSession,
            broker,
            order_id: str,
            data: OrderUpdate,
    ) -> OrderResponse:
        """Обновить заказ (в основном статус)"""
        order = await self.order_service.update_order(db_session, order_id, data)

        if data.status:
            order_msg = ExtendedOrderMessage(
                order_id=order_id,
                user_id=order.user_id,
                address_id=order.address_id,
                items=[],
                status=data.status,
                action="update_status"
            )
            await broker.publish(order_msg.dict(), "order_status")

        return order

    @delete("/{order_id:str}")
    async def delete_order(
            self,
            db_session: AsyncSession,
            order_id: str,
    ) -> None:
        """Удалить заказ"""
        order = await self.order_service.get_order_by_id(db_session, order_id)
        if not order:
            raise HTTPException(status_code=404, detail=f"Order {order_id} not found")

        await self.order_service.delete_order(db_session, order_id)

    @post("/{order_id:str}/cancel")
    async def cancel_order(
            self,
            db_session: AsyncSession,
            broker,
            order_id: str,
    ) -> OrderResponse:
        """Отменить заказ"""
        order = await self.order_service.get_order_by_id(db_session, order_id)
        if not order:
            raise HTTPException(status_code=404, detail=f"Order {order_id} not found")

        update_data = OrderUpdate(status=OrderStatus.CANCELLED)
        order = await self.order_service.update_order(db_session, order_id, update_data)

        order_msg = ExtendedOrderMessage(
            order_id=order_id,
            user_id=order.user_id,
            address_id=order.address_id,
            items=[],
            status=OrderStatus.CANCELLED,
            action="update_status"
        )
        await broker.publish(order_msg.dict(), "order_status")

        return order