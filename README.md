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
- Динамический статус рассылки (Создана / Запущена / Завершена)
- Отправка писем по требованию (интерфейс + команда)
- Проверка времени отправки (только в интервале start_time – end_time)
- Фиксация попыток рассылок (MailingAttempt)
- Статистика на главной странице
- Валидация дат (start_time не в прошлом, start_time < end_time)
- Человеко-читаемые сообщения об ошибках (с датами по МСК)
- Зелёная тема Bootstrap

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
```

## Команды

- Запуск сервера: `python manage.py runserver`
- Создание суперпользователя: `python manage.py createsuperuser`
- Отправка рассылки: `python manage.py send_mailing <id>`