#!/usr/bin/env python3
"""
Скрипт для создания администратора
Использование: 
  python scripts/create_admin.py                              # интерактивный режим
  python scripts/create_admin.py email@example.com password   # с аргументами
  ADMIN_PASSWORD=mypass python scripts/create_admin.py        # через env
"""
import asyncio
import sys
import os
import secrets
import string

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.core.database import async_session_maker, init_db
from app.core.security import get_password_hash
from app.models.user import User, UserRole


def generate_secure_password(length: int = 16) -> str:
    """Генерация безопасного случайного пароля"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


async def create_admin(email: str, password: str, first_name: str, last_name: str):
    """Создать администратора в базе данных"""
    
    # Инициализируем БД
    await init_db()
    
    async with async_session_maker() as session:
        # Проверяем, существует ли уже пользователь
        result = await session.execute(
            select(User).where(User.email == email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            if existing_user.role == UserRole.ADMIN:
                print(f"⚠️  Администратор с email {email} уже существует")
                return None
            else:
                # Повышаем до админа
                existing_user.role = UserRole.ADMIN
                existing_user.is_active = True
                existing_user.is_verified = True
                await session.commit()
                print(f"✅ Пользователь {email} повышен до администратора")
                return None
        
        # Создаём нового админа
        admin = User(
            email=email,
            hashed_password=get_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
            rating_score=0.0,
            completed_projects=0,
        )
        
        session.add(admin)
        await session.commit()
        await session.refresh(admin)
        
        print(f"✅ Администратор создан:")
        print(f"   Email: {email}")
        print(f"   Имя: {first_name} {last_name}")
        print(f"   ID: {admin.id}")
        
        return password


def main():
    """Главная функция"""
    print("=" * 50)
    print("🔐 Создание администратора WORK21")
    print("=" * 50)
    
    # Приоритет: аргументы > env > интерактив
    if len(sys.argv) >= 3:
        # Режим с аргументами: python create_admin.py email password [first] [last]
        email = sys.argv[1]
        password = sys.argv[2]
        first_name = sys.argv[3] if len(sys.argv) > 3 else "Admin"
        last_name = sys.argv[4] if len(sys.argv) > 4 else "Work21"
        generated = False
    elif os.environ.get("ADMIN_EMAIL") and os.environ.get("ADMIN_PASSWORD"):
        # Режим через переменные окружения
        email = os.environ["ADMIN_EMAIL"]
        password = os.environ["ADMIN_PASSWORD"]
        first_name = os.environ.get("ADMIN_FIRST_NAME", "Admin")
        last_name = os.environ.get("ADMIN_LAST_NAME", "Work21")
        generated = False
    else:
        # Интерактивный режим
        email = input("Email [admin@work21.ru]: ").strip() or "admin@work21.ru"
        
        # Спрашиваем про пароль
        password_input = input("Пароль (Enter для генерации случайного): ").strip()
        
        if password_input:
            password = password_input
            generated = False
        else:
            password = generate_secure_password()
            generated = True
            print(f"🔑 Сгенерирован пароль: {password}")
        
        first_name = input("Имя [Admin]: ").strip() or "Admin"
        last_name = input("Фамилия [Work21]: ").strip() or "Work21"
    
    # Валидация пароля
    if len(password) < 8:
        print("❌ Пароль должен быть не менее 8 символов")
        sys.exit(1)
    
    result = asyncio.run(create_admin(email, password, first_name, last_name))
    
    print()
    if result:
        print("=" * 50)
        print("🎉 СОХРАНИТЕ ЭТИ ДАННЫЕ!")
        print("=" * 50)
        print(f"   URL:    https://admin.work-21.com")
        print(f"   Email:  {email}")
        print(f"   Пароль: {password}")
        print("=" * 50)
        if generated:
            print("⚠️  Пароль был сгенерирован автоматически!")
            print("   Сохраните его в безопасное место!")


if __name__ == "__main__":
    main()
