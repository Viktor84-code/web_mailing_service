import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from clients.models import Client
from email_messages.models import Message
from mailings.models import Mailing


@pytest.mark.django_db
class TestMailingModel:

    def test_mailing_creation(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        message = Message.objects.create(
            subject='Test Subject',
            body='Test Body',
            owner=user
        )
        client = Client.objects.create(
            email='test@example.com',
            full_name='Test Client',
            owner=user
        )
        mailing = Mailing.objects.create(
            first_sent_at=timezone.now() + timezone.timedelta(days=1),
            end_at=timezone.now() + timezone.timedelta(days=2),
            message=message,
            owner=user
        )
        mailing.recipients.add(client)
        assert mailing.status == 'created'
        assert mailing.is_sent is False
        assert mailing.recipients.count() == 1

    def test_mailing_str(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        message = Message.objects.create(
            subject='Test Subject',
            body='Test Body',
            owner=user
        )
        mailing = Mailing.objects.create(
            first_sent_at=timezone.now() + timezone.timedelta(days=1),
            end_at=timezone.now() + timezone.timedelta(days=2),
            message=message,
            owner=user
        )
        assert str(mailing) == f"Рассыла #{mailing.id} - Создана"
