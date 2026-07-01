"""Контроллеры (CBV) для управления сообщениями."""

from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Message


class MessageListView(LoginRequiredMixin, ListView):
    """Отображает список всех сообщений."""

    model = Message
    template_name = "email_messages/message_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        if self.request.user.groups.filter(name='Менеджер').exists():
            return Message.objects.all()
        return Message.objects.filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    """Создаёт новое сообщение."""

    model = Message
    fields = ["subject", "body"]
    template_name = "email_messages/message_form.html"
    success_url = reverse_lazy("email_messages:list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(UpdateView):
    """Редактирует существующее сообщение."""

    model = Message
    fields = ["subject", "body"]
    template_name = "email_messages/message_form.html"
    success_url = reverse_lazy("email_messages:list")


class MessageDeleteView(DeleteView):
    """Удаляет сообщение."""

    model = Message
    template_name = "email_messages/message_confirm_delete.html"
    success_url = reverse_lazy("email_messages:list")


class MessageDetailView(LoginRequiredMixin, DetailView):
    """Отображает детальную страницу сообщения."""

    model = Message
    template_name = "email_messages/message_detail.html"
    context_object_name = "message"
