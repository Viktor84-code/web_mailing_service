"""Команда для отправки рассылки через консоль.

Пример использования:
    python manage.py send_mailing 1
"""

import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from mailings.models import Mailing
from mailings.services import MailingService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Отправляет рассылку по её ID или все активные рассылки."""

    help = "Отправляет рассылку по ID или все активные рассылки"

    def add_arguments(self, parser):
        """Добавляет аргумент mailing_id в команду."""
        parser.add_argument(
            "mailing_id",
            type=int,
            nargs="?",
            help="ID рассылки для отправки (если не указан - отправляются все активные)",
        )

    def handle(self, *args, **options):
        """Основная логика команды."""
        mailing_id = options.get("mailing_id")

        if mailing_id:
            self._send_single_mailing(mailing_id)
        else:
            self._send_all_active_mailings()

    def _send_single_mailing(self, mailing_id):
        """Отправляет одну рассылку по ID."""
        try:
            mailing = Mailing.objects.get(pk=mailing_id)

            # Проверяем, можно ли отправить
            if not MailingService.can_send(mailing):
                self.stdout.write(
                    self.style.WARNING(f"Рассылка #{mailing_id} неактивна или не входит в интервал отправки")
                )
                return

            # Обновляем статус на "started"
            mailing.status = "started"
            mailing.save(update_fields=["status"])

            # Отправляем через сервис
            result = MailingService.send_mailing(mailing)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Рассылка #{mailing_id} отправлена. "
                    f"Успешно: {result['success_count']}, "
                    f"Ошибок: {result['failed_count']}"
                )
            )
            logger.info(
                f"Команда send_mailing: рассылка {mailing_id} отправлена. "
                f"Успешно: {result['success_count']}, Ошибок: {result['failed_count']}"
            )

        except Mailing.DoesNotExist:
            msg = f"Рассылка #{mailing_id} не найдена"
            self.stdout.write(self.style.ERROR(msg))
            logger.error(msg)
        except ValueError as e:
            self.stdout.write(self.style.ERROR(str(e)))
            logger.error(f"Ошибка валидации рассылки {mailing_id}: {e}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка: {e}"))
            logger.error(f"Неизвестная ошибка при отправке рассылки {mailing_id}: {e}")

    def _send_all_active_mailings(self):
        """Отправляет все активные рассылки, которые можно отправить."""
        now = timezone.now()

        # Ищем рассылки, которые можно отправить
        mailings = Mailing.objects.filter(
            is_active=True, is_sent=False, first_sent_at__lte=now, end_at__gte=now
        ).select_related("message")

        if not mailings.exists():
            self.stdout.write(self.style.WARNING("Нет активных рассылок для отправки"))
            return

        total_sent = 0
        total_errors = 0
        total_success_messages = 0
        total_failed_messages = 0

        for mailing in mailings:
            try:
                # Обновляем статус на "started"
                mailing.status = "started"
                mailing.save(update_fields=["status"])

                # Отправляем через сервис
                result = MailingService.send_mailing(mailing)

                total_sent += 1
                total_success_messages += result["success_count"]
                total_failed_messages += result["failed_count"]

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Рассылка #{mailing.id} отправлена. "
                        f"Успешно: {result['success_count']}, "
                        f"Ошибок: {result['failed_count']}"
                    )
                )
                logger.info(
                    f"Рассылка {mailing.id} отправлена. "
                    f"Успешно: {result['success_count']}, Ошибок: {result['failed_count']}"
                )

            except Exception as e:
                total_errors += 1
                self.stdout.write(self.style.ERROR(f"Ошибка при отправке рассылки #{mailing.id}: {e}"))
                logger.error(f"Ошибка при отправке рассылки {mailing.id}: {e}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nГотово! Отправлено рассылок: {total_sent}, "
                f"ошибок при отправке рассылок: {total_errors}\n"
                f"Всего писем: успешно {total_success_messages}, "
                f"ошибок {total_failed_messages}"
            )
        )
        logger.info(
            f"Команда send_mailing завершена. "
            f"Рассылок: {total_sent}, ошибок: {total_errors}. "
            f"Писем: успешно {total_success_messages}, ошибок {total_failed_messages}"
        )
