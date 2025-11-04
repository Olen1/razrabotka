from pydantic import BaseModel
from typing import Optional
from datetime import datetime  # ← добавлен импорт datetime


class UserCreate(BaseModel):
    username: str
    email: str
    description: Optional[str] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None


class UserRead(BaseModel):
    id: str
    username: str
    email: str
    description: Optional[str] = None
    created_at: datetime  # ← изменено с str на datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    description: Optional[str] = None
    created_at: datetime  # ← изменено с str на datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}