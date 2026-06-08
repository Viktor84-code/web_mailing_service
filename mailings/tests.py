from datetime import datetime, timedelta
from io import StringIO

import pytest
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time

from clients.models import Client
from email_messages.models import Message
from mailings.forms import MailingForm
from mailings.models import Mailing


@pytest.mark.django_db
class TestMailingsModels:
    def test_mailing_creation(self):
        client = Client.objects.create(email="test@test.com", full_name="Test")
        message = Message.objects.create(subject="Subj", body="Body")
        start = timezone.now() + timedelta(days=1)
        end = start + timedelta(days=7)
        mailing = Mailing.objects.create(first_sent_at=start, end_at=end, message=message)
        mailing.recipients.add(client)
        assert mailing.status == "created"

    @freeze_time("2026-06-10 12:00:00")
    def test_mailing_status_started(self):
        client = Client.objects.create(email="test@test.com", full_name="Test")
        message = Message.objects.create(subject="Subj", body="Body")
        start = timezone.make_aware(datetime(2026, 6, 10, 10, 0, 0))
        end = timezone.make_aware(datetime(2026, 6, 20, 10, 0, 0))
        mailing = Mailing.objects.create(
            first_sent_at=start, end_at=end, message=message, is_sent=True
        )
        mailing.recipients.add(client)
        mailing.update_status()
        assert mailing.status == 'started'


@pytest.mark.django_db
class TestMailingsViews:
    def test_client_create_view(self, client):
        Client.objects.create(email="a@a.com", full_name="A")
        Client.objects.create(email="b@b.com", full_name="B")
        url = reverse("clients:create")
        response = client.get(url)
        assert response.status_code == 200
        response = client.post(url, {
            "email": "new@test.com", "full_name": "New User", "comment": "Test"
        })
        assert response.status_code == 302
        assert Client.objects.count() == 3

    def test_mailing_update_view(self, client):
        message = Message.objects.create(subject="Subj", body="Body")
        client_obj = Client.objects.create(email="test@test.com", full_name="Test")
        mailing = Mailing.objects.create(
            first_sent_at=timezone.now() + timedelta(days=1),
            end_at=timezone.now() + timedelta(days=7),
            message=message
        )
        mailing.recipients.add(client_obj)
        url = reverse('mailings:update', args=[mailing.id])
        response = client.get(url)
        assert response.status_code == 200

    def test_mailing_delete_view(self, client):
        message = Message.objects.create(subject="Subj", body="Body")
        client_obj = Client.objects.create(email="test@test.com", full_name="Test")
        mailing = Mailing.objects.create(
            first_sent_at=timezone.now() + timedelta(days=1),
            end_at=timezone.now() + timedelta(days=7),
            message=message
        )
        mailing.recipients.add(client_obj)
        url = reverse('mailings:delete', args=[mailing.id])
        response = client.get(url)
        assert response.status_code == 200


@pytest.mark.django_db
class TestMailingsCommands:
    def test_command_send_mailing(self):
        client = Client.objects.create(email="test@test.com", full_name="Test")
        message = Message.objects.create(subject="Subj", body="Body")
        mailing = Mailing.objects.create(
            first_sent_at="2026-06-10 10:00:00",
            end_at="2026-06-20 10:00:00",
            message=message
        )
        mailing.recipients.add(client)
        out = StringIO()
        with freeze_time("2026-06-15 12:00:00"):
            call_command('send_mailing', mailing.id, stdout=out)
        assert f"Рассылка #{mailing.id} отправлена" in out.getvalue()

    def test_command_send_mailing_not_found(self):
        out = StringIO()
        call_command('send_mailing', 999, stdout=out)
        assert "Рассылка #999 не найдена" in out.getvalue()


@pytest.mark.django_db
class TestMailingsForms:
    def test_mailing_form_validation_invalid_dates(self):
        message = Message.objects.create(subject="Subj", body="Body")
        client = Client.objects.create(email="test@test.com", full_name="Test")
        start = timezone.now() - timedelta(days=1)
        end = timezone.now() + timedelta(days=7)
        form = MailingForm(data={
            'first_sent_at': start, 'end_at': end, 'message': message.id,
            'status': 'created', 'recipients': [client.id],
        })
        assert not form.is_valid()
        assert any('Дата начала не может быть в прошлом' in error for error in form.errors.get('__all__', []))

    def test_mailing_form_validation_end_before_start(self):
        message = Message.objects.create(subject="Subj", body="Body")
        client = Client.objects.create(email="test@test.com", full_name="Test")
        start = timezone.now() + timedelta(days=5)
        end = timezone.now() + timedelta(days=1)
        form = MailingForm(data={
            'first_sent_at': start, 'end_at': end, 'message': message.id,
            'status': 'created', 'recipients': [client.id],
        })
        assert not form.is_valid()
        assert any('должна быть раньше' in error for error in form.errors.get('__all__', []))
