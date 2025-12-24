# WORK21 Backend API

🚀 Бэкенд платформы WORK21 — соединяет студентов Школы 21 с реальными заказчиками.

## Технологии

- **FastAPI** — современный async Python фреймворк
- **PostgreSQL** — база данных
- **SQLAlchemy** — ORM
- **Alembic** — миграции
- **JWT** — аутентификация
- **Docker** — контейнеризация

## Быстрый старт

### 1. Клонирование

```bash
git clone https://github.com/ChargeOnTop/work21-backend.git
cd work21-backend
```

### 2. Настройка окружения

```bash
cp .env.production.example .env
# Отредактируйте .env файл
```

### 3. Запуск с Docker

```bash
docker compose up -d
```

### 4. Проверка

```bash
curl http://localhost:8000/health
# {"status":"healthy"}
```

## API Документация

После запуска доступна по адресам:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Admin панель: http://localhost:8000/admin

## Структура проекта

```
work21-backend/
├── app/
│   ├── api/           # API endpoints
│   ├── core/          # Конфигурация, безопасность
│   ├── models/        # SQLAlchemy модели
│   ├── schemas/       # Pydantic схемы
│   ├── services/      # Бизнес-логика
│   └── main.py        # Точка входа
├── alembic/           # Миграции БД
├── nginx/             # Конфигурация Nginx
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `DATABASE_URL` | URL подключения к PostgreSQL | - |
| `SECRET_KEY` | Секретный ключ для JWT | - |
| `DEBUG` | Режим отладки | `true` |
| `POSTGRES_USER` | Пользователь БД | `work21` |
| `POSTGRES_PASSWORD` | Пароль БД | `work21password` |
| `POSTGRES_DB` | Имя БД | `work21` |

## Команды

```bash
# Запуск
docker compose up -d

# Логи
docker compose logs -f backend

# Остановка
docker compose down

# Пересборка
docker compose up -d --build

# Миграции (внутри контейнера)
docker exec work21-backend alembic upgrade head
```

## Лицензия

MIT

