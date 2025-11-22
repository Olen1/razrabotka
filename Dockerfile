FROM python:3.13-slim

WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml .

# Устанавливаем зависимости
RUN pip install --no-cache-dir "uvicorn[standard]" fastapi

# Копируем весь проект
COPY . .

# Устанавливаем наше приложение
RUN pip install --no-cache-dir -e .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]