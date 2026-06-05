# Web Mailing Service

Сервис управления рассылками на Django

## Технологии

- Python 3.13
- Django 6.0.5
- PostgreSQL (планируется)
- pytest, flake8, black, mypy

## Установка

git clone <url>
cd web_mailing_service
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows
pip install -e .[dev]

## Функционал

- Управление клиентами (CRUD)
- Управление сообщениями (CRUD)
- Управление рассылками (CRUD)
- Отправка писем по требованию (интерфейс + команда)
- Автоматические попытки рассылок
- Статистика на главной странице

## Установка и запуск

... (уже есть)

## Технологии

Django, SQLite/PostgreSQL, Bootstrap , Celery