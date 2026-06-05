from django.core.mail import send_mail
from django.db import models
from django.utils import timezone

from clients.models import Client
from email_messages.models import Message


class Mailing(models.Model):
    STATUS_CHOICES = [
        ('created', 'Создана'),
        ('started', 'Запущена'),
        ('completed', 'Завершена'),
    ]

    first_sent_at = models.DateTimeField(verbose_name="Дата и время первой отправки")
    end_at = models.DateTimeField(verbose_name="Дата и время окончания отправки")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created', verbose_name="Статус")
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name="Сообщение")
    recipients = models.ManyToManyField(Client, verbose_name="Получатели")
    is_sent = models.BooleanField(default=False, verbose_name="Была ли отправка")

    def __str__(self):
        return f"Рассылка #{self.id} - {self.get_status_display()}"

    def send(self):
        from .models import MailingAttempt  # импорт внутри метода, чтобы избежать цикла
        success_count = 0
        for client in self.recipients.all():
            try:
                send_mail(...)
                MailingAttempt.objects.create(
                    mailing=self,
                    status='success',
                    server_response='OK'
                )
                success_count += 1
            except Exception as e:
                MailingAttempt.objects.create(
                    mailing=self,
                    status='failed',
                    server_response=str(e)

                )
        if not self.is_sent and success_count > 0:
            self.is_sent = True
            self.status = 'started'
            self.save()

        return success_count


class MailingAttempt(models.Model):
    STATUS_CHOICES = [
        ('success', 'Успешно'),
        ('failed', 'Не успешно'),
    ]

    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, verbose_name="Рассылка")
    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время попытки")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Статус")
    server_response = models.TextField(blank=True, verbose_name="Ответ почтового сервера")

    def __str__(self):
        return f"Попытка #{self.id} - {self.get_status_display()}"

    def update_status(self):
        """Обновляет статус рассылки по правилам ТЗ"""
        if self.status == 'completed':
            return  # Завершённые не трогаем

        if self.end_at < timezone.now():
            self.status = 'completed'

        self.save()
