"""Контроллеры (CBV) для управления клиентами."""

from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .models import Client


class ClientListView(ListView):
    """Отображает список всех клиентов."""

    model = Client
    template_name = "clients/client_list.html"
    context_object_name = "clients"


class ClientCreateView(CreateView):
    """Создаёт нового клиента."""

    model = Client
    fields = ["email", "full_name", "comment"]
    template_name = "clients/client_form.html"
    success_url = reverse_lazy("clients:list")


class ClientUpdateView(UpdateView):
    """Редактирует существующего клиента."""

    model = Client
    fields = ["email", "full_name", "comment"]
    template_name = "clients/client_form.html"
    success_url = reverse_lazy("clients:list")


class ClientDeleteView(DeleteView):
    """Удаляет клиента."""

    model = Client
    template_name = "clients/client_confirm_delete.html"
    success_url = reverse_lazy("clients:list")
