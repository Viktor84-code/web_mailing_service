"""Настройка административной панели для модели Message."""

from django.contrib import admin

from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Настройка отображения модели Message в админке."""

    list_display = ("subject",)
    search_fields = ("subject",)
