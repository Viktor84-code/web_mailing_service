# Web Mailing Service

Сервис управления рассылками на Django

## Технологии

- Python 3.13
- Django 6.0.5
- SQLite / PostgreSQL
- Bootstrap 5 (зелёная тема)
- django-admin-interface
- pytest, flake8, black, mypy (планируется)

## Функционал

- Управление клиентами (CRUD)
- Управление сообщениями (CRUD)
- Управление рассылками (CRUD)
- Отправка писем по требованию (интерфейс + команда)
- Автоматические попытки рассылок (MailingAttempt)
- Статистика на главной странице

## Установка и запуск

```bash
git clone <url>
cd web_mailing_service
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows
pip install -e .[dev]
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver