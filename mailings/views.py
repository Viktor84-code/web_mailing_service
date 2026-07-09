"""Контроллеры (CBV) для управления рассылками."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import MailingForm
from .models import Mailing
from .services import MailingService


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
            return False
        return obj.owner == user


class MailingListView(LoginRequiredMixin, ListView):
    """Отображает список всех рассылок с обновлением статусов."""

    model = Mailing
    template_name = "mailings/mailing_list.html"
    context_object_name = "mailings"

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name="Менеджер").exists():
            queryset = Mailing.objects.all()
        else:
            queryset = Mailing.objects.filter(owner=user)

        # Обновляем статусы через сервис
        service = MailingService()
        for mailing in queryset:
            service.update_status(mailing)

        return queryset


@method_decorator(cache_page(60 * 15), name="dispatch")
class MailingDetailView(LoginRequiredMixin, OwnerOrManagerMixin, DetailView):
    """Отображает детальную страницу рассылки."""

    model = Mailing
    template_name = "mailings/mailing_detail.html"
    context_object_name = "mailing"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        service = MailingService()
        service.update_status(obj)
        return obj


class MailingCreateView(LoginRequiredMixin, CreateView):
    """Создаёт новую рассылку."""

    model = Mailing
    form_class = MailingForm
    template_name = "mailings/mailing_form.html"
    success_url = reverse_lazy("mailings:list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, OwnerOnlyMixin, UpdateView):
    """Редактирует существующую рассылку."""

    model = Mailing
    form_class = MailingForm
    template_name = "mailings/mailing_form.html"
    success_url = reverse_lazy("mailings:list")


class MailingDeleteView(LoginRequiredMixin, OwnerOrManagerMixin, DeleteView):
    """Удаляет рассылку (только владелец или менеджер)."""

    model = Mailing
    template_name = "mailings/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailings:list")


class MailingSendView(LoginRequiredMixin, OwnerOrManagerMixin, View):
    """Контроллер для ручной отправки рассылки (POST-запрос)."""

    def post(self, request, pk):
        """Обрабатывает POST-запрос на отправку рассылки."""
        mailing = get_object_or_404(Mailing, pk=pk)

        # Проверка прав через миксин
        if not self.test_func():
            messages.error(request, "У вас нет прав на отправку этой рассылки")
            return redirect("mailings:list")

        service = MailingService()
        try:
            result = service.send_mailing(mailing)
            messages.success(
                request,
                f"Рассылка #{pk} отправлена. "
                f"Успешно: {result['success_count']}, "
                f"Ошибок: {result['failed_count']}",
            )
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Ошибка при отправке: {e}")

        return redirect("mailings:list")

    def test_func(self):
        """Проверка прав для отправки."""
        mailing = get_object_or_404(Mailing, pk=self.kwargs["pk"])
        user = self.request.user
        if user.is_superuser:
            return True
        if user.groups.filter(name="Менеджер").exists():
            return True
        return mailing.owner == user
