from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView, View

from .forms import UserRegisterForm
from .services import UserService

User = get_user_model()


class RegisterView(CreateView):
    """Регистрация пользователя."""

    form_class = UserRegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("main:home")

    def form_valid(self, form):
        # Создаем пользователя
        user = UserService.create_user(form)
        # Авторизуем
        UserService.login_user(self.request, user)
        messages.success(self.request, "Регистрация прошла успешно!")
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, TemplateView):
    """Профиль пользователя со статистикой."""

    template_name = "users/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stats = UserService.get_profile_stats(self.request.user)
        context.update(stats)
        context["user"] = self.request.user
        return context


class ManagerRequiredMixin(UserPassesTestMixin):
    """Миксин для проверки прав менеджера."""

    def test_func(self):
        return self.request.user.groups.filter(name="Менеджер").exists()

    def handle_no_permission(self):
        messages.error(self.request, "У вас нет прав для просмотра этой страницы")
        return redirect("main:home")


class UserListView(LoginRequiredMixin, ManagerRequiredMixin, ListView):
    """Список пользователей для менеджера."""

    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"
    paginate_by = 25

    def get_queryset(self):
        """Исключаем суперпользователей из списка."""
        queryset = super().get_queryset()
        return queryset.filter(is_superuser=False).order_by("email")


class UserToggleBlockView(LoginRequiredMixin, ManagerRequiredMixin, View):
    """Блокировка/разблокировка пользователя."""

    def post(self, request, pk):
        """Используем POST для безопасности."""
        user = get_object_or_404(User, pk=pk)

        if user == request.user:
            messages.error(request, "Нельзя заблокировать себя!")
            return redirect("users:user_list")

        if user.is_superuser:
            messages.error(request, "Нельзя заблокировать администратора!")
            return redirect("users:user_list")

        # Переключаем статус
        user.is_active = not user.is_active
        user.save()

        status = "заблокирован" if not user.is_active else "разблокирован"
        messages.success(request, f"Пользователь {user.username} {status}")

        return redirect("users:user_list")


class UserToggleActiveMixin:
    """Миксин для проверки активного пользователя во всех вьюхах."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_active:
            messages.error(request, "Ваш аккаунт заблокирован. Обратитесь к администратору.")
            return redirect("logout")
        return super().dispatch(request, *args, **kwargs)
