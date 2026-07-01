"""Главные URL-маршруты проекта."""

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("clients/", include("clients.urls")),
    path("", include("main.urls")),
    path("messages/", include("email_messages.urls")),
    path("mailings/", include("mailings.urls")),
    path('users/', include('users.urls')),
    path('accounts/profile/', lambda request: redirect('/')),
]
