from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from mailings.models import Mailing, MailingAttempt
from .forms import UserRegisterForm  # <-- ЭТА СТРОКА


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('main:home')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    user_mailings = Mailing.objects.filter(owner=request.user)
    total_attempts = MailingAttempt.objects.filter(mailing__in=user_mailings).count()
    success_attempts = MailingAttempt.objects.filter(mailing__in=user_mailings, status='success').count()
    failed_attempts = total_attempts - success_attempts
    sent_messages = Mailing.objects.filter(owner=request.user, is_sent=True).count()

    context = {
        'total_mailings': user_mailings.count(),
        'total_attempts': total_attempts,
        'success_attempts': success_attempts,
        'failed_attempts': failed_attempts,
        'sent_messages': sent_messages,
    }
    return render(request, 'users/profile.html', context)
