FROM python:3.13-slim

WORKDIR /app

# Установка Poetry
RUN pip install poetry

# Копирование файлов зависимостей
COPY pyproject.toml poetry.lock ./

# Установка зависимостей Python
RUN poetry config virtualenvs.create false && poetry install --no-root


# Копирование исходного кода
COPY . .

# Создание статических файлов и медиа директорий
RUN mkdir -p static media

EXPOSE 8000

# Команда по умолчанию для разработки
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
