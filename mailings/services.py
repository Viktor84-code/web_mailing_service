from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import MailingAttempt


class MailingService:
    """Сервис для работы с рассылками (бизнес-логика)"""

    @staticmethod
    def send_mailing(mailing):
        """
        Отправляет рассылку всем получателям.
        Возвращает количество успешных отправок.
        """
        now = timezone.now()

        # Проверка что рассылка активна по времени
        if not (mailing.first_sent_at <= now <= mailing.end_at):
            raise ValueError("Рассылка неактивна в данный момент")

        # Проверка что рассылка включена менеджером
        if not mailing.is_active:
            raise ValueError("Рассылка отключена менеджером")

        success_count = 0

        for client in mailing.recipients.all():
            try:
                send_mail(
                    subject=mailing.message.subject,
                    message=mailing.message.body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[client.email],
                    fail_silently=False,
                )
                MailingAttempt.objects.create(
                    mailing=mailing,
                    status="success",
                    server_response="OK"
                )
                success_count += 1
            except Exception as e:
                MailingAttempt.objects.create(
                    mailing=mailing,
                    status="failed",
                    server_response=str(e)
                )

        # Если хотя бы одно письмо ушло - отмечаем рассылку как отправленную
        if success_count > 0 and not mailing.is_sent:
            mailing.is_sent = True
            mailing.save()

        return success_count

    @staticmethod
    def update_status(mailing):
        """
        Обновляет статус рассылки на основе текущего времени.
        """
        now = timezone.now()

        if now < mailing.first_sent_at:
            new_status = "created"
        elif mailing.first_sent_at <= now <= mailing.end_at:
            new_status = "started"
        else:
            new_status = "completed"

        if mailing.status != new_status:
            mailing.status = new_status
            mailing.save()
            return True
        return False

    @staticmethod
    def can_send(mailing):
        """
        Проверяет, можно ли отправить рассылку.
        """
        now = timezone.now()
        return (
                mailing.is_active and
                mailing.first_sent_at <= now <= mailing.end_at
        )
