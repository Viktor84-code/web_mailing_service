"""Контроллеры (CBV) для управления клиентами."""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import ClientForm
from .models import Client


class OwnerOrManagerMixin(UserPassesTestMixin):
    """Миксин для проверки прав: владелец или менеджер."""

    def test_func(self):
        obj = self.get_object()
        user = self.request.user
        if user.is_superuser:
            return True
        if user.groups.filter(name="Менеджер").exists():
            return True
        return obj.owner == user


class OwnerOnlyMixin(UserPassesTestMixin):
    """Миксин для проверки прав: только владелец (менеджеры не могут)."""

    def test_func(self):
        obj = self.get_object()
        user = self.request.user
        if user.is_superuser:
            return True
        if user.groups.filter(name="Менеджер").exists():
            return False  # Менеджеры НЕ могут
        return obj.owner == user


class ClientListView(LoginRequiredMixin, ListView):
    """Отображает список всех клиентов."""

    model = Client
    template_name = "clients/client_list.html"
    context_object_name = "clients"

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name="Менеджер").exists():
            return Client.objects.all()
        return Client.objects.filter(owner=user)


class ClientCreateView(LoginRequiredMixin, CreateView):
    """Создаёт нового клиента."""

    model = Client
    fields = ["email", "full_name", "comment"]
    template_name = "clients/client_form.html"
    success_url = reverse_lazy("clients:list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, OwnerOnlyMixin, UpdateView):
    """Редактирует существующего клиента."""

    model = Client
    form_class = ClientForm
    template_name = "clients/client_form.html"
    success_url = reverse_lazy("clients:list")


class ClientDeleteView(LoginRequiredMixin, OwnerOnlyMixin, DeleteView):
    """Удаляет клиента."""

    model = Client
    template_name = "clients/client_confirm_delete.html"
    success_url = reverse_lazy("clients:list")
