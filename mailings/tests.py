from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from clients.models import Client
from email_messages.models import Message
from mailings.models import Mailing


@pytest.mark.django_db
def test_mailing_creation():
    client = Client.objects.create(email="test@test.com", full_name="Test")
    message = Message.objects.create(subject="Subj", body="Body")
    start = timezone.now() + timedelta(days=1)
    end = start + timedelta(days=7)
    mailing = Mailing.objects.create(
        first_sent_at=start,
        end_at=end,
        message=message
    )
    mailing.recipients.add(client)
    assert mailing.status == 'created'
    assert mailing.message.subject == "Subj"
    assert mailing.recipients.count() == 1


@pytest.mark.django_db
def test_mailing_status_created():
    client = Client.objects.create(email="test@test.com", full_name="Test")
    message = Message.objects.create(subject="Subj", body="Body")
    start = timezone.now() + timedelta(days=1)
    end = start + timedelta(days=7)
    mailing = Mailing.objects.create(
        first_sent_at=start,
        end_at=end,
        message=message
    )
    mailing.recipients.add(client)
    # не сдвигаем время — start в будущем
    mailing.update_status()
    assert mailing.status == 'created'


@pytest.mark.django_db
def test_client_create_view(client):
    url = reverse('clients:create')
    response = client.get(url)
    assert response.status_code == 200
    response = client.post(url, {
        'email': 'new@test.com',
        'full_name': 'New User',
        'comment': 'Test'
    })
    assert response.status_code == 302  # редирект после создания
    assert Client.objects.count() == 3  # было 2 + 1
