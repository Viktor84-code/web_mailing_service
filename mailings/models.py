"""
Модели для управления рассылками и фиксации попыток отправки.
"""

from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone

from clients.models import Client
from email_messages.models import Message


class Mailing(models.Model):
    """Модель рассылки с параметрами и статусом."""

    STATUS_CHOICES = [
        ("created", "Создана"),
        ("started", "Запущена"),
        ("completed", "Завершена"),
    ]

    first_sent_at = models.DateTimeField(verbose_name="Дата и время начала отправки")
    end_at = models.DateTimeField(verbose_name="Дата и время окончания отправки")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="created", verbose_name="Статус")
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name="Сообщение")
    recipients = models.ManyToManyField(Client, verbose_name="Получатели")
    is_sent = models.BooleanField(default=False, verbose_name="Была ли отправка")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Рассылка #{self.id} - {self.get_status_display()}"

    def update_status(self):
        """Обновляет статус рассылки на основе текущего времени и дат start/end."""
        now = timezone.now()
        print(f"[DEBUG] now = {now}, first_sent_at = {self.first_sent_at}, end_at = {self.end_at}")

        if now < self.first_sent_at:
            new_status = "created"
        elif self.first_sent_at <= now <= self.end_at:
            new_status = "started"
        else:
            new_status = "completed"

        print(f"[DEBUG] new_status = {new_status}, old status = {self.status}")

        if self.status != new_status:
            self.status = new_status
            self.save()
            print(f"[DEBUG] статус обновлён на {new_status}")

    def send(self):
        """Отправляет рассылку всем получателям, фиксирует попытки."""

        from .models import MailingAttempt

        now = timezone.now()
        if not (self.first_sent_at <= now <= self.end_at):
            msk_timezone = timedelta(hours=3)  # Москва UTC+3
            start_msk = self.first_sent_at + msk_timezone
            end_msk = self.end_at + msk_timezone
            start_str = start_msk.strftime("%d.%m.%Y %H:%M")
            end_str = end_msk.strftime("%d.%m.%Y %H:%M")
            raise ValueError(f"Рассылка может быть отправлена только с {start_str} по {end_str}")
        success_count = 0
        for client in self.recipients.all():
            try:
                send_mail(
                    subject=self.message.subject,
                    message=self.message.body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[client.email],
                    fail_silently=False,
                )
                MailingAttempt.objects.create(mailing=self, status="success", server_response="OK")
                success_count += 1
            except Exception as e:
                MailingAttempt.objects.create(mailing=self, status="failed", server_response=str(e))
        if not self.is_sent and success_count > 0:
            self.is_sent = True
            self.status = "started"
            self.save()
        return success_count

    def clean(self):
        """Валидация дат рассылки."""
        if self.first_sent_at and self.end_at:
            if self.first_sent_at >= self.end_at:
                raise ValidationError("Дата начала должна быть раньше даты окончания.")
            if self.first_sent_at < timezone.now():
                raise ValidationError("Дата начала не может быть в прошлом.")


class MailingAttempt(models.Model):
    """Модель попытки отправки письма для конкретной рассылки."""

    STATUS_CHOICES = [
        ("success", "Успешно"),
        ("failed", "Не успешно"),
    ]

    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, verbose_name="Рассылка")
    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время попытки")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Статус")
    server_response = models.TextField(blank=True, verbose_name="Ответ почтового сервера")

    def __str__(self):
        return f"Попытка #{self.id} - {self.get_status_display()}"
