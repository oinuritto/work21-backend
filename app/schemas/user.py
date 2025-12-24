"""
Pydantic схемы для пользователей
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    """Базовая схема пользователя"""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role: UserRole = UserRole.STUDENT


class UserCreate(UserBase):
    """Схема для создания пользователя"""
    password: str = Field(..., min_length=8)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "student@school21.ru",
                "first_name": "Иван",
                "last_name": "Петров",
                "role": "student",
                "password": "securepassword123"
            }
        }


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    bio: Optional[str] = None
    skills: Optional[List[str]] = None
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    """Схема ответа с данными пользователя"""
    id: int
    bio: Optional[str] = None
    skills: Optional[str] = None
    avatar_url: Optional[str] = None
    rating_score: float
    completed_projects: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Схема для входа"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Схема JWT токена"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Данные из токена"""
    user_id: Optional[int] = None
    email: Optional[str] = None


