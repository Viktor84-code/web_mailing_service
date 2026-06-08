from django.core.management.base import BaseCommand

from mailings.models import Mailing


class Command(BaseCommand):
    help = "Отправляет рассылку по ID"

    def add_arguments(self, parser):
        parser.add_argument("mailing_id", type=int)

    def handle(self, *args, **options):
        mailing_id = options["mailing_id"]
        try:
            mailing = Mailing.objects.get(pk=mailing_id)
            mailing.send()
            self.stdout.write(self.style.SUCCESS(f"Рассылка #{mailing_id} отправлена"))
        except Mailing.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Рассылка #{mailing_id} не найдена"))
        except ValueError as e:
            self.stdout.write(self.style.ERROR(str(e)))
