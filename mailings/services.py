import logging

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import MailingAttempt

logger = logging.getLogger(__name__)


class EmailSender:
    """Абстракция для отправки писем."""

    @staticmethod
    def send(email, subject, body, from_email):
        """Отправляет одно письмо."""
        return send_mail(
            subject=subject,
            message=body,
            from_email=from_email,
            recipient_list=[email],
            fail_silently=False,
        )


class MailingService:
    """Сервис для работы с рассылками."""

    def __init__(self, email_sender=None):
        self.email_sender = email_sender or EmailSender()

    def send_mailing(self, mailing):
        """
        Отправляет рассылку всем получателям.
        Возвращает словарь с результатами.
        """
        print(f"DEBUG: Начинаем отправку рассылки #{mailing.id}")

        self._validate_mailing(mailing)
        print("DEBUG: Валидация пройдена")

        results = []
        for client in mailing.recipients.all():
            print(f"DEBUG: Отправка клиенту {client.email}")
            result = self._send_to_client(mailing, client)
            results.append(result)
            print(f"DEBUG: Результат {result}")

        print("DEBUG: Все письма отправлены")
        self._update_mailing_status(mailing, results)

        success_count = self._count_success(results)
        failed_count = len(results) - success_count

        logger.info(
            f"Рассылка #{mailing.id} отправлена. "
            f"Успешно: {success_count}, Ошибок: {failed_count}"
        )

        return {
            'success_count': success_count,
            'failed_count': failed_count
        }

    def _validate_mailing(self, mailing):
        """Проверяет, можно ли отправить рассылку."""
        print(f"DEBUG: Валидация рассылки #{mailing.id}")

        # Убрали проверку на время
        if not mailing.is_active:
            print("DEBUG: Ошибка - рассылка отключена")
            raise ValueError("Рассылка отключена менеджером")

        if mailing.is_sent:
            print("DEBUG: Ошибка - рассылка уже отправлена")
            raise ValueError("Рассылка уже была отправлена")

        print("DEBUG: Валидация пройдена успешно")

    def _send_to_client(self, mailing, client):
        """Отправляет письмо одному клиенту и создает попытку."""
        try:
            self.email_sender.send(
                email=client.email,
                subject=mailing.message.subject,
                body=mailing.message.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
            )
            status = "success"
            response = "OK"
        except Exception as e:
            status = "failed"
            response = str(e)
            logger.error(f"Ошибка отправки на {client.email}: {response}")

        MailingAttempt.objects.create(
            mailing=mailing,
            status=status,
            server_response=response
        )
        return status

    def _update_mailing_status(self, mailing, results):
        """Обновляет статус рассылки на основе результатов."""
        success_count = results.count('success')
        failed_count = results.count('failed')

        if success_count == 0:
            new_status = 'failed'
        elif failed_count == 0:
            new_status = 'completed'
        else:
            new_status = 'partial'

        mailing.status = new_status
        # Если хотя бы одно письмо ушло - считаем рассылку отправленной
        if success_count > 0:
            mailing.is_sent = True
        mailing.save()

    def _count_success(self, results):
        """Считает количество успешных отправок."""
        return results.count('success')

    def update_status(self, mailing):
        """
        Обновляет статус по времени (для фоновых задач).
        Возвращает True если статус изменился.
        """
        now = timezone.now()

        # Если рассылка уже отправлена, статус не меняем
        if mailing.is_sent:
            return False

        if now < mailing.first_sent_at:
            new_status = "created"
        elif mailing.first_sent_at <= now <= mailing.end_at:
            new_status = "started"
        else:
            new_status = "completed"
            # Если время истекло, но письма не ушли - помечаем как failed
            if mailing.status != "completed" and not mailing.is_sent:
                new_status = "failed"

        if mailing.status != new_status:
            mailing.status = new_status
            mailing.save()
            logger.info(f"Статус рассылки #{mailing.id} обновлен на {new_status}")
            return True
        return False

    def can_send(self, mailing):
        """
        Проверяет, можно ли отправить рассылку.
        """
        now = timezone.now()
        return (
                mailing.is_active and
                not mailing.is_sent and
                mailing.first_sent_at <= now <= mailing.end_at
        )
