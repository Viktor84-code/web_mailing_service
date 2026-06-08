import pytest
from django.urls import reverse
from clients.models import Client

@pytest.mark.django_db
def test_client_creation():
    client = Client.objects.create(
        email="test@example.com",
        full_name="Test User",
        comment="Test comment"
    )
    assert client.email == "test@example.com"
    assert str(client) == "Test User"

@pytest.mark.django_db
def test_client_list_view(client):
    Client.objects.create(email="a@a.com", full_name="A")
    Client.objects.create(email="b@b.com", full_name="B")
    url = reverse('clients:list')
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.context['clients']) == 2

