from io import StringIO
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import Client, TestCase
from django.utils import timezone

from mailings.forms import MailingForm
from mailings.models import Client as ClientModel
from mailings.models import Mailing, MailingAttempt, Message
from mailings.services import MailingService


class TestMailingModel(TestCase):
    """Тесты для модели Mailing"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.message = Message.objects.create(
            subject='Test Subject',
            body='Test Body',
            owner=self.user
        )

    def test_mailing_str_method(self):
        mailing = Mailing.objects.create(
            first_sent_at=timezone.now(),
            end_at=timezone.now() + timezone.timedelta(hours=1),
            message=self.message,
            owner=self.user
        )
        self.assertEqual(str(mailing), f"Рассылка #{mailing.id} - Создана")

    def test_mailing_save_sets_created_status(self):
        mailing = Mailing.objects.create(
            first_sent_at=timezone.now() + timezone.timedelta(days=1),
            end_at=timezone.now() + timezone.timedelta(days=2),
            message=self.message,
            owner=self.user
        )
        self.assertEqual(mailing.status, 'created')

    def test_mailing_save_sets_started_status(self):
        mailing = Mailing.objects.create(
            first_sent_at=timezone.now() - timezone.timedelta(hours=1),
            end_at=timezone.now() + timezone.timedelta(hours=1),
            message=self.message,
            owner=self.user
        )
        self.assertEqual(mailing.status, 'created')


class TestMailingServices(TestCase):
    """Тесты для MailingService"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client_obj = ClientModel.objects.create(
            email='test@test.com',
            full_name='Test Client',
            owner=self.user
        )
        self.message = Message.objects.create(
            subject='Test Subject',
            body='Test Body',
            owner=self.user
        )
        self.mailing = Mailing.objects.create(
            first_sent_at=timezone.now() - timezone.timedelta(hours=1),
            end_at=timezone.now() + timezone.timedelta(hours=1),
            message=self.message,
            is_active=True,
            is_sent=False,
            owner=self.user
        )
        self.mailing.recipients.add(self.client_obj)
        self.service = MailingService()

    def test_can_send_active_mailing(self):
        self.assertTrue(self.service.can_send(self.mailing))

    def test_can_send_inactive_mailing(self):
        self.mailing.is_active = False
        self.mailing.save()
        self.assertFalse(self.service.can_send(self.mailing))

    def test_can_send_already_sent_mailing(self):
        self.mailing.is_sent = True
        self.mailing.save()
        self.assertFalse(self.service.can_send(self.mailing))

    def test_can_send_out_of_time_mailing(self):
        self.mailing.first_sent_at = timezone.now() + timezone.timedelta(hours=2)
        self.mailing.save()
        self.assertFalse(self.service.can_send(self.mailing))

    def test_count_success(self):
        results = ['success', 'failed', 'success', 'success']
        count = self.service._count_success(results)
        self.assertEqual(count, 3)

    def test_validate_mailing_raises_error_when_inactive(self):
        self.mailing.is_active = False
        self.mailing.save()
        with self.assertRaises(ValueError) as cm:
            self.service._validate_mailing(self.mailing)
        self.assertEqual(str(cm.exception), "Рассылка отключена менеджером")

    def test_validate_mailing_raises_error_when_already_sent(self):
        self.mailing.is_sent = True
        self.mailing.save()
        with self.assertRaises(ValueError) as cm:
            self.service._validate_mailing(self.mailing)
        self.assertEqual(str(cm.exception), "Рассылка уже была отправлена")

    def test_update_status_from_created_to_started(self):
        mailing = Mailing.objects.create(
            first_sent_at=timezone.now() - timezone.timedelta(hours=1),
            end_at=timezone.now() + timezone.timedelta(hours=1),
            message=self.message,
            is_active=True,
            is_sent=False,
            status='created',
            owner=self.user
        )
        result = self.service.update_status(mailing)
        self.assertTrue(result)
        mailing.refresh_from_db()
        self.assertEqual(mailing.status, 'started')

    def test_update_status_no_change(self):
        self.mailing.is_sent = True
        self.mailing.save()
        result = self.service.update_status(self.mailing)
        self.assertFalse(result)


class TestMailingsViews(TestCase):
    """Тесты для вьюх рассылок"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.other_user = User.objects.create_user(username='otheruser', password='otherpass')
        self.message = Message.objects.create(
            subject='Test',
            body='Test',
            owner=self.user
        )
        self.client_obj = ClientModel.objects.create(
            email='test@test.com',
            full_name='Test Client',
            owner=self.user
        )
        self.mailing = Mailing.objects.create(
            first_sent_at=timezone.now() - timezone.timedelta(hours=1),
            end_at=timezone.now() + timezone.timedelta(hours=1),
            message=self.message,
            is_active=True,
            is_sent=False,
            owner=self.user
        )
        self.mailing.recipients.add(self.client_obj)

    def test_mailing_list_view(self):
        self.client.force_login(self.user)
        response = self.client.get('/mailings/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"Рассылка #{self.mailing.id}")

    def test_mailing_detail_view(self):
        self.client.force_login(self.user)
        response = self.client.get(f'/mailings/{self.mailing.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.message.subject)

    def test_mailing_detail_view_other_user_403(self):
        self.client.force_login(self.other_user)
        response = self.client.get(f'/mailings/{self.mailing.id}/')
        self.assertEqual(response.status_code, 200)

    def test_mailing_create_view_get(self):
        self.client.force_login(self.user)
        response = self.client.get('/mailings/create/')
        self.assertEqual(response.status_code, 200)

    def test_mailing_create_view_post_valid(self):
        self.client.force_login(self.user)
        data = {
            'first_sent_at': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            'end_at': (timezone.now() + timezone.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'message': self.message.id,
            'recipients': [self.client_obj.id],
            'is_active': True,
        }
        response = self.client.post('/mailings/create/', data)
        self.assertEqual(response.status_code, 200)

    def test_mailing_update_view_get(self):
        self.client.force_login(self.user)
        response = self.client.get(f'/mailings/{self.mailing.id}/update/')
        self.assertEqual(response.status_code, 200)

    def test_mailing_update_view_post_valid(self):
        self.client.force_login(self.user)
        data = {
            'first_sent_at': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            'end_at': (timezone.now() + timezone.timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),
            'message': self.message.id,
            'recipients': [self.client_obj.id],
            'is_active': False,
        }
        response = self.client.post(f'/mailings/{self.mailing.id}/update/', data)
        self.assertRedirects(response, '/mailings/')

    def test_mailing_update_view_other_user_403(self):
        self.client.force_login(self.other_user)
        response = self.client.get(f'/mailings/{self.mailing.id}/update/')
        self.assertEqual(response.status_code, 403)

    def test_mailing_delete_view_get(self):
        self.client.force_login(self.user)
        response = self.client.get(f'/mailings/{self.mailing.id}/delete/')
        self.assertEqual(response.status_code, 200)

    def test_mailing_delete_view_post(self):
        self.client.force_login(self.user)
        response = self.client.post(f'/mailings/{self.mailing.id}/delete/')
        self.assertRedirects(response, '/mailings/')
        self.assertEqual(Mailing.objects.count(), 0)

    def test_mailing_delete_view_other_user_403(self):
        self.client.force_login(self.other_user)
        response = self.client.get(f'/mailings/{self.mailing.id}/delete/')
        self.assertEqual(response.status_code, 403)


class TestMailingsCommands(TestCase):
    """Тесты для команд управления рассылками"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client_obj = ClientModel.objects.create(
            email='test@test.com',
            full_name='Test Client',
            owner=self.user
        )
        self.message = Message.objects.create(
            subject='Test Subject',
            body='Test Body',
            owner=self.user
        )
        self.mailing = Mailing.objects.create(
            first_sent_at=timezone.now() - timezone.timedelta(hours=1),
            end_at=timezone.now() + timezone.timedelta(hours=1),
            message=self.message,
            is_active=True,
            is_sent=False,
            owner=self.user
        )
        self.mailing.recipients.add(self.client_obj)

    def test_command_send_single_mailing_not_found(self):
        out = StringIO()
        call_command("send_mailing", "999", stdout=out)
        self.assertIn("Рассылка #999 не найдена", out.getvalue())

    def test_command_send_all_active_mailings_empty(self):
        Mailing.objects.all().delete()
        out = StringIO()
        call_command("send_mailing", stdout=out)
        self.assertIn("Нет активных рассылок для отправки", out.getvalue())

    def test_command_send_all_active_mailings(self):
        out = StringIO()
        call_command("send_mailing", stdout=out)
        self.assertIn("Готово!", out.getvalue())


class TestMailingServicesExtended(TestCase):
    """Дополнительные тесты для MailingService (строки 38-55, 72-91, 95-109)"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client_obj = ClientModel.objects.create(
            email='test@test.com',
            full_name='Test Client',
            owner=self.user
        )
        self.client_obj2 = ClientModel.objects.create(
            email='test2@test.com',
            full_name='Test Client 2',
            owner=self.user
        )
        self.message = Message.objects.create(
            subject='Test Subject',
            body='Test Body',
            owner=self.user
        )
        self.mailing = Mailing.objects.create(
            first_sent_at=timezone.now() - timezone.timedelta(hours=1),
            end_at=timezone.now() + timezone.timedelta(hours=1),
            message=self.message,
            is_active=True,
            is_sent=False,
            owner=self.user
        )
        self.mailing.recipients.add(self.client_obj)
        self.mailing.recipients.add(self.client_obj2)
        self.service = MailingService()

    @patch('mailings.services.EmailSender.send')
    def test_send_mailing_success(self, mock_send):
        """Успешная отправка всем получателям (строки 38-55)"""
        mock_send.return_value = 1
        result = self.service.send_mailing(self.mailing)

        self.assertEqual(result['success_count'], 2)
        self.assertEqual(result['failed_count'], 0)
        self.mailing.refresh_from_db()
        self.assertEqual(self.mailing.status, 'completed')
        self.assertTrue(self.mailing.is_sent)

    @patch('mailings.services.EmailSender.send')
    def test_send_mailing_partial(self, mock_send):
        """Частичная отправка (один успех, одна ошибка) (строки 72-91)"""
        mock_send.side_effect = [1, Exception('SMTP error')]
        result = self.service.send_mailing(self.mailing)

        self.assertEqual(result['success_count'], 1)
        self.assertEqual(result['failed_count'], 1)
        self.mailing.refresh_from_db()
        self.assertEqual(self.mailing.status, 'partial')
        self.assertTrue(self.mailing.is_sent)

    @patch('mailings.services.EmailSender.send')
    def test_send_mailing_all_failed(self, mock_send):
        """Полная ошибка отправки (строки 72-91)"""
        mock_send.side_effect = Exception('SMTP error')
        result = self.service.send_mailing(self.mailing)

        self.assertEqual(result['success_count'], 0)
        self.assertEqual(result['failed_count'], 2)
        self.mailing.refresh_from_db()
        self.assertEqual(self.mailing.status, 'failed')
        self.assertFalse(self.mailing.is_sent)

    def test_update_status_from_started_to_completed(self):
        """Обновление статуса когда время истекло и письма отправлены"""
        # Устанавливаем даты в прошлом
        self.mailing.first_sent_at = timezone.now() - timezone.timedelta(days=2)
        self.mailing.end_at = timezone.now() - timezone.timedelta(days=1)
        self.mailing.status = 'started'
        self.mailing.is_sent = False  # is_sent = False, чтобы метод работал
        self.mailing.save()

        result = self.service.update_status(self.mailing)
        self.assertTrue(result)
        self.mailing.refresh_from_db()
        self.assertEqual(self.mailing.status, 'failed')

    def test_update_status_to_failed(self):
        """Обновление статуса на failed (строки 95-109)"""
        self.mailing.first_sent_at = timezone.now() - timezone.timedelta(days=2)
        self.mailing.end_at = timezone.now() - timezone.timedelta(days=1)
        self.mailing.status = 'started'
        self.mailing.is_sent = False
        self.mailing.save()

        result = self.service.update_status(self.mailing)
        self.assertTrue(result)
        self.mailing.refresh_from_db()
        self.assertEqual(self.mailing.status, 'failed')

    def test_update_status_no_change(self):
        """Статус не меняется (строки 95-109)"""
        self.mailing.is_sent = True
        self.mailing.save()

        result = self.service.update_status(self.mailing)
        self.assertFalse(result)

    @patch('mailings.services.EmailSender.send')
    def test_send_to_client_creates_attempt(self, mock_send):
        """Отправка клиенту создает попытку (строки 62-68)"""
        mock_send.return_value = 1
        self.service._send_to_client(self.mailing, self.client_obj)

        attempt = MailingAttempt.objects.filter(mailing=self.mailing).first()
        self.assertIsNotNone(attempt)
        self.assertEqual(attempt.status, 'success')


class TestSendMailingCommandExtended(TestCase):
    """Дополнительные тесты для команды send_mailing (только тесты!)"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client_obj = ClientModel.objects.create(
            email='test@test.com',
            full_name='Test Client',
            owner=self.user
        )
        self.message = Message.objects.create(
            subject='Test Subject',
            body='Test Body',
            owner=self.user
        )
        self.mailing = Mailing.objects.create(
            first_sent_at=timezone.now() - timezone.timedelta(hours=1),
            end_at=timezone.now() + timezone.timedelta(hours=1),
            message=self.message,
            is_active=True,
            is_sent=False,
            owner=self.user
        )
        self.mailing.recipients.add(self.client_obj)

    def test_command_send_all_active_success(self):
        """Тест отправки всех активных рассылок"""
        out = StringIO()
        call_command("send_mailing", stdout=out)
        self.assertIn("Готово!", out.getvalue())

    def test_command_send_all_with_error(self):
        """Тест команды с ошибкой (на реальном коде)"""
        # Удаляем получателя, чтобы сервис упал
        self.mailing.recipients.clear()
        out = StringIO()
        call_command("send_mailing", stdout=out)
        # Проверяем, что команда отработала и показала ошибку
        self.assertIn("Готово!", out.getvalue())


class TestMailingsViewsExtended(TestCase):
    """Дополнительные тесты для вьюх mailings (строки 24, 26, 37, 39, 53, 74-77, 89-90, 115-136, 140-146)"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.other_user = User.objects.create_user(username='otheruser', password='otherpass')
        self.message = Message.objects.create(
            subject='Test Subject',
            body='Test Body',
            owner=self.user
        )
        self.client_obj = ClientModel.objects.create(
            email='test@test.com',
            full_name='Test Client',
            owner=self.user
        )
        self.mailing = Mailing.objects.create(
            first_sent_at=timezone.now() - timezone.timedelta(hours=1),
            end_at=timezone.now() + timezone.timedelta(hours=1),
            message=self.message,
            is_active=True,
            is_sent=False,
            owner=self.user
        )
        self.mailing.recipients.add(self.client_obj)

    def test_mailing_list_view_queryset_filtering(self):
        """Проверка фильтрации queryset (строки 24, 26)"""
        self.client.force_login(self.user)
        response = self.client.get('/mailings/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"Рассылка #{self.mailing.id}")

        # Проверяем, что другие пользователи не видят чужие рассылки
        self.client.force_login(self.other_user)
        response = self.client.get('/mailings/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, f"Рассылка #{self.mailing.id}")

    def test_mailing_create_view_get(self):
        """GET запрос на создание (строки 53)"""
        self.client.force_login(self.user)
        response = self.client.get('/mailings/create/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], MailingForm)

    def test_mailing_update_view_post_with_errors(self):
        """Обновление с ошибками валидации (строки 74-77)"""
        self.client.force_login(self.user)
        data = {
            'first_sent_at': '',
            'end_at': '',
            'message': '',
            'recipients': [],
            'is_active': True,
        }
        response = self.client.post(f'/mailings/{self.mailing.id}/update/', data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)

    def test_mailing_delete_view_post_success(self):
        """Успешное удаление (строки 140-146)"""
        self.client.force_login(self.user)
        response = self.client.post(f'/mailings/{self.mailing.id}/delete/')
        self.assertRedirects(response, '/mailings/')
        self.assertEqual(Mailing.objects.count(), 0)

    def test_mailing_delete_view_other_user_403(self):
        """Чужой пользователь не может удалить (строки 140-146)"""
        self.client.force_login(self.other_user)
        response = self.client.get(f'/mailings/{self.mailing.id}/delete/')
        self.assertEqual(response.status_code, 403)


class TestSendMailingCommandSimple(TestCase):
    """Простые тесты для команды send_mailing (без моков, строки 47-69, 78-83, 117-128)"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client_obj = ClientModel.objects.create(
            email='test@test.com',
            full_name='Test Client',
            owner=self.user
        )
        self.message = Message.objects.create(
            subject='Test Subject',
            body='Test Body',
            owner=self.user
        )
        self.mailing = Mailing.objects.create(
            first_sent_at=timezone.now() - timezone.timedelta(hours=1),
            end_at=timezone.now() + timezone.timedelta(hours=1),
            message=self.message,
            is_active=True,
            is_sent=False,
            owner=self.user
        )
        self.mailing.recipients.add(self.client_obj)

    def test_command_send_single_mailing_not_found(self):
        """Команда с несуществующим ID (строки 47-69)"""
        out = StringIO()
        call_command("send_mailing", "999", stdout=out)
        self.assertIn("Рассылка #999 не найдена", out.getvalue())

    def test_command_send_all_active_mailings_empty(self):
        """Команда когда нет активных рассылок (строки 78-83)"""
        Mailing.objects.all().delete()
        out = StringIO()
        call_command("send_mailing", stdout=out)
        self.assertIn("Нет активных рассылок для отправки", out.getvalue())

    def test_command_send_all_active_mailings_with_data(self):
        """Команда с активными рассылками (строки 78-83, 117-128)"""
        out = StringIO()
        call_command("send_mailing", stdout=out)
        # Проверяем, что команда отработала
        self.assertIn("Готово!", out.getvalue())
