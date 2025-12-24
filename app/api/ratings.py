"""
API endpoints для рейтингов
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User, UserRole
from app.models.project import Project, ProjectStatus
from app.models.rating import Rating


router = APIRouter()


class RatingCreate(BaseModel):
    """Схема для создания рейтинга"""
    project_id: int
    reviewee_id: int  # ID студента, которому ставим оценку
    score: int = Field(..., ge=1, le=5)
    comment: str | None = None
    quality_score: int | None = Field(None, ge=1, le=5)
    communication_score: int | None = Field(None, ge=1, le=5)
    deadline_score: int | None = Field(None, ge=1, le=5)


class RatingResponse(BaseModel):
    """Схема ответа с данными рейтинга"""
    id: int
    project_id: int
    reviewer_id: int
    reviewee_id: int
    score: int
    comment: str | None
    quality_score: int | None
    communication_score: int | None
    deadline_score: int | None
    
    class Config:
        from_attributes = True


@router.post("/", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
async def create_rating(
    rating_data: RatingCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Создать рейтинг/отзыв (заказчик -> студент или студент -> заказчик после завершения проекта)
    """
    result = await db.execute(
        select(Project).where(Project.id == rating_data.project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )
    
    if project.status != ProjectStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Можно оставить отзыв только после завершения проекта"
        )
    
    if current_user.role == UserRole.CUSTOMER:
        if project.customer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы не являетесь заказчиком этого проекта"
            )
        if not project.assignee_id or project.assignee_id != rating_data.reviewee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный исполнитель"
            )
    elif current_user.role == UserRole.STUDENT:
        if project.assignee_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы не являетесь исполнителем этого проекта"
            )
        if project.customer_id != rating_data.reviewee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный заказчик"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только заказчики и студенты могут оставлять отзывы"
        )
    
    existing = await db.execute(
        select(Rating)
        .where(Rating.project_id == rating_data.project_id)
        .where(Rating.reviewer_id == current_user.id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы уже оставили отзыв на этот проект"
        )
    
    rating = Rating(
        project_id=rating_data.project_id,
        reviewer_id=current_user.id,
        reviewee_id=rating_data.reviewee_id,
        score=rating_data.score,
        comment=rating_data.comment,
        quality_score=rating_data.quality_score,
        communication_score=rating_data.communication_score,
        deadline_score=rating_data.deadline_score,
    )
    
    db.add(rating)
    
    reviewee_result = await db.execute(
        select(User).where(User.id == rating_data.reviewee_id)
    )
    reviewee = reviewee_result.scalar_one_or_none()
    
    if reviewee:
        avg_result = await db.execute(
            select(func.avg(Rating.score))
            .where(Rating.reviewee_id == reviewee.id)
        )
        avg_score = avg_result.scalar() or 0
        reviewee.rating_score = float(avg_score)
        if current_user.role == UserRole.CUSTOMER:
            reviewee.completed_projects += 1
    
    await db.commit()
    await db.refresh(rating)
    
    return rating


@router.get("/user/{user_id}", response_model=List[RatingResponse])
async def get_user_ratings(
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить отзывы о пользователе
    """
    result = await db.execute(
        select(Rating)
        .where(Rating.reviewee_id == user_id)
        .order_by(Rating.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    
    return result.scalars().all()


