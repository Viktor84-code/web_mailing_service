"""URL-маршруты для приложения mailings."""

from django.urls import path

from . import views

app_name = "mailings"

urlpatterns = [
    path("", views.MailingListView.as_view(), name="list"),
    path("create/", views.MailingCreateView.as_view(), name="create"),  # ← сначала create
    path("<int:pk>/", views.MailingDetailView.as_view(), name="detail"),
    path("<int:pk>/update/", views.MailingUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.MailingDeleteView.as_view(), name="delete"),
    path("<int:pk>/send/", views.MailingSendView.as_view(), name="send"),
]
