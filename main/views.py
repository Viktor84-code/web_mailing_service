from django.shortcuts import render

from clients.models import Client
from mailings.models import Mailing


def home(request):
    total_mailings = Mailing.objects.count()
    active_mailings = Mailing.objects.filter(status="started").count()
    unique_clients = Client.objects.count()

    context = {
        "total_mailings": total_mailings,
        "active_mailings": active_mailings,
        "unique_clients": unique_clients,
    }
    return render(request, "main/home.html", context)
