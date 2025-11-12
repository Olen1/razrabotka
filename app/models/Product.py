import uuid
from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.Base import Base

def uuid4_str():
    return str(uuid.uuid4())

class Product(Base):
    __tablename__ = 'products'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid4_str)
    name: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)  # в копейках/центах
    description: Mapped[str] = mapped_column(Text, nullable=True)
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Связь с OrderItem (НЕ напрямую с Order)
    order_items = relationship("OrderItem", back_populates="product")
    # (опционально) получить заказы через OrderItem
    # orders = association_proxy("order_items", "order") # требует sqlalchemy.ext.associationproxy