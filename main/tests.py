import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from clients.models import Client
from email_messages.models import Message
from mailings.models import Mailing


@pytest.mark.django_db
class TestMain:

    def test_home_page_anonymous(self, client):
        """Главная для неавторизованного пользователя"""
        response = client.get("/")
        # Редирект на логин
        assert response.status_code == 302
        assert "/users/login/" in response.url

    def test_home_page_authenticated(self, client):
        """Главная для авторизованного пользователя"""
        User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        response = client.get("/")
        assert response.status_code == 200
        # Проверяем наличие текста без b''
        assert "Сервис рассылок" in response.content.decode("utf-8")

    def test_home_page_stats(self, client):
        """Проверка статистики на главной"""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        # Создаём клиентов
        Client.objects.create(email="a@a.com", full_name="A", owner=user)
        Client.objects.create(email="b@b.com", full_name="B", owner=user)

        # Создаём сообщение
        message = Message.objects.create(subject="Test", body="Body", owner=user)

        # Создаём рассылки с корректными датами
        start = timezone.now() - timedelta(days=1)
        end = timezone.now() + timedelta(days=7)

        Mailing.objects.create(
            first_sent_at=start,
            end_at=end,
            message=message,
            status="started",
            is_active=True,
            is_sent=False,
            owner=user,
        )
        Mailing.objects.create(
            first_sent_at=start,
            end_at=end,
            message=message,
            status="started",
            is_active=True,
            is_sent=False,
            owner=user,
        )

        url = reverse("main:home")
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["unique_clients"] == 2
        assert response.context["total_mailings"] == 2
        assert response.context["active_mailings"] == 2
