"""
Настройка подключения к базе данных
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


# Создаём асинхронный движок (для API)
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
)

# Синхронный движок (для SQLAdmin)
# Преобразуем async URL в sync URL
if "+asyncpg" in settings.database_url:
    # PostgreSQL: postgresql+asyncpg -> postgresql+psycopg2
    sync_database_url = settings.database_url.replace("+asyncpg", "+psycopg2")
elif "+aiosqlite" in settings.database_url:
    # SQLite: sqlite+aiosqlite -> sqlite
    sync_database_url = settings.database_url.replace("+aiosqlite", "")
else:
    # Если уже синхронный URL, используем как есть
    sync_database_url = settings.database_url

engine = create_engine(
    sync_database_url,
    echo=settings.debug,
)

# Фабрика сессий (асинхронная)
async_session_maker = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


async def get_db() -> AsyncSession:
    """
    Dependency для получения сессии базы данных
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """
    Инициализация базы данных (создание таблиц)
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


