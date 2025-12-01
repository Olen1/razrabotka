# app/schemas.py
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class ProductStatus(str, Enum):
    AVAILABLE = "available"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"


# Product Schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    stock_quantity: int
    status: ProductStatus = ProductStatus.AVAILABLE


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock_quantity: Optional[int] = None
    status: Optional[ProductStatus] = None


class ProductResponse(ProductBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Order Item Schemas
class OrderItemBase(BaseModel):
    product_id: str
    quantity: int


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase):
    id: str
    price: Decimal
    total: Decimal

    class Config:
        from_attributes = True


# Order Schemas
class OrderBase(BaseModel):
    user_id: str
    address_id: str
    status: OrderStatus = OrderStatus.PENDING


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    address_id: Optional[str] = None


class OrderResponse(OrderBase):
    id: str
    total_amount: Decimal
    items: List[OrderItemResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Message schemas for queues (используем ваши модели)
class OrderItemMessage(BaseModel):
    product_id: str
    quantity: int


class OrderMessage(BaseModel):
    user_id: str
    address_id: str
    items: List[OrderItemMessage]


class ProductMessage(BaseModel):
    id: str
    name: str
    price: int
    description: Optional[str] = None
    stock_quantity: int


# Extended message schemas with actions
class ExtendedOrderMessage(OrderMessage):
    action: str = "create"  # create, update_status
    order_id: Optional[str] = None
    status: Optional[OrderStatus] = None


class ExtendedProductMessage(ProductMessage):
    action: str = "create"  # create, update, delete, stock_update, mark_out_of_stock
