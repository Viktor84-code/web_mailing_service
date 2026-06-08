"""
Модель для управления сообщениями рассылок.
"""

from django.db import models


class Message(models.Model):
    """Модель сообщения для рассылки."""

    subject = models.CharField(max_length=255, verbose_name="Тема письма")
    body = models.TextField(verbose_name="Тело письма")

    def __str__(self):
        """Возвращает тему сообщения."""
        return self.subject
