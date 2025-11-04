# app/models/user.py
from typing import List
from datetime import datetime
import uuid
from sqlalchemy import String, Text, Integer
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

    orders = relationship("Order", back_populates="product")