"""
Конфигурация приложения WORK21
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Основные настройки
    app_name: str = "WORK21"
    app_version: str = "0.1.0"
    debug: bool = True
    
    # База данных
    database_url: str = "postgresql+asyncpg://work21:work21password@localhost:5433/work21"
    
    # JWT настройки
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS - разрешаем все необходимые origins
    cors_origins: list[str] = [
        "http://localhost:3000", 
        "http://localhost:8099",
        "https://ift-1.brojs.ru",
        "https://ift-2.brojs.ru",
        "https://ift-3.brojs.ru",
    ]
    
    # AI настройки (опционально)
    openai_api_key: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache()
def get_settings() -> Settings:
    """Получить настройки (кэшированные)"""
    return Settings()


settings = get_settings()


