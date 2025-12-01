# app/queue_handlers.py
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.database import async_session_maker
from app.services.product_service import ProductService
from app.services.order_service import OrderService
from app.repositories.product_reposutory import ProductRepository  # Исправлено
from app.repositories.order_repository import OrderRepository  # Исправлено
from app.repositories.user_repository import UserRepository  # Исправлено
from app.queue_schemas import ExtendedOrderMessage, ExtendedProductMessage, OrderStatus, ProductStatus, OrderCreate, ProductCreate, ProductUpdate
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

class QueueHandlers:
    def __init__(self):
        self.product_service = ProductService(ProductRepository())
        self.order_service = OrderService(
            OrderRepository(),
            ProductRepository(),
            UserRepository()
        )

    async def _get_db_session(self) -> AsyncSession:
        return async_session_maker()

    async def handle_product_message(self, product_msg: dict) -> None:
        """Обработка сообщений о продукции"""
        session = await self._get_db_session()
        try:
            extended_msg = ExtendedProductMessage(**product_msg)
            action = extended_msg.action

            if action == "create":
                product_data = ProductCreate(
                    name=extended_msg.name,
                    description=extended_msg.description,
                    price=Decimal(extended_msg.price),
                    stock_quantity=extended_msg.stock_quantity,
                    status=ProductStatus.AVAILABLE
                )
                product = await self.product_service.create(session, product_data)
                logger.info("Product created: %s - %s", product.id, product.name)

            elif action == "update":
                update_data = ProductUpdate(
                    name=extended_msg.name,
                    description=extended_msg.description,
                    price=Decimal(extended_msg.price),
                    stock_quantity=extended_msg.stock_quantity
                )
                product = await self.product_service.update(session, extended_msg.id, update_data)
                logger.info("Product updated: %s", extended_msg.id)

            elif action == "delete":
                await self.product_service.delete(session, extended_msg.id)
                logger.info("Product deleted: %s", extended_msg.id)

            elif action == "stock_update":
                update_data = ProductUpdate(stock_quantity=extended_msg.stock_quantity)
                await self.product_service.update(session, extended_msg.id, update_data)
                logger.info("Product stock updated: %s -> %s", extended_msg.id, extended_msg.stock_quantity)

            elif action == "mark_out_of_stock":
                update_data = ProductUpdate(status=ProductStatus.OUT_OF_STOCK)
                await self.product_service.update(session, extended_msg.id, update_data)
                logger.info("Product marked as out of stock: %s", extended_msg.id)

            await session.commit()

        except Exception as e:  # pylint: disable=broad-except
            await session.rollback()
            logger.error("Error processing product message: %s", e)
            raise
        finally:
            await session.close()

    async def handle_order_message(self, order_msg: dict) -> None:
        """Обработка сообщений о заказах"""
        session = await self._get_db_session()
        try:
            extended_msg = ExtendedOrderMessage(**order_msg)
            action = extended_msg.action

            if action == "create":
                for item in extended_msg.items:
                    product = await self.product_service.get_by_id(session, item.product_id)
                    if not product:
                        raise ValueError(f"Product {item.product_id} not found")
                    if product.status == ProductStatus.OUT_OF_STOCK:
                        raise ValueError(f"Product {item.product_id} is out of stock")
                    if product.stock_quantity < item.quantity:
                        raise ValueError(
                            f"Not enough stock for product {item.product_id}. "
                            f"Required: {item.quantity}, Available: {product.stock_quantity}"
                        )

                order_data = OrderCreate(
                    user_id=extended_msg.user_id,
                    address_id=extended_msg.address_id,
                    items=[{"product_id": item.product_id, "quantity": item.quantity} for item in extended_msg.items]
                )

                order = await self.order_service.create_order(session, order_data)
                logger.info("Order created successfully: %s for user %s", order.id, order.user_id)

            elif action == "update_status" and extended_msg.order_id:
                if not extended_msg.status:
                    raise ValueError("Status is required for update_status action")

                update_data = {"status": extended_msg.status}
                order = await self.order_service.update_order(session, extended_msg.order_id, update_data)
                logger.info("Order status updated: %s -> %s", extended_msg.order_id, extended_msg.status)

            await session.commit()

        except Exception as e:  # pylint: disable=broad-except
            await session.rollback()
            logger.error("Error processing order message: %s", e)

            if action == "create":
                logger.error("Failed to create order for user %s: %s", extended_msg.user_id, e)

            raise
        finally:
            await session.close()

# Создаем экземпляр обработчиков
queue_handlers = QueueHandlers()