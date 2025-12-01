import json

import pika


def send_products():
    """Отправляет 5 продуктов в очередь 'product'."""
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost", port=5672, virtual_host="local")
    )
    channel = connection.channel()

    # Объявляем очередь (если ещё не объявлена)
    channel.queue_declare(queue="product", durable=True)

    products = [
        {
            "id": "prod-001",
            "name": "Laptop",
            "price": 50000,
            "description": "High-end laptop",
            "stock_quantity": 100,
            "action": "create",
        },
        {
            "id": "prod-002",
            "name": "Mouse",
            "price": 1500,
            "description": "Wireless mouse",
            "stock_quantity": 200,
            "action": "create",
        },
        {
            "id": "prod-003",
            "name": "Keyboard",
            "price": 3000,
            "description": "Mechanical keyboard",
            "stock_quantity": 150,
            "action": "create",
        },
        {
            "id": "prod-004",
            "name": "Monitor",
            "price": 25000,
            "description": "4K Monitor",
            "stock_quantity": 50,
            "action": "create",
        },
        {
            "id": "prod-005",
            "name": "Headphones",
            "price": 8000,
            "description": "Noise-cancelling headphones",
            "stock_quantity": 80,
            "action": "create",
        },
    ]

    for product in products:
        channel.basic_publish(
            exchange="",
            routing_key="product",
            body=json.dumps(product),
            properties=pika.BasicProperties(
                delivery_mode=2, content_type="application/json"  # persistent
            ),
        )
        print(f"✓ Sent product: {product['name']} ({product['id']})")

    connection.close()


def send_orders():
    """Отправляет 3 заказа в очередь 'order'."""
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost", port=5672, virtual_host="local")
    )
    channel = connection.channel()

    # --- ИСПРАВЛЕНО: Объявляем очередь 'order' ---
    # Проверяем, существует ли очередь 'order'
    try:
        channel.queue_declare(queue="order", durable=True, passive=True)
        print("Queue 'order' already exists.")
    except pika.exceptions.ChannelClosedByBroker as e:
        if e.reply_code == 404:
            # Очередь не существует, создаём
            print("Queue 'order' does not exist, creating...")
            channel.queue_declare(queue="order", durable=True)
        else:
            # Другая ошибка
            raise

    # --- END OF FIX ---

    orders = [
        {
            "user_id": "user-001",
            "address_id": "addr-001",
            "items": [
                {"product_id": "prod-001", "quantity": 1},  # Laptop
                {"product_id": "prod-002", "quantity": 2},  # 2x Mouse
            ],
        },
        {
            "user_id": "user-002",
            "address_id": "addr-002",
            "items": [
                {"product_id": "prod-003", "quantity": 1},  # Keyboard
                {"product_id": "prod-004", "quantity": 1},  # Monitor
            ],
        },
        {
            "user_id": "user-003",
            "address_id": "addr-003",
            "items": [
                {"product_id": "prod-005", "quantity": 1},  # Headphones
                {"product_id": "prod-002", "quantity": 1},  # 1x Mouse
            ],
        },
    ]

    for order in orders:
        channel.basic_publish(
            exchange="",
            routing_key="order",
            body=json.dumps(order),
            properties=pika.BasicProperties(
                delivery_mode=2, content_type="application/json"  # persistent
            ),
        )
        print(f"✓ Sent order for user: {order['user_id']}")

    connection.close()


if __name__ == "__main__":
    print("Sending products...")
    send_products()

    print("\nSending orders...")
    send_orders()

    print("\nAll messages sent successfully!")
