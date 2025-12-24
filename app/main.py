"""
WORK21 Backend - FastAPI Application
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api import api_router
from app.admin import create_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle events: startup and shutdown
    """
    # Startup
    await init_db()
    yield
    # Shutdown
    pass


# Создаём приложение
app = FastAPI(
    title=settings.app_name,
    description="""
    🚀 **WORK21** — платформа, соединяющая студентов Школы 21 с реальными заказчиками.
    
    ## Возможности API
    
    * 🔐 **Аутентификация** — регистрация и вход (JWT)
    * 👤 **Пользователи** — профили студентов и заказчиков
    * 📋 **Проекты** — создание и управление проектами
    * 📝 **Заявки** — подача и обработка заявок
    * ⭐ **Рейтинги** — система оценок и отзывов
    
    ## AI-агенты (в разработке)
    
    * **Task Analyst** — анализ задач и генерация ТЗ
    * **Talent Matcher** — подбор исполнителей
    * **Legal Assistant** — генерация договоров
    """,
    version=settings.app_version,
    lifespan=lifespan,
)

# CORS middleware - для работы с cookies через постоянные домены
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8099",
        "https://ift-1.brojs.ru",
        "https://ift-2.brojs.ru",
        "https://ift-3.brojs.ru",
        "https://admin.work-21.com",
        "https://work-21.com",
    ],
    allow_credentials=True,  # Включаем для cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session middleware (для админ-панели) - должен быть ПОСЛЕ CORS
app.add_middleware(
    SessionMiddleware,
    secret_key="super-secret-session-key-work21-admin",
    same_site="lax",
    https_only=False,
)

# Подключаем роутеры
app.include_router(api_router, prefix="/api/v1")

# Админ-панель (доступна по /admin)
admin = create_admin(app)


@app.get("/", tags=["root"])
async def root():
    """
    Корневой endpoint — информация о сервисе
    """
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc",
        "admin": "/admin",
    }


@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}


