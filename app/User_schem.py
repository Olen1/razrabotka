from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# --- USER SCHEMAS ---
class UserCreate(BaseModel):
    username: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    email: str
    description: Optional[str] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    username: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    email: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UsersListResponse(BaseModel):
    users: List[UserResponse]
    total_count: int


# --- PRODUCT SCHEMAS ---
class ProductCreate(BaseModel):
    name: str
    price: int  # в копейках/центах
    description: Optional[str] = None
    stock_quantity: int = 0  # <- Новое поле


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[int] = None
    description: Optional[str] = None
    stock_quantity: Optional[int] = None # <- Новое поле


class ProductResponse(BaseModel):
    id: str
    name: str
    price: int
    description: Optional[str] = None
    stock_quantity: int # <- Новое поле

    model_config = {"from_attributes": True}


class ProductsListResponse(BaseModel):
    products: List[ProductResponse]
    total_count: int


# --- ORDER ITEM SCHEMAS ---
class OrderItemCreate(BaseModel):
    product_id: str
    quantity: int = 1


class OrderItemUpdate(BaseModel):
    quantity: Optional[int] = None


class OrderItemResponse(BaseModel):
    id: str
    product_id: str
    quantity: int

    # Опционально: включить ProductResponse
    # product: ProductResponse

    model_config = {"from_attributes": True}


# --- ORDER SCHEMAS ---
class OrderCreate(BaseModel):
    user_id: str
    address_id: str
    items: List[OrderItemCreate] # <- Включаем список OrderItem


class OrderUpdate(BaseModel):
    user_id: Optional[str] = None
    address_id: Optional[str] = None
    # Обычно Order не обновляют items напрямую через update, а добавляют/удаляют отдельно


class OrderResponse(BaseModel):
    id: str
    user_id: str
    address_id: str
    created_at: datetime
    items: List[OrderItemResponse] # <- Включаем список OrderItemResponse

    model_config = {"from_attributes": True}


class OrdersListResponse(BaseModel):
    orders: List[OrderResponse]
    total_count: int