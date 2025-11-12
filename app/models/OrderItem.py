import uuid
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.Base import Base

def uuid4_str():
    return str(uuid.uuid4())

class OrderItem(Base):
    __tablename__ = 'order_items'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid4_str)
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")