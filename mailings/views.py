"""Контроллеры (CBV) для управления рассылками."""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from .services import MailingService
from .forms import MailingForm
from .models import Mailing
from django.contrib.auth.mixins import LoginRequiredMixin

class MailingListView(LoginRequiredMixin, ListView):
    """Отображает список всех рассылок с обновлением статусов."""

    model = Mailing
    template_name = "mailings/mailing_list.html"
    context_object_name = "mailings"

    def get_queryset(self):
        queryset = super().get_queryset()
        for mailing in queryset:
            mailing.update_status()  # ← обновляем статус у каждой рассылки
        return queryset

    def get_queryset(self):
        if self.request.user.groups.filter(name='Менеджер').exists():
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.request.user)


class MailingDetailView(LoginRequiredMixin, DetailView):
    """Отображает детальную страницу рассылки."""

    model = Mailing
    template_name = "mailings/mailing_detail.html"
    context_object_name = "mailing"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj


class MailingCreateView(CreateView):
    """Создаёт новую рассылку."""

    model = Mailing
    form_class = MailingForm
    template_name = "mailings/mailing_form.html"
    success_url = reverse_lazy("mailings:list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирует существующую рассылку."""

    model = Mailing
    form_class = MailingForm
    template_name = "mailings/mailing_form.html"
    success_url = reverse_lazy("mailings:list")


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    """Удаляет рассылку."""

    model = Mailing
    template_name = "mailings/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailings:list")


class MailingSendView(LoginRequiredMixin, View):
    """Контроллер для ручной отправки рассылки (POST-запрос)."""

    def post(self, request, pk):
        """Обрабатывает POST-запрос на отправку рассылки."""
        mailing = get_object_or_404(Mailing, pk=pk)
        try:
            mailing.send()
            messages.success(request, f"Рассылка #{pk} отправлена")
        except ValueError as e:
            messages.error(request, str(e))
        return redirect("mailings:list")
