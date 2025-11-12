import pytest
from unittest.mock import Mock, AsyncMock

from app.repositories.OrderRepository import OrderRepository
from app.repositories.productReposutory import ProductRepository
from app.repositories.user_repository import UserRepository
from app.services import order_service
from app.services.order_service import OrderService
from app.User_schem import OrderCreate, OrderItemCreate


class TestOrderService2:
    @pytest.mark.asyncio
    async def test_create_order_insufficient_stock(self, session):
        """Тест создания заказа с недостаточным количеством товара"""
        # Мокаем репозитории
        mock_order_repo = AsyncMock(spec=OrderRepository)
        mock_product_repo = AsyncMock(spec=ProductRepository)
        mock_user_repo = AsyncMock(spec=UserRepository)

        # Настраиваем моки
        mock_user_repo.get_by_id.return_value = Mock(id="1")
        mock_product_repo.get_by_id.return_value = Mock(
            id="1", name="Test Product", price=100.0, stock_quantity=1
        )

        order_service = OrderService(
            order_repository=mock_order_repo,
            product_repository=mock_product_repo,
            user_repository=mock_user_repo
        )

        # Подготовим данные заказа как Pydantic-схему
        order_item_data = OrderItemCreate(product_id="1", quantity=5)
        order_data = OrderCreate(
            user_id="1",
            address_id="1",
            items=[order_item_data]
        )


        with pytest.raises(ValueError, match="Not enough stock"):
           await order_service.create_order(session, order_data)