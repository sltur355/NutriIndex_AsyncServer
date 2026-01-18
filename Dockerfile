FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Создаем пользователя для безопасности
RUN useradd -m -u 1000 django && chown -R django:django /app
USER django

COPY . .

# Запуск сервиса
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]