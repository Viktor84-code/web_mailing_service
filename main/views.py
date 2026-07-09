"""Контроллер для главной страницы со статистикой."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers

from clients.models import Client
from mailings.models import Mailing


@cache_page(60 * 5)
@vary_on_headers("Cookie")
@login_required
def home(request):
    """Отображает главную страницу со статистикой."""
    user = request.user

    if user.is_superuser or user.groups.filter(name="Менеджер").exists():
        mailings = Mailing.objects.all()
        clients = Client.objects.all()
    else:
        mailings = Mailing.objects.filter(owner=user)
        clients = Client.objects.filter(owner=user)

    total_mailings = mailings.count()
    active_mailings = mailings.filter(status__in=["created", "started"]).count()
    completed_mailings = mailings.filter(status__in=["completed", "failed"]).count()
    unique_clients = clients.count()

    context = {
        "total_mailings": total_mailings,
        "active_mailings": active_mailings,
        "completed_mailings": completed_mailings,
        "unique_clients": unique_clients,
    }
    return render(request, "main/home.html", context)
