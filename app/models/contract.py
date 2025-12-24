"""
Модель контракта/договора
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import String, Text, Float, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ContractStatus(str, Enum):
    """Статусы договора"""
    DRAFT = "draft"
    PENDING_SIGNATURE = "pending_signature"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


class Contract(Base):
    """Модель договора между заказчиком и исполнителем"""
    
    __tablename__ = "contracts"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Связи
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    # Финансовые условия
    total_amount: Mapped[float] = mapped_column(Float)  # Общая сумма
    platform_fee: Mapped[float] = mapped_column(Float)  # Комиссия платформы
    student_payment: Mapped[float] = mapped_column(Float)  # Выплата студенту
    
    # Условия договора (сгенерированные AI)
    terms: Mapped[str] = mapped_column(Text)
    
    # Статус
    status: Mapped[ContractStatus] = mapped_column(
        SQLEnum(ContractStatus),
        default=ContractStatus.DRAFT
    )
    
    # Даты подписания
    customer_signed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    student_signed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Метаданные
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    def __repr__(self) -> str:
        return f"<Contract project={self.project_id} ({self.status.value})>"


