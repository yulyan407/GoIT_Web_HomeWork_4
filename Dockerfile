# Використовуємо базовий образ Python з підтримкою Python 3.11-slim
FROM python:3.11-slim

# Встановимо змінну середовища
ENV APP_HOME /app

# Встановимо робочу директорію всередині контейнера
WORKDIR $APP_HOME

#Встановлюємо залежності всередені контейнера
COPY pyproject.toml $APP_HOME/pyproject.toml

RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install --only main

# Скопіюємо інші файли в робочу директорію контейнера
COPY . .

EXPOSE 3000

# Команда для запуску додатку, змініть на своє
CMD ["python", "main.py"]