"""
API endpoints для админ-панели
"""
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, update, delete
from pydantic import BaseModel, EmailStr, Field

from app.core.database import get_db
from app.core.security import get_password_hash
from app.api.deps import get_current_admin_user
from app.models.user import User, UserRole
from app.models.project import Project, ProjectStatus, Application, ApplicationStatus, Task
from app.models.rating import Rating
from app.models.contract import Contract, ContractStatus

router = APIRouter()


# ============= Схемы =============

class StatsResponse(BaseModel):
    """Статистика платформы"""
    total_users: int
    total_students: int
    total_customers: int
    total_admins: int
    total_projects: int
    open_projects: int
    in_progress_projects: int
    completed_projects: int
    total_applications: int
    pending_applications: int
    total_contracts: int
    active_contracts: int


class PaginatedResponse(BaseModel):
    """Пагинированный ответ"""
    items: List
    total: int
    page: int
    per_page: int
    pages: int


class UserAdminResponse(BaseModel):
    """Ответ с данными пользователя для админки"""
    id: int
    email: str
    first_name: str
    last_name: str
    role: str
    bio: Optional[str] = None
    skills: Optional[str] = None
    avatar_url: Optional[str] = None
    rating_score: float
    completed_projects: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserAdminUpdate(BaseModel):
    """Схема обновления пользователя админом"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[UserRole] = None
    bio: Optional[str] = None
    skills: Optional[str] = None
    rating_score: Optional[float] = Field(None, ge=0, le=5)
    completed_projects: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class PasswordResetRequest(BaseModel):
    """Запрос на сброс пароля"""
    new_password: str = Field(..., min_length=8)


class UserAdminCreate(BaseModel):
    """Схема создания пользователя админом"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role: UserRole
    bio: Optional[str] = None
    skills: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False


class ProjectAdminCreate(BaseModel):
    """Схема создания проекта админом"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    requirements: Optional[str] = None
    budget: float = Field(..., ge=0)
    deadline: Optional[datetime] = None
    tech_stack: Optional[str] = None
    status: ProjectStatus = ProjectStatus.DRAFT
    customer_id: int
    assignee_id: Optional[int] = None


class ProjectAdminResponse(BaseModel):
    """Ответ с данными проекта для админки"""
    id: int
    title: str
    description: str
    requirements: Optional[str] = None
    budget: float
    deadline: Optional[datetime] = None
    tech_stack: Optional[str] = None
    status: str
    customer_id: int
    assignee_id: Optional[int] = None
    generated_spec: Optional[str] = None
    llm_estimation: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectAdminUpdate(BaseModel):
    """Схема обновления проекта админом"""
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    budget: Optional[float] = None
    deadline: Optional[datetime] = None
    tech_stack: Optional[str] = None
    status: Optional[ProjectStatus] = None
    customer_id: Optional[int] = None
    assignee_id: Optional[int] = None
    generated_spec: Optional[str] = None
    llm_estimation: Optional[str] = None


class ApplicationAdminResponse(BaseModel):
    """Ответ с данными заявки"""
    id: int
    project_id: int
    student_id: int
    cover_letter: Optional[str] = None
    proposed_rate: Optional[float] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ApplicationAdminUpdate(BaseModel):
    """Обновление заявки"""
    status: Optional[ApplicationStatus] = None


class ContractAdminResponse(BaseModel):
    """Ответ с данными договора"""
    id: int
    project_id: int
    customer_id: int
    student_id: int
    total_amount: float
    status: str
    signed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RatingAdminResponse(BaseModel):
    """Ответ с данными рейтинга"""
    id: int
    project_id: int
    reviewer_id: int
    reviewee_id: int
    score: int
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============= Статистика =============

@router.get("/stats", response_model=StatsResponse)
async def get_admin_stats(
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Получить общую статистику платформы"""
    
    # Пользователи
    total_users = await db.scalar(select(func.count(User.id))) or 0
    total_students = await db.scalar(
        select(func.count(User.id)).where(User.role == UserRole.STUDENT)
    ) or 0
    total_customers = await db.scalar(
        select(func.count(User.id)).where(User.role == UserRole.CUSTOMER)
    ) or 0
    total_admins = await db.scalar(
        select(func.count(User.id)).where(User.role == UserRole.ADMIN)
    ) or 0
    
    # Проекты
    total_projects = await db.scalar(select(func.count(Project.id))) or 0
    open_projects = await db.scalar(
        select(func.count(Project.id)).where(Project.status == ProjectStatus.OPEN)
    ) or 0
    in_progress_projects = await db.scalar(
        select(func.count(Project.id)).where(Project.status == ProjectStatus.IN_PROGRESS)
    ) or 0
    completed_projects = await db.scalar(
        select(func.count(Project.id)).where(Project.status == ProjectStatus.COMPLETED)
    ) or 0
    
    # Заявки
    total_applications = await db.scalar(select(func.count(Application.id))) or 0
    pending_applications = await db.scalar(
        select(func.count(Application.id)).where(Application.status == ApplicationStatus.PENDING)
    ) or 0
    
    # Контракты
    total_contracts = await db.scalar(select(func.count(Contract.id))) or 0
    active_contracts = await db.scalar(
        select(func.count(Contract.id)).where(Contract.status == ContractStatus.ACTIVE)
    ) or 0
    
    return StatsResponse(
        total_users=total_users,
        total_students=total_students,
        total_customers=total_customers,
        total_admins=total_admins,
        total_projects=total_projects,
        open_projects=open_projects,
        in_progress_projects=in_progress_projects,
        completed_projects=completed_projects,
        total_applications=total_applications,
        pending_applications=pending_applications,
        total_contracts=total_contracts,
        active_contracts=active_contracts,
    )


# ============= Пользователи =============

@router.get("/users")
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Получить список пользователей с фильтрацией и пагинацией"""
    
    query = select(User)
    count_query = select(func.count(User.id))
    
    # Фильтры
    if search:
        search_filter = or_(
            User.email.ilike(f"%{search}%"),
            User.first_name.ilike(f"%{search}%"),
            User.last_name.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
    
    if role:
        query = query.where(User.role == role)
        count_query = count_query.where(User.role == role)
    
    if is_active is not None:
        query = query.where(User.is_active == is_active)
        count_query = count_query.where(User.is_active == is_active)
    
    # Подсчёт
    total = await db.scalar(count_query) or 0
    
    # Сортировка
    sort_column = getattr(User, sort_by, User.created_at)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # Пагинация
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    return {
        "items": [
            UserAdminResponse(
                id=u.id,
                email=u.email,
                first_name=u.first_name,
                last_name=u.last_name,
                role=u.role.value,
                bio=u.bio,
                skills=u.skills,
                avatar_url=u.avatar_url,
                rating_score=u.rating_score,
                completed_projects=u.completed_projects,
                is_active=u.is_active,
                is_verified=u.is_verified,
                created_at=u.created_at,
                updated_at=u.updated_at,
            ) for u in users
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page if per_page > 0 else 0,
    }


@router.post("/users")
async def create_user(
    data: UserAdminCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Создать нового пользователя"""
    
    # Проверяем что email не занят
    result = await db.execute(select(User).where(User.email == data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=400, 
            detail=f"Пользователь с email {data.email} уже существует"
        )
    
    # Создаём пользователя
    user = User(
        email=data.email,
        hashed_password=get_password_hash(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        role=data.role,
        bio=data.bio,
        skills=data.skills,
        is_active=data.is_active,
        is_verified=data.is_verified,
        rating_score=0.0,
        completed_projects=0,
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return {"message": "Пользователь создан", "id": user.id}


@router.get("/users/{user_id}", response_model=UserAdminResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Получить детали пользователя"""
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    return UserAdminResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role.value,
        bio=user.bio,
        skills=user.skills,
        avatar_url=user.avatar_url,
        rating_score=user.rating_score,
        completed_projects=user.completed_projects,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.patch("/users/{user_id}")
async def update_user(
    user_id: int,
    data: UserAdminUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Обновить данные пользователя"""
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Обновляем только переданные поля
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    
    return {"message": "Пользователь обновлён", "user_id": user.id}


@router.post("/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Сбросить пароль пользователя"""
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Хешируем новый пароль
    user.hashed_password = get_password_hash(data.new_password)
    
    await db.commit()
    
    return {"message": f"Пароль пользователя {user.email} успешно изменён"}


@router.post("/users/{user_id}/block")
async def block_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Заблокировать пользователя"""
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    if user.id == current_admin.id:
        raise HTTPException(status_code=400, detail="Нельзя заблокировать самого себя")
    
    user.is_active = False
    await db.commit()
    
    return {"message": f"Пользователь {user.email} заблокирован"}


@router.post("/users/{user_id}/unblock")
async def unblock_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Разблокировать пользователя"""
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    user.is_active = True
    await db.commit()
    
    return {"message": f"Пользователь {user.email} разблокирован"}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Удалить пользователя (мягкое удаление)"""
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    if user.id == current_admin.id:
        raise HTTPException(status_code=400, detail="Нельзя удалить самого себя")
    
    # Мягкое удаление
    user.is_active = False
    user.email = f"deleted_{user.id}_{user.email}"
    
    await db.commit()
    
    return {"message": "Пользователь удалён"}


# ============= Проекты =============

@router.get("/projects")
async def list_projects(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[ProjectStatus] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Получить список проектов"""
    
    query = select(Project)
    count_query = select(func.count(Project.id))
    
    if search:
        search_filter = or_(
            Project.title.ilike(f"%{search}%"),
            Project.description.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
    
    if status:
        query = query.where(Project.status == status)
        count_query = count_query.where(Project.status == status)
    
    total = await db.scalar(count_query) or 0
    
    sort_column = getattr(Project, sort_by, Project.created_at)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    
    result = await db.execute(query)
    projects = result.scalars().all()
    
    return {
        "items": [
            ProjectAdminResponse(
                id=p.id,
                title=p.title,
                description=p.description,
                requirements=p.requirements,
                budget=p.budget,
                deadline=p.deadline,
                tech_stack=p.tech_stack,
                status=p.status.value,
                customer_id=p.customer_id,
                assignee_id=p.assignee_id,
                generated_spec=p.generated_spec,
                llm_estimation=p.llm_estimation,
                created_at=p.created_at,
                updated_at=p.updated_at,
            ) for p in projects
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page if per_page > 0 else 0,
    }


@router.post("/projects")
async def create_project(
    data: ProjectAdminCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Создать новый проект"""
    
    # Проверяем что заказчик существует
    result = await db.execute(select(User).where(User.id == data.customer_id))
    customer = result.scalar_one_or_none()
    
    if not customer:
        raise HTTPException(status_code=400, detail="Заказчик не найден")
    
    # Проверяем исполнителя если указан
    if data.assignee_id:
        result = await db.execute(select(User).where(User.id == data.assignee_id))
        assignee = result.scalar_one_or_none()
        if not assignee:
            raise HTTPException(status_code=400, detail="Исполнитель не найден")
    
    # Создаём проект
    project = Project(
        title=data.title,
        description=data.description,
        requirements=data.requirements,
        budget=data.budget,
        deadline=data.deadline,
        tech_stack=data.tech_stack,
        status=data.status,
        customer_id=data.customer_id,
        assignee_id=data.assignee_id,
    )
    
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    return {"message": "Проект создан", "id": project.id}


@router.get("/projects/{project_id}", response_model=ProjectAdminResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Получить детали проекта"""
    
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    return ProjectAdminResponse(
        id=project.id,
        title=project.title,
        description=project.description,
        requirements=project.requirements,
        budget=project.budget,
        deadline=project.deadline,
        tech_stack=project.tech_stack,
        status=project.status.value,
        customer_id=project.customer_id,
        assignee_id=project.assignee_id,
        generated_spec=project.generated_spec,
        llm_estimation=project.llm_estimation,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.patch("/projects/{project_id}")
async def update_project(
    project_id: int,
    data: ProjectAdminUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Обновить проект"""
    
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    await db.commit()
    await db.refresh(project)
    
    return {"message": "Проект обновлён", "project_id": project.id}


@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Удалить проект"""
    
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    # Устанавливаем статус отменён вместо удаления
    project.status = ProjectStatus.CANCELLED
    await db.commit()
    
    return {"message": "Проект удалён (отменён)"}


# ============= Заявки =============

@router.get("/applications")
async def list_applications(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[ApplicationStatus] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Получить список заявок"""
    
    query = select(Application)
    count_query = select(func.count(Application.id))
    
    if status:
        query = query.where(Application.status == status)
        count_query = count_query.where(Application.status == status)
    
    total = await db.scalar(count_query) or 0
    
    sort_column = getattr(Application, sort_by, Application.created_at)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    
    result = await db.execute(query)
    applications = result.scalars().all()
    
    return {
        "items": [
            ApplicationAdminResponse(
                id=a.id,
                project_id=a.project_id,
                student_id=a.student_id,
                cover_letter=a.cover_letter,
                proposed_rate=a.proposed_rate,
                status=a.status.value,
                created_at=a.created_at,
            ) for a in applications
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page if per_page > 0 else 0,
    }


@router.patch("/applications/{application_id}")
async def update_application(
    application_id: int,
    data: ApplicationAdminUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Обновить заявку"""
    
    result = await db.execute(select(Application).where(Application.id == application_id))
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(application, field, value)
    
    await db.commit()
    
    return {"message": "Заявка обновлена", "application_id": application.id}


# ============= Договоры =============

@router.get("/contracts")
async def list_contracts(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[ContractStatus] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Получить список договоров"""
    
    query = select(Contract)
    count_query = select(func.count(Contract.id))
    
    if status:
        query = query.where(Contract.status == status)
        count_query = count_query.where(Contract.status == status)
    
    total = await db.scalar(count_query) or 0
    
    sort_column = getattr(Contract, sort_by, Contract.created_at)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    
    result = await db.execute(query)
    contracts = result.scalars().all()
    
    return {
        "items": [
            ContractAdminResponse(
                id=c.id,
                project_id=c.project_id,
                customer_id=c.customer_id,
                student_id=c.student_id,
                total_amount=c.total_amount,
                status=c.status.value,
                signed_at=c.signed_at,
                completed_at=c.completed_at,
                created_at=c.created_at,
            ) for c in contracts
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page if per_page > 0 else 0,
    }


# ============= Рейтинги =============

@router.get("/ratings")
async def list_ratings(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Получить список рейтингов"""
    
    query = select(Rating)
    count_query = select(func.count(Rating.id))
    
    total = await db.scalar(count_query) or 0
    
    sort_column = getattr(Rating, sort_by, Rating.created_at)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    
    result = await db.execute(query)
    ratings = result.scalars().all()
    
    return {
        "items": [
            RatingAdminResponse(
                id=r.id,
                project_id=r.project_id,
                reviewer_id=r.reviewer_id,
                reviewee_id=r.reviewee_id,
                score=r.score,
                comment=r.comment,
                created_at=r.created_at,
            ) for r in ratings
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page if per_page > 0 else 0,
    }


@router.delete("/ratings/{rating_id}")
async def delete_rating(
    rating_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Удалить рейтинг"""
    
    result = await db.execute(select(Rating).where(Rating.id == rating_id))
    rating = result.scalar_one_or_none()
    
    if not rating:
        raise HTTPException(status_code=404, detail="Рейтинг не найден")
    
    await db.delete(rating)
    await db.commit()
    
    return {"message": "Рейтинг удалён"}

