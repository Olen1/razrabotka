
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from test import Base, User, Address, Product, Order 

engine = create_engine("sqlite:///./test.db", echo=False)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(bind=engine)

#  1. Данные пользователей и адресов ===
users_with_addresses = [
    {
        "username": "Alice Johnson",
        "email": "alice@example.com",
        "description": "Frontend developer",
        "addresses": [
            {"street": "123 Maple St", "city": "New York", "state": "NY", "zip_code": "10001", "country": "USA", "is_primary": True},
            {"street": "456 Oak Ave", "city": "Brooklyn", "state": "NY", "zip_code": "11201", "country": "USA", "is_primary": False},
        ]
    },
    {
        "username": "Bob Smith",
        "email": "bob@example.com",
        "description": "Data scientist",
        "addresses": [
            {"street": "789 Pine Rd", "city": "Los Angeles", "state": "CA", "zip_code": "90210", "country": "USA", "is_primary": True},
        ]
    },
    {
        "username": "Charlie Brown",
        "email": "charlie@example.com",
        "description": "DevOps engineer",
        "addresses": [
            {"street": "101 Birch Ln", "city": "Chicago", "state": "IL", "zip_code": "60601", "country": "USA", "is_primary": True},
            {"street": "202 Cedar Blvd", "city": "Miami", "state": "FL", "zip_code": "33101", "country": "USA", "is_primary": False},
        ]
    },
    {
        "username": "Diana Prince",
        "email": "diana@example.com",
        "description": "UX designer",
        "addresses": [
            {"street": "303 Spruce Dr", "city": "Seattle", "state": "WA", "zip_code": "98101", "country": "USA", "is_primary": True},
        ]
    },
    {
        "username": "Evan Davis",
        "email": "evan@example.com",
        "description": "Backend developer",
        "addresses": [
            {"street": "404 Willow Way", "city": "Denver", "state": "CO", "zip_code": "80201", "country": "USA", "is_primary": True},
            {"street": "505 Elm St", "city": "Portland", "state": "OR", "zip_code": "97201", "country": "USA", "is_primary": False},
        ]
    },
]

#  2. Данные продуктов ===
products_data = [
    {"name": "Laptop", "price": 120000, "description": "High-performance laptop"},
    {"name": "Mouse", "price": 2500, "description": "Wireless ergonomic mouse"},
    {"name": "Keyboard", "price": 8000, "description": "Mechanical keyboard"},
    {"name": "Monitor", "price": 30000, "description": "27-inch 4K monitor"},
    {"name": "Headphones", "price": 15000, "description": "Noise-cancelling headphones"},
]

with SessionLocal() as session:
    # Добавляем пользователей и адреса
    users = []
    addresses = []

    for user_data in users_with_addresses:
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            description=user_data["description"]
        )
        session.add(user)
        session.flush()
        users.append(user)

        for addr in user_data["addresses"]:
            address = Address(
                user_id=user.id,
                street=addr["street"],
                city=addr["city"],
                state=addr.get("state"),
                zip_code=addr.get("zip_code"),
                country=addr["country"],
                is_primary=addr["is_primary"]
            )
            session.add(address)
            session.flush()
            addresses.append(address)

    # Добавляем продукты 
    products = []
    for prod in products_data:
        product = Product(
            name=prod["name"],
            price=prod["price"],
            description=prod["description"]
        )
        session.add(product)
        session.flush()
        products.append(product)

    #  Добавляем заказы (по одному на пользователя, используем первый адрес)
    for i in range(5):
        # Находим первый адрес пользователя
        user_addresses = [a for a in addresses if a.user_id == users[i].id]
        primary_address = next((a for a in user_addresses if a.is_primary), user_addresses[0])

        order = Order(
            user_id=users[i].id,
            address_id=primary_address.id,
            product_id=products[i].id,
            quantity=1
        )
        session.add(order)

    session.commit()
    print("Добавлено: 5 пользователей, их адреса, 5 продуктов и 5 заказов.")