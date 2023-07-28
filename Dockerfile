FROM python:3.10-slim

WORKDIR /usr/src/app

# Скопировать код тестов внутрь контейнера
COPY ./tests /usr/src/app/tests

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Создать кэш-директорию для pytest
RUN mkdir .pytest_cache

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]