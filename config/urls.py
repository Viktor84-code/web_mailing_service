"""Главные URL-маршруты проекта."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("clients/", include("clients.urls")),
    path("", include("main.urls")),
    path("messages/", include("email_messages.urls")),
    path("mailings/", include("mailings.urls")),
    path("users/", include("users.urls")),
    path("accounts/", include("django.contrib.auth.urls")),  # стандартные пути для логина/выхода
]
