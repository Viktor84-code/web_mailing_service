"""Контроллеры (CBV) для управления сообщениями."""

from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .models import Message


class MessageListView(ListView):
    """Отображает список всех сообщений."""

    model = Message
    template_name = "email_messages/message_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class MessageCreateView(CreateView):
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


class MessageDetailView(DetailView):
    """Отображает детальную страницу сообщения."""

    model = Message
    template_name = "email_messages/message_detail.html"
    context_object_name = "message"
