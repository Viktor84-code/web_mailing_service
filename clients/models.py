"""
Модель Client для управления получателями рассылок.
"""

from django.db import models


class Client(models.Model):
    """Модель получателя рассылки."""

    email = models.EmailField(unique=True, verbose_name="Email")
    full_name = models.CharField(max_length=255, verbose_name="Ф. И. О.")
    comment = models.TextField(blank=True, verbose_name="Комментарий")

    def __str__(self):
        """Возвращает строковое представление клиента."""
        return self.full_name or self.email
