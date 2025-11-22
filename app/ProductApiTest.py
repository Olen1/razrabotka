import uuid

import pytest
from litestar.testing import AsyncTestClient

from app.main import app
from app.models.Product import Product


@pytest.mark.asyncio
async def test_create_product(session):
    """Тест создания продукта"""
    product_data = {
        "name": "Test Product",
        "price": 1000,
        "description": "Test description",
        "stock_quantity": 50,
    }

    async with AsyncTestClient(app=app) as ac:
        response = await ac.post("/products/", json=product_data)

    print("Create Product Status:", response.status_code)
    print("Create Product Response:", response.text)

    assert response.status_code == 201
    product_response = response.json()

    assert product_response["name"] == "Test Product"
    assert product_response["price"] == 1000
    assert product_response["description"] == "Test description"
    assert product_response["stock_quantity"] == 50
    assert "id" in product_response

    # Проверка в БД
    fetched_product = await session.get(Product, product_response["id"])
    assert fetched_product is not None

    return product_response["id"]


@pytest.mark.asyncio
async def test_get_all_products(session):
    """Тест получения всех продуктов"""
    async with AsyncTestClient(app=app) as ac:
        response = await ac.get("/products/", params={"count": 10, "page": 1})

    print("Get All Products Status:", response.status_code)

    assert response.status_code == 200
    response_data = response.json()

    assert "products" in response_data
    assert "total_count" in response_data
    assert isinstance(response_data["products"], list)

    # Проверяем структуру продуктов
    if response_data["products"]:
        product = response_data["products"][0]
        assert "id" in product
        assert "name" in product
        assert "price" in product
        assert "stock_quantity" in product


@pytest.mark.asyncio
async def test_get_all_products_default_params(session):
    """Тест получения продуктов с параметрами по умолчанию"""
    async with AsyncTestClient(app=app) as ac:
        response = await ac.get("/products/")

    print("Get Products Default Params Status:", response.status_code)

    assert response.status_code == 200
    response_data = response.json()
    assert "products" in response_data
    assert "total_count" in response_data


@pytest.mark.asyncio
async def test_get_product_by_id(session):
    """Тест получения продукта по ID"""
    # Сначала создаем продукт
    product_data = {
        "name": "Get By ID Product",
        "price": 2000,
        "description": "Get by ID description",
        "stock_quantity": 25,
    }

    async with AsyncTestClient(app=app) as ac:
        create_response = await ac.post("/products/", json=product_data)
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]

        # Получаем по ID
        response = await ac.get(f"/products/{product_id}")

    print("Get Product By ID Status:", response.status_code)

    assert response.status_code == 200
    product_response = response.json()
    assert product_response["id"] == product_id
    assert product_response["name"] == "Get By ID Product"
    assert product_response["price"] == 2000
    assert product_response["stock_quantity"] == 25


@pytest.mark.asyncio
async def test_update_product(session):
    """Тест обновления продукта"""
    product_data = {
        "name": "Update Product",
        "price": 1000,
        "description": "Before update",
        "stock_quantity": 10,
    }

    async with AsyncTestClient(app=app) as ac:
        create_response = await ac.post("/products/", json=product_data)
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]

        # Обновляем
        update_data = {
            "name": "Updated Product",
            "price": 1500,
            "description": "After update",
            "stock_quantity": 20,
        }
        response = await ac.put(f"/products/{product_id}", json=update_data)

    print("Update Product Status:", response.status_code)

    assert response.status_code == 200
    product_response = response.json()
    assert product_response["name"] == "Updated Product"
    assert product_response["price"] == 1500
    assert product_response["description"] == "After update"
    assert product_response["stock_quantity"] == 20
