"""
Модели проекта, задач и заявок
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List

from sqlalchemy import String, Text, Float, Integer, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProjectStatus(str, Enum):
    """Статусы проекта"""
    DRAFT = "draft"
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskStatus(str, Enum):
    """Статусы задачи"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"


class ApplicationStatus(str, Enum):
    """Статусы заявки"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class Project(Base):
    """Модель проекта"""
    
    __tablename__ = "projects"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Основная информация
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON или Markdown
    
    # Бюджет и сроки
    budget: Mapped[float] = mapped_column(Float)
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Технический стек (JSON строка)
    tech_stack: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Статус
    status: Mapped[ProjectStatus] = mapped_column(
        SQLEnum(ProjectStatus), 
        default=ProjectStatus.DRAFT
    )
    
    # Связи
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    customer: Mapped["User"] = relationship("User", back_populates="projects", foreign_keys=[customer_id])
    
    # Исполнитель проекта (студент)
    assignee_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    assignee: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assignee_id])
    
    # Сгенерированное ТЗ от AI
    generated_spec: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Оценка времени выполнения от LLM
    llm_estimation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Метаданные
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="project")
    applications: Mapped[List["Application"]] = relationship("Application", back_populates="project")
    
    def __repr__(self) -> str:
        return f"<Project {self.title} ({self.status.value})>"


class Task(Base):
    """Модель задачи (подзадачи проекта)"""
    
    __tablename__ = "tasks"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Основная информация
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    
    # Сложность и сроки
    complexity: Mapped[int] = mapped_column(Integer, default=1)  # 1-5
    estimated_hours: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Статус
    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus),
        default=TaskStatus.PENDING
    )
    
    # Порядок выполнения
    order: Mapped[int] = mapped_column(Integer, default=0)
    
    # Связи
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship("Project", back_populates="tasks")
    
    assignee_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    assignee: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assignee_id])
    
    # Метаданные
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<Task {self.title} ({self.status.value})>"


class Application(Base):
    """Модель заявки студента на проект"""
    
    __tablename__ = "applications"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Связи
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship("Project", back_populates="applications")
    
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    student: Mapped["User"] = relationship("User", back_populates="applications")
    
    # Сопроводительное письмо
    cover_letter: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Предложенная ставка (если отличается от бюджета)
    proposed_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Статус
    status: Mapped[ApplicationStatus] = mapped_column(
        SQLEnum(ApplicationStatus),
        default=ApplicationStatus.PENDING
    )
    
    # Метаданные
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<Application student={self.student_id} project={self.project_id}>"


