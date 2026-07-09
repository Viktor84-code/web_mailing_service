"""
Модели для управления рассылками и фиксации попыток отправки.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from clients.models import Client
from email_messages.models import Message


class Mailing(models.Model):
    """Модель рассылки - только данные и валидация."""

    STATUS_CHOICES = [
        ("created", "Создана"),
        ("started", "Запущена"),
        ("partial", "Частично выполнена"),
        ("completed", "Завершена"),
        ("failed", "Ошибка"),
    ]

    first_sent_at = models.DateTimeField(verbose_name="Дата и время начала")
    end_at = models.DateTimeField(verbose_name="Дата и время окончания")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="created", verbose_name="Статус")
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name="Сообщение")
    recipients = models.ManyToManyField(Client, verbose_name="Получатели")
    is_sent = models.BooleanField(default=False, verbose_name="Отправлена")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Владелец"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "is_active", "is_sent"]),
            models.Index(fields=["first_sent_at", "end_at"]),
        ]

    def __str__(self):
        return f"Рассылка #{self.id} - {self.get_status_display()}"

    def clean(self):
        """Валидация дат."""
        if self.first_sent_at and self.end_at:
            if self.first_sent_at >= self.end_at:
                raise ValidationError("Дата начала должна быть раньше даты окончания.")
            # Только для новых объектов
            if not self.pk and self.first_sent_at < timezone.now():
                raise ValidationError("Дата начала не может быть в прошлом.")


class MailingAttempt(models.Model):
    """Модель попытки отправки письма для конкретной рассылки."""

    STATUS_CHOICES = [
        ("success", "Успешно"),
        ("failed", "Не успешно"),
    ]

    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, verbose_name="Рассылка", related_name="attempts")
    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время попытки")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Статус")
    server_response = models.TextField(blank=True, verbose_name="Ответ почтового сервера")

    class Meta:
        verbose_name = "Попытка отправки"
        verbose_name_plural = "Попытки отправки"
        ordering = ["-attempt_time"]
        indexes = [
            models.Index(fields=["mailing", "status"]),
        ]

    def __str__(self):
        return f"Попытка #{self.id} - {self.get_status_display()}"
