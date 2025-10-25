import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, ForeignKey, Integer, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

def uuid4_str():
    return str(uuid.uuid4())

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid4_str)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=datetime.utcnow, nullable=True)

    addresses = relationship("Address", back_populates="user")
    orders = relationship("Order", back_populates="user")
    
class Address(Base):
    __tablename__ = 'addresses'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid4_str)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    street: Mapped[str] = mapped_column(String, nullable=False)
    city: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=True)        # ← добавлено
    zip_code: Mapped[str] = mapped_column(String, nullable=True)     # ← добавлено
    country: Mapped[str] = mapped_column(String, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=datetime.utcnow, nullable=True)

    user = relationship("User", back_populates="addresses")
    orders = relationship("Order", back_populates="delivery_address")

class Product(Base):
    __tablename__ = 'products'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid4_str)
    name: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)  # в копейках/центах
    description: Mapped[str] = mapped_column(Text, nullable=True)

    orders = relationship("Order", back_populates="product")

class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid4_str)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    address_id: Mapped[str] = mapped_column(ForeignKey("addresses.id"), nullable=False)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="orders")
    delivery_address = relationship("Address", back_populates="orders")
    product = relationship("Product", back_populates="orders")