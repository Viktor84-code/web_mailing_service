"""Контроллеры (CBV) для управления клиентами."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import ClientForm
from .models import Client


class ClientListView(LoginRequiredMixin, ListView):
    """Отображает список всех клиентов."""

    model = Client
    template_name = "clients/client_list.html"
    context_object_name = "clients"

    def get_queryset(self):
        if self.request.user.groups.filter(name='Менеджер').exists():
            return Client.objects.all()  # Менеджер видит всех
        return Client.objects.filter(owner=self.request.user)


class ClientCreateView(LoginRequiredMixin, CreateView):
    """Создаёт нового клиента."""

    model = Client
    fields = ["email", "full_name", "comment"]
    template_name = "clients/client_form.html"
    success_url = reverse_lazy("clients:list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирует существующего клиента."""

    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('clients:list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if request.user.groups.filter(name='Менеджер').exists():
            raise PermissionDenied("Менеджеры не могут редактировать клиентов")
        if obj.owner != request.user:
            raise PermissionDenied("Вы не можете редактировать этот объект")
        return super().dispatch(request, *args, **kwargs)


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    """Удаляет клиента."""

    model = Client
    template_name = "clients/client_confirm_delete.html"
    success_url = reverse_lazy("clients:list")
