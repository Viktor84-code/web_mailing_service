from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import UserRegisterForm
from .services import UserService  # <-- ИМПОРТ СЕРВИСА


def register(request):
    """Регистрация пользователя."""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # Используем сервис для регистрации
            user = UserService.register_user(request, form)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('main:home')
    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    """Профиль пользователя со статистикой."""
    # Используем сервис для получения статистики
    stats = UserService.get_profile_stats(request.user)

    context = {
        'total_mailings': stats['total_mailings'],
        'total_attempts': stats['total_attempts'],
        'success_attempts': stats['success_attempts'],
        'failed_attempts': stats['failed_attempts'],
        'sent_messages': stats['sent_messages'],
    }

    return render(request, 'users/profile.html', context)
