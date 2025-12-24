"""
Модель пользователя
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List

from sqlalchemy import String, Text, Float, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserRole(str, Enum):
    """Роли пользователей"""
    STUDENT = "student"
    CUSTOMER = "customer"
    ADMIN = "admin"


class User(Base):
    """Модель пользователя платформы"""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    
    # Профиль
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.STUDENT)
    
    # Дополнительные данные профиля
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    skills: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON строка
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Рейтинг (для студентов)
    rating_score: Mapped[float] = mapped_column(Float, default=0.0)
    completed_projects: Mapped[int] = mapped_column(default=0)
    
    # Метаданные
    is_active: Mapped[bool] = mapped_column(default=True)
    is_verified: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    
    # Relationships
    projects: Mapped[List["Project"]] = relationship(
        "Project", 
        back_populates="customer",
        foreign_keys="Project.customer_id"
    )
    applications: Mapped[List["Application"]] = relationship(
        "Application",
        back_populates="student"
    )
    
    @property
    def full_name(self) -> str:
        """Полное имя пользователя"""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role.value})>"


