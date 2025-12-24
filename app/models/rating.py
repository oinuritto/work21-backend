"""
Модель рейтинга
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Rating(Base):
    """Модель рейтинга/отзыва"""
    
    __tablename__ = "ratings"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Связи
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    
    # Кто оставил отзыв (заказчик) и кому (студент)
    reviewer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    reviewee_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    # Оценка (1-5)
    score: Mapped[int] = mapped_column(Integer)
    
    # Комментарий
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Категории оценки
    quality_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Качество кода
    communication_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Коммуникация
    deadline_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Соблюдение сроков
    
    # Метаданные
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<Rating project={self.project_id} score={self.score}>"


