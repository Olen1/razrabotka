import pytest
from unittest.mock import Mock, AsyncMock

from app.repositories.OrderRepository import OrderRepository
from app.repositories.productReposutory import ProductRepository
from app.repositories.user_repository import UserRepository
from app.services.order_service import OrderService  # Убедитесь, что путь правильный
from app.User_schem import OrderCreate, OrderItemCreate


class TestOrderService:
    @pytest.mark.asyncio
    async def test_create_order_success(self, session, order_repository, product_repository, user_repository):
        """Тест успешного создания заказа через OrderService"""
        # Мокаем репозитории
        mock_order_repo = AsyncMock(spec=OrderRepository)
        mock_product_repo = AsyncMock(spec=ProductRepository)
        mock_user_repo = AsyncMock(spec=UserRepository)

        # Настраиваем моки
        mock_user_repo.get_by_id.return_value = Mock(id="1", email="test@example.com") # id тоже строка
        mock_product_repo.get_by_id.return_value = Mock(
            id="1", name="Test Product", price=100.0, stock_quantity=5
        )
        mock_order_repo.create.return_value = Mock(
            id="1", user_id="1", total_amount=200.0, status="pending"
        )

        order_service = OrderService(
            order_repository=mock_order_repo,
            product_repository=mock_product_repo,
            user_repository=mock_user_repo
        )

        # Подготовим данные заказа как Pydantic-схему
        order_item_data = OrderItemCreate(product_id="1", quantity=2)
        order_data = OrderCreate(
            user_id="1",
            address_id="1",
            items=[order_item_data]
        )


        result = await order_service.create_order(session, order_data)

        # Проверки
        assert result is not None
        assert result.total_amount == 200.0
        assert result.user_id == "1"

        # Проверим, что метод create был вызван у репозитория
        mock_order_repo.create.assert_called_once()