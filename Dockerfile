# WORK21 Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Копируем entrypoint скрипт в фиксированное место и делаем исполняемым
# (чтобы он работал даже при монтировании volumes)
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Порт
EXPOSE 8000

# Используем entrypoint для автоматического применения миграций
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

