# Web Mailing Service

Production-ready сервис для управления email-рассылками с системой прав доступа, кэшированием и автоматической отправкой.

---

## Стек технологий

- **Backend:** Python 3.13, Django 6.0.5
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **Cache & Broker:** Redis 5.0+
- **Task Queue:** Celery (планируется)
- **Frontend:** Bootstrap 5, Font Awesome
- **Admin UI:** django-admin-interface
- **Code Quality:** flake8, black, isort, mypy
- **Testing:** pytest, pytest-django, pytest-cov

---

## Функциональные возможности

### Модули
- **Клиенты** — CRUD с привязкой к владельцу
- **Сообщения** — CRUD с привязкой к владельцу
- **Рассылки** — CRUD с валидацией дат и динамическим статусом
- **Попытки отправки** — логирование каждой попытки с ответом сервера

### Отправка
- Ручной запуск через интерфейс и команду `send_mailing`
- Проверка активности рассылки по времени (`start_time` – `end_time`)
- Создание записей `MailingAttempt` при каждой отправке

### Права доступа
- **Пользователь** — управляет только своими объектами
- **Менеджер** — просмотр всех данных, блокировка пользователей, отключение рассылок
- **Администратор** — полный доступ через Django Admin

### Кэширование
- Redis (серверный кэш)
- Кэширование страниц (главная, детальные, профиль)
- Кэширование шаблонов
- Клиентское кэширование статики (Cache-Control)

### Статистика
- Главная страница: общее количество рассылок, активные, завершённые, клиенты
- Профиль пользователя: успешные/неуспешные попытки, отправленные сообщения

---

## Установка и запуск

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd web_mailing_service
2. Настройка окружения
bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
3. Установка зависимостей
bash
pip install -r requirements.txt
4. Переменные окружения
Создайте файл .env в корне проекта:

env
SECRET_KEY=your-secret-key
DEBUG=True
EMAIL_HOST_USER=your-email@yandex.ru
EMAIL_HOST_PASSWORD=your-app-password
5. Миграции
bash
python manage.py makemigrations
python manage.py migrate
6. Создание суперпользователя
bash
python manage.py createsuperuser
7. Запуск Redis
bash
redis-server
8. Запуск сервера
bash
python manage.py runserver
Команды
Команда	Описание
python manage.py runserver	Запуск dev-сервера
python manage.py createsuperuser	Создание администратора
python manage.py send_mailing <id>	Отправка рассылки по ID
python manage.py send_mailing	Отправка всех активных рассылок
python manage.py collectstatic	Сбор статики
python manage.py flush	Очистка базы данных
Тестирование
Запуск тестов
bash
pytest
Проверка покрытия
bash
pytest --cov=.
Код-стайл
bash
# Форматирование
black .
isort .

# Линтинг
flake8 .
mypy .
```
Автор
Виктор Бриткин