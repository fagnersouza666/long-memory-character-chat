from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: str
    role: str = "employee"
    department: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool = True
    createdAt: datetime
    updatedAt: datetime
    lastLogin: Optional[datetime] = None

    class Config:
        orm_mode = True

class UserInDB(User):
    passwordHash: str