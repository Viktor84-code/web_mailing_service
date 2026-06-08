from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from clients.models import Client
from email_messages.models import Message
from mailings.models import Mailing


@pytest.mark.django_db
class TestMain:

    def test_home_page_stats(self, client):  # ← добавили client в аргументы
        # Создаём клиентов
        Client.objects.create(email="a@a.com", full_name="A")
        Client.objects.create(email="b@b.com", full_name="B")

        # Создаём сообщение
        message = Message.objects.create(subject="Test", body="Body")

        # Создаём рассылки с корректными датами (с часовым поясом)
        start = timezone.now() - timedelta(days=1)  # уже началась
        end = timezone.now() + timedelta(days=7)  # ещё не закончилась

        Mailing.objects.create(first_sent_at=start, end_at=end, message=message, status="started")
        Mailing.objects.create(first_sent_at=start, end_at=end, message=message, status="started")

        url = reverse("main:home")
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["unique_clients"] == 2
        assert response.context["total_mailings"] == 2
        assert response.context["active_mailings"] == 2
