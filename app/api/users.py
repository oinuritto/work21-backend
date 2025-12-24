"""
API endpoints для пользователей
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User, UserRole
from app.schemas.user import UserResponse, UserUpdate


router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Получить профиль текущего пользователя
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Обновить профиль текущего пользователя
    """
    update_data = user_data.model_dump(exclude_unset=True)
    
    # Преобразуем skills в JSON строку если передано
    if "skills" in update_data and update_data["skills"]:
        import json
        update_data["skills"] = json.dumps(update_data["skills"])
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_profile(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить публичный профиль пользователя
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    return user


@router.get("/", response_model=List[UserResponse])
async def list_students(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список студентов (для заказчиков)
    """
    result = await db.execute(
        select(User)
        .where(User.role == UserRole.STUDENT)
        .where(User.is_active == True)
        .order_by(User.rating_score.desc())
        .offset(skip)
        .limit(limit)
    )
    
    return result.scalars().all()


@router.get("/leaderboard", response_model=List[UserResponse])
async def get_leaderboard(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить топ студентов по рейтингу
    """
    result = await db.execute(
        select(User)
        .where(User.role == UserRole.STUDENT)
        .where(User.is_active == True)
        .order_by(User.rating_score.desc())
        .limit(limit)
    )
    
    return result.scalars().all()


