# CLAUDE.md - Work21 Backend

## Обзор проекта

**Work21 Backend** — REST API сервер на FastAPI для платформы фриланса, соединяющей студентов и заказчиков.

## Технологический стек

- **Framework:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL 15
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic
- **Auth:** JWT (python-jose)
- **Validation:** Pydantic v2
- **Container:** Docker

## Структура проекта

```
work21-backend/
├── app/
│   ├── main.py              # Точка входа FastAPI
│   ├── api/                  # API endpoints
│   │   ├── auth.py          # Авторизация (login, register)
│   │   ├── users.py         # Пользователи
│   │   ├── projects.py      # Проекты
│   │   └── ratings.py       # Рейтинги
│   ├── models/              # SQLAlchemy модели
│   │   ├── user.py
│   │   ├── project.py
│   │   └── task.py
│   ├── schemas/             # Pydantic схемы
│   ├── core/
│   │   ├── config.py        # Настройки приложения
│   │   ├── security.py      # JWT, хеширование паролей
│   │   └── database.py      # Подключение к БД
│   └── crud/                # CRUD операции
├── alembic/                 # Миграции базы данных
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Ключевые команды

```bash
# Запуск с Docker
docker compose up -d

# Локальный запуск
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Миграции
alembic upgrade head
alembic revision --autogenerate -m "описание"

# Тесты
pytest
```

## API Endpoints

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/v1/auth/register` | Регистрация |
| POST | `/api/v1/auth/login` | Вход (OAuth2) |
| GET | `/api/v1/users/me` | Текущий пользователь |
| GET | `/api/v1/projects/` | Список проектов |
| POST | `/api/v1/projects/` | Создать проект |
| POST | `/api/v1/projects/{id}/apply` | Подать заявку |

Полная документация: `/docs` (Swagger UI)

## Переменные окружения

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/work21
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Модели данных

### User
- `id`, `email`, `hashed_password`
- `first_name`, `last_name`
- `role`: student | customer | admin
- `rating_score`, `completed_projects`

### Project
- `id`, `title`, `description`, `requirements`
- `budget`, `deadline`, `tech_stack`
- `status`: draft | open | in_progress | review | completed
- `customer_id`, `assignee_id`

### Task
- `id`, `title`, `description`
- `complexity`, `estimated_hours`
- `status`, `project_id`, `assignee_id`

## CORS

Разрешённые origins настраиваются в `app/core/config.py`:
```python
cors_origins: list[str] = [
    "http://localhost:3000",
    "http://localhost:8099",
    "https://ift-1.brojs.ru",
]
```

## Связанные сервисы

- **AI Agent:** https://github.com/ChargeOnTop/work21-agent
- **Frontend:** https://github.com/ChargeOnTop/work21-fr
- **Deploy:** https://github.com/ChargeOnTop/work21-deploy

## Production

- **URL:** https://api.work-21.com
- **Docs:** https://api.work-21.com/docs

