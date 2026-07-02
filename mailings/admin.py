"""Настройка административной панели для модели Mailing."""

from django.contrib import admin
from django.utils.html import format_html

from .models import Mailing, MailingAttempt


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    """Настройка отображения модели Mailing в админке."""

    list_display = (
        "id",
        "status_badge",
        "owner",
        "message",
        "recipients_count",
        "first_sent_at",
        "end_at",
        "is_active",
        "is_sent",
        "created_at",
    )
    list_filter = (
        "status",
        "is_active",
        "is_sent",
        "created_at",
        "owner",
    )
    search_fields = (
        "id",
        "message__subject",
        "owner__email",
        "owner__username",
    )
    list_display_links = ("id", "message")
    ordering = ("-created_at",)
    list_per_page = 25
    readonly_fields = (
        "created_at",
        "is_sent",
        "status",
    )
    fieldsets = (
        ("Основная информация", {
            "fields": (
                "message",
                "recipients",
                "owner",
                "status",
                "is_active",
                "is_sent",
            )
        }),
        ("Временные параметры", {
            "fields": (
                "first_sent_at",
                "end_at",
                "created_at",
            )
        }),
    )

    def status_badge(self, obj):
        """Отображает статус с цветной меткой."""
        colors = {
            "created": "gray",
            "started": "blue",
            "partial": "orange",
            "completed": "green",
            "failed": "red",
        }
        color = colors.get(obj.status, "gray")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )

    status_badge.short_description = "Статус"
    status_badge.admin_order_field = "status"

    def recipients_count(self, obj):
        """Возвращает количество получателей."""
        return obj.recipients.count()

    recipients_count.short_description = "Кол-во получателей"

    def get_queryset(self, request):
        """Оптимизация запросов с подсчетом recipients."""
        return super().get_queryset(request).select_related(
            "message", "owner"
        ).prefetch_related("recipients")


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    """Настройка отображения модели MailingAttempt в админке."""

    list_display = (
        "id",
        "mailing",
        "attempt_time",
        "status_badge",
        "server_response_short",
    )
    list_filter = (
        "status",
        "attempt_time",
    )
    search_fields = (
        "mailing__id",
        "server_response",
    )
    list_display_links = ("id", "mailing")
    ordering = ("-attempt_time",)
    list_per_page = 25
    readonly_fields = (
        "mailing",
        "attempt_time",
        "status",
        "server_response",
    )

    def status_badge(self, obj):
        """Отображает статус с цветной меткой."""
        color = "green" if obj.status == "success" else "red"
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )

    status_badge.short_description = "Статус"
    status_badge.admin_order_field = "status"

    def server_response_short(self, obj):
        """Обрезает server_response до 50 символов."""
        if len(obj.server_response) > 50:
            return obj.server_response[:50] + "..."
        return obj.server_response

    server_response_short.short_description = "Ответ сервера"
