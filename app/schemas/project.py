"""
Pydantic схемы для проектов, задач и заявок
"""
import json
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, model_validator

from app.models.project import ProjectStatus, TaskStatus, ApplicationStatus


class TaskCreate(BaseModel):
    """Схема для создания задачи"""
    title: str = Field(..., min_length=1, max_length=255)
    description: str
    complexity: int = Field(default=1, ge=1, le=5)
    estimated_hours: Optional[int] = None
    deadline: Optional[datetime] = None
    order: int = 0


class TaskAssigneeInfo(BaseModel):
    """Информация об исполнителе задачи"""
    id: int
    first_name: str
    last_name: str
    email: str
    avatar_url: Optional[str] = None
    rating_score: float
    
    class Config:
        from_attributes = True


class TaskResponse(TaskCreate):
    """Схема ответа с данными задачи"""
    id: int
    status: TaskStatus
    project_id: int
    assignee_id: Optional[int] = None
    assignee: Optional[TaskAssigneeInfo] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    """Базовая схема проекта"""
    title: str = Field(..., min_length=1, max_length=255)
    description: str
    requirements: Optional[str] = None
    budget: float = Field(..., gt=0)
    deadline: Optional[datetime] = None
    tech_stack: Optional[List[str]] = None
    llm_estimation: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Схема для создания проекта"""
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Мобильное приложение для доставки",
                "description": "Разработка кроссплатформенного приложения на React Native",
                "requirements": "iOS и Android, интеграция с Firebase, push-уведомления",
                "budget": 150000,
                "deadline": "2025-02-01T00:00:00",
                "tech_stack": ["React Native", "Firebase", "TypeScript"]
            }
        }


class ProjectUpdate(BaseModel):
    """Схема для обновления проекта"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    requirements: Optional[str] = None
    budget: Optional[float] = Field(None, gt=0)
    deadline: Optional[datetime] = None
    tech_stack: Optional[List[str]] = None
    llm_estimation: Optional[str] = None
    status: Optional[ProjectStatus] = None


class ProjectAssigneeInfo(BaseModel):
    """Информация об исполнителе проекта"""
    id: int
    first_name: str
    last_name: str
    email: str
    avatar_url: Optional[str] = None
    rating_score: float
    
    class Config:
        from_attributes = True


class ProjectResponse(ProjectBase):
    """Схема ответа с данными проекта"""
    id: int
    status: ProjectStatus
    customer_id: int
    assignee_id: Optional[int] = None
    assignee: Optional[ProjectAssigneeInfo] = None
    generated_spec: Optional[str] = None
    llm_estimation: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    tasks: List[TaskResponse] = []
    
    @model_validator(mode='before')
    @classmethod
    def parse_tech_stack(cls, data):
        """Преобразует tech_stack из JSON строки в список"""
        if isinstance(data, dict):
            tech_stack = data.get('tech_stack')
            if isinstance(tech_stack, str) and tech_stack:
                try:
                    data['tech_stack'] = json.loads(tech_stack)
                except (json.JSONDecodeError, TypeError):
                    data['tech_stack'] = None
        elif hasattr(data, '__dict__'):
            # Если это объект модели SQLAlchemy или другой объект
            tech_stack = getattr(data, 'tech_stack', None)
            if isinstance(tech_stack, str) and tech_stack:
                try:
                    # Временно изменяем атрибут для сериализации
                    object.__setattr__(data, 'tech_stack', json.loads(tech_stack))
                except (json.JSONDecodeError, TypeError):
                    object.__setattr__(data, 'tech_stack', None)
        return data
    
    class Config:
        from_attributes = True


class ApplicationCreate(BaseModel):
    """Схема для создания заявки"""
    project_id: int
    cover_letter: Optional[str] = None
    proposed_rate: Optional[float] = Field(None, gt=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_id": 1,
                "cover_letter": "Имею опыт работы с React Native более 2 лет...",
                "proposed_rate": 140000
            }
        }


class ApplicationResponse(BaseModel):
    """Схема ответа с данными заявки"""
    id: int
    project_id: int
    student_id: int
    cover_letter: Optional[str] = None
    proposed_rate: Optional[float] = None
    status: ApplicationStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


class ApplicationStatusUpdate(BaseModel):
    """Схема для обновления статуса заявки"""
    status: ApplicationStatus


