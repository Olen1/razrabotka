# app/queue_subscribers.py
from app.queue_schemas import OrderMessage, ProductMessage, ExtendedOrderMessage, ExtendedProductMessage
from app.queue_hendlers import queue_handlers
import logging

logger = logging.getLogger(__name__)

def setup_queue_subscribers(broker):
    """Настройка подписчиков на очереди"""

    @broker.subscriber("order")
    async def subscribe_order(order_msg: dict):
        """Обработка сообщений из очереди заказов"""
        try:
            logger.info("Received order message for user: %s", order_msg.get('user_id'))

            if "action" not in order_msg:
                order_msg["action"] = "create"

            await queue_handlers.handle_order_message(order_msg)

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to process order message: %s", e)

    @broker.subscriber("product")
    async def subscribe_product(product_msg: dict):
        """Обработка сообщений из очереди продукции"""
        try:
            logger.info("Received product message: %s", product_msg.get('name'))

            if "action" not in product_msg:
                product_msg["action"] = "create"

            await queue_handlers.handle_product_message(product_msg)

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to process product message: %s", e)

    @broker.subscriber("order_status")
    async def subscribe_order_status(order_msg: dict):
        """Обработка обновлений статусов заказов"""
        try:
            if "action" not in order_msg:
                order_msg["action"] = "update_status"

            await queue_handlers.handle_order_message(order_msg)

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to update order status: %s", e)

    return broker