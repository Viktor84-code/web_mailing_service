"""Контроллеры (CBV) для управления сообщениями."""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import MessageForm
from .models import Message


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


class MessageListView(LoginRequiredMixin, ListView):
    """Отображает список всех сообщений."""

    model = Message
    template_name = "email_messages/message_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name="Менеджер").exists():
            return Message.objects.all()
        return Message.objects.filter(owner=user)


@method_decorator(cache_page(60 * 15), name="dispatch")
class MessageDetailView(LoginRequiredMixin, OwnerOrManagerMixin, DetailView):
    """Отображает детальную страницу сообщения."""

    model = Message
    template_name = "email_messages/message_detail.html"
    context_object_name = "message"


class MessageCreateView(LoginRequiredMixin, CreateView):
    """Создаёт новое сообщение."""

    model = Message
    form_class = MessageForm
    template_name = "email_messages/message_form.html"
    success_url = reverse_lazy("email_messages:list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, OwnerOrManagerMixin, UpdateView):
    """Редактирует существующее сообщение."""

    model = Message
    form_class = MessageForm
    template_name = "email_messages/message_form.html"
    success_url = reverse_lazy("email_messages:list")


class MessageDeleteView(LoginRequiredMixin, OwnerOrManagerMixin, DeleteView):
    """Удаляет сообщение."""

    model = Message
    template_name = "email_messages/message_confirm_delete.html"
    success_url = reverse_lazy("email_messages:list")
