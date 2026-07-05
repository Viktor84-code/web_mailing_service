from celery import shared_task
from django.utils import timezone

from mailings.models import Mailing
from mailings.services import MailingService


@shared_task
def check_mailings():
    """Проверяет и отправляет активные рассылки."""
    now = timezone.now()
    mailings = Mailing.objects.filter(is_active=True, is_sent=False, first_sent_at__lte=now, end_at__gte=now)

    for mailing in mailings:
        try:
            MailingService.send_mailing(mailing)
        except Exception as e:
            print(f"Ошибка отправки рассылки #{mailing.id}: {e}")
