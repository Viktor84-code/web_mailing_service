"""Команда для отправки рассылки через консоль.

Пример использования:
    python manage.py send_mailing 1
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from mailings.models import Mailing
from mailings.services import MailingService


class Command(BaseCommand):
    """Отправляет рассылку по её ID или все активные рассылки."""

    help = "Отправляет рассылку по ID или все активные рассылки"

    def add_arguments(self, parser):
        """Добавляет аргумент mailing_id в команду."""
        parser.add_argument(
            "mailing_id",
            type=int,
            nargs="?",  # делаем аргумент опциональным
            help="ID рассылки для отправки (если не указан - отправляются все активные)"
        )

    def handle(self, *args, **options):
        """Основная логика команды."""
        mailing_id = options.get("mailing_id")

        if mailing_id:
            # Отправка конкретной рассылки
            self._send_single_mailing(mailing_id)
        else:
            # Отправка всех активных рассылок
            self._send_all_active_mailings()

    def _send_single_mailing(self, mailing_id):
        """Отправляет одну рассылку по ID."""
        try:
            mailing = Mailing.objects.get(pk=mailing_id)

            # Проверяем, можно ли отправить
            if not MailingService.can_send(mailing):
                self.stdout.write(
                    self.style.WARNING(
                        f"Рассылка #{mailing_id} неактивна или не входит в интервал отправки"
                    )
                )
                return

            # Отправляем через сервис
            count = MailingService.send_mailing(mailing)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Рассылка #{mailing_id} отправлена, успешно: {count}"
                )
            )

        except Mailing.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"Рассылка #{mailing_id} не найдена")
            )
        except ValueError as e:
            self.stdout.write(self.style.ERROR(str(e)))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка: {e}"))

    def _send_all_active_mailings(self):
        """Отправляет все активные рассылки, которые можно отправить."""
        now = timezone.now()

        # Ищем рассылки, которые можно отправить
        mailings = Mailing.objects.filter(
            is_active=True,
            is_sent=False,
            first_sent_at__lte=now,
            end_at__gte=now
        )

        if not mailings.exists():
            self.stdout.write(
                self.style.WARNING("Нет активных рассылок для отправки")
            )
            return

        total_sent = 0
        total_errors = 0

        for mailing in mailings:
            try:
                count = MailingService.send_mailing(mailing)
                total_sent += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Рассылка #{mailing.id} отправлена, успешно: {count}"
                    )
                )
            except Exception as e:
                total_errors += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"Ошибка при отправке рассылки #{mailing.id}: {e}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nГотово! Отправлено: {total_sent}, ошибок: {total_errors}"
            )
        )
