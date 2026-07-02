"""Настройка административной панели для модели Message."""

from django.contrib import admin

from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Настройка отображения модели Message в админке."""

    list_display = ("subject", "owner", "created_at", "preview_body")
    search_fields = ("subject", "body")
    list_filter = ("created_at", "owner")
    ordering = ("-created_at",)
    list_per_page = 25

    def preview_body(self, obj):
        """Возвращает первые 50 символов тела сообщения."""
        return obj.body[:50] + "..." if len(obj.body) > 50 else obj.body

    preview_body.short_description = "Текст (предпросмотр)"
