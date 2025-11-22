from models import Address, Order, Product, User
from sqlalchemy import create_engine, select
from sqlalchemy.orm import selectinload, sessionmaker

engine = create_engine("sqlite:///./test.db", echo=False)
SessionLocal = sessionmaker(bind=engine)

with SessionLocal() as session:
    print("=" * 60)
    print("СПИСОК ПОЛЬЗОВАТЕЛЕЙ И ИХ АДРЕСОВ")
    print("=" * 60)

    # Загружаем пользователей + адреса
    users = session.scalars(select(User).options(selectinload(User.addresses))).all()

    for user in users:
        print(f"\n {user.username} ({user.email})")
        print(f"   Описание: {user.description or '—'}")
        for addr in user.addresses:
            primary = " " if addr.is_primary else ""
            print(f"   {addr.street}, {addr.city}, {addr.country}{primary}")

    print("\n" + "=" * 60)
    print("СПИСОК ЗАКАЗОВ")
    print("=" * 60)

    # Загружаем заказы + связанные данные (пользователь, адрес, продукт)
    orders = session.scalars(
        select(Order)
        .options(
            selectinload(Order.user),
            selectinload(Order.delivery_address),
            selectinload(Order.product),
        )
        .order_by(Order.created_at)
    ).all()

    for order in orders:
        print(f"\n Заказ ID: {order.id[:8]}")
        print(f"   Пользователь: {order.user.username}")
        addr = order.delivery_address
        print(f"   Адрес доставки: {addr.street}, {addr.city}, {addr.country}")
        prod = order.product
        price_rub = prod.price / 100
        print(f"   Товар: {prod.name} — {order.quantity} шт. (${price_rub:.2f})")
        print(f"   Дата: {order.created_at.strftime('%Y-%m-%d %H:%M')}")

    print("\n" + "=" * 60)
    print("СПИСОК ПРОДУКТОВ")
    print("=" * 60)

    products = session.scalars(select(Product)).all()
    for prod in products:
        print(f"\n🛒 {prod.name}")
        print(f"   Цена: ${prod.price / 100:.2f}")
        print(f"   Описание: {prod.description or '—'}")
