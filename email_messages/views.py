from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .models import Message


class MessageListView(ListView):
    model = Message
    template_name = "email_messages/message_list.html"
    context_object_name = "messages"


class MessageCreateView(CreateView):
    model = Message
    fields = ["subject", "body"]
    template_name = "email_messages/message_form.html"
    success_url = reverse_lazy("email_messages:list")


class MessageUpdateView(UpdateView):
    model = Message
    fields = ["subject", "body"]
    template_name = "email_messages/message_form.html"
    success_url = reverse_lazy("email_messages:list")


class MessageDeleteView(DeleteView):
    model = Message
    template_name = "email_messages/message_confirm_delete.html"
    success_url = reverse_lazy("email_messages:list")


class MessageDetailView(DetailView):
    model = Message
    template_name = "email_messages/message_detail.html"
    context_object_name = "message"
