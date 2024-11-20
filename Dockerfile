# Dockerfile
FROM python:3.10-slim

# Устанавливаем рабочую директорию на уровень с приложением
WORKDIR /app

# Копируем файл зависимостей в корень контейнера
COPY requirements.txt /app/requirements.txt

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Копируем директорию `app` в контейнер
COPY ./app /app/app

# Запускаем приложение
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
