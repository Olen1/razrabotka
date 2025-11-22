import pytest

from app.models.Product import Product
from app.repositories.productReposutory import ProductRepository
from app.User_schem import ProductCreate, ProductUpdate


class TestProductRepository:
    @pytest.mark.asyncio
    async def test_create_product(self, session, product_repository: ProductRepository):
        """Тест создания продукта"""
        product_data = {
            "name": "Test Product",
            "price": 1000,
            "description": "A test product",
            "stock_quantity": 50,
        }

        product_create_schema = ProductCreate(**product_data)
        product = await product_repository.create(session, product_create_schema)

        assert product.id is not None
        assert product.name == "Test Product"
        assert product.price == 1000
        assert product.stock_quantity == 50

        # Проверим, что продукт действительно в БД
        fetched_product = await session.get(Product, product.id)
        assert fetched_product is not None
        assert fetched_product.id == product.id

    @pytest.mark.asyncio
    async def test_update_product(self, session, product_repository: ProductRepository):
        """Тест обновления продукта"""
        # Сначала создаём продукт
        product_data = {
            "name": "Original Product",
            "price": 500,
            "description": "Original description",
            "stock_quantity": 10,
        }
        product_create_schema = ProductCreate(**product_data)
        product = await product_repository.create(session, product_create_schema)

        # Подготовим данные для обновления
        update_data = {
            "name": "Updated Product",
            "stock_quantity": 20,
        }
        product_update_schema = ProductUpdate(**update_data)

        # Обновляем
        updated_product = await product_repository.update(
            session, product.id, product_update_schema
        )

        assert updated_product.name == "Updated Product"
        assert updated_product.price == 500  # не изменилось
        assert updated_product.stock_quantity == 20

    @pytest.mark.asyncio
    async def test_get_all_products(
        self, session, product_repository: ProductRepository
    ):
        """Тест получения списка продуктов"""
        # Сначала создаём несколько продуктов
        products_data = [
            {
                "name": "Product One",
                "price": 100,
                "description": "First product",
                "stock_quantity": 5,
            },
            {
                "name": "Product Two",
                "price": 200,
                "description": "Second product",
                "stock_quantity": 10,
            },
        ]

        created_products = []
        for data in products_data:
            product_create_schema = ProductCreate(**data)
            product = await product_repository.create(session, product_create_schema)
            created_products.append(product)

        # Получаем список
        products_list = await product_repository.get_by_filter(
            session, count=10, page=1
        )

        # Проверяем, что все созданные продукты есть в списке
        assert len(products_list) >= 2
        product_ids = {p.id for p in products_list}
        for product in created_products:
            assert product.id in product_ids

    @pytest.mark.asyncio
    async def test_get_product_by_id(
        self, session, product_repository: ProductRepository
    ):
        """Тест получения продукта по ID"""
        # Сначала создаём продукт
        product_data = {
            "name": "Find Me Product",
            "price": 300,
            "description": "Findable product",
            "stock_quantity": 15,
        }
        product_create_schema = ProductCreate(**product_data)
        product = await product_repository.create(session, product_create_schema)

        # Получаем по ID
        fetched_product = await product_repository.get_by_id(session, product.id)

        assert fetched_product is not None
        assert fetched_product.id == product.id
        assert fetched_product.name == "Find Me Product"

    @pytest.mark.asyncio
    async def test_delete_product(self, session, product_repository: ProductRepository):
        """Тест удаления продукта"""
        # Сначала создаём продукт
        product_data = {
            "name": "Delete Me Product",
            "price": 400,
            "description": "To be deleted",
            "stock_quantity": 1,
        }
        product_create_schema = ProductCreate(**product_data)
        product = await product_repository.create(session, product_create_schema)

        # Проверим, что он существует
        fetched_product = await session.get(Product, product.id)
        assert fetched_product is not None

        # Удаляем
        await product_repository.delete(session, product.id)

        # Проверим, что его больше нет
        deleted_product = await session.get(Product, product.id)
        assert deleted_product is None
