# Учебный проект по курсу FastAPI

Проект создан в рамках обучения на курсе **Артема Шумейко** ([artemshumeiko.ru](https://artemshumeiko.ru)) и посвящён освоению современного фреймворка **FastAPI** для разработки API на Python.

## Основные технологии
- ⚡ **FastAPI** — высокопроизводительный фреймворк для веб-API
- 🐍 **Python 3.10+** — с поддержкой асинхронности
- 🛢️ **SQLAlchemy 2.0 + Alembic** — работа с базами данных и миграции
- 🛡️ **JWT-аутентификация** — безопасный доступ к API
- 🐳 **Docker** — контейнеризация приложения

## Как запустить проект?
1. Создаем виртуальное окружение:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
2. Установливаем зависимости:
   ```bash
   poetry install
3. Создаем локальную базу PostgreSQL, устанавливаем локальный Redis.
4. Создаем файлы .env и .test.env, аналогичные *.example, записываем свои данные.
5. Запукаем celery:
   ```bash
   celery --app=app.tasks.celery_app:celery_instance worker -l INFO -B
5. Запускаем проект:
   ```bash
   python3 app/main.py