"""
Настройка административной панели для модели Client.
"""

from django.contrib import admin

from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """Настройка отображения модели Client в админке."""

    list_display = ("email", "full_name", "comment")
    search_fields = ("email", "full_name")
