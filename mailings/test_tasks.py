from unittest.mock import patch, MagicMock

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from mailings.models import Client as ClientModel, Mailing, Message
from mailings.tasks import check_mailings


@pytest.mark.django_db
class TestMailingsTasks:

    @patch("mailings.tasks.MailingService")
    def test_check_mailings(self, MockMailingService):
        """Тест задачи check_mailings с моком сервиса"""
        user = User.objects.create_user(username="testuser", password="testpass")
        client_obj = ClientModel.objects.create(email="test@test.com", full_name="Test Client", owner=user)
        message = Message.objects.create(subject="Test Subject", body="Test Body", owner=user)
        mailing = Mailing.objects.create(
            first_sent_at=timezone.now() - timezone.timedelta(hours=1),
            end_at=timezone.now() + timezone.timedelta(hours=1),
            message=message,
            is_active=True,
            is_sent=False,
            owner=user,
        )
        mailing.recipients.add(client_obj)

        # Мокаем метод send_mailing на самом классе
        MockMailingService.send_mailing = MagicMock(return_value={"success_count": 1, "failed_count": 0})

        # Запускаем задачу
        check_mailings()

        # Проверяем, что send_mailing был вызван с правильным аргументом
        MockMailingService.send_mailing.assert_called_once_with(mailing)

    @patch("mailings.tasks.MailingService")
    def test_check_mailings_no_active(self, MockMailingService):
        """Тест когда нет активных рассылок"""
        mock_service = MockMailingService.return_value

        # Запускаем задачу синхронно
        check_mailings()

        # Сервис НЕ должен вызываться, т.к. нет активных рассылок
        mock_service.send_mailing.assert_not_called()
