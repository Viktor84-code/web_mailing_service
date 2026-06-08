import pytest
from django.urls import reverse
from email_messages.models import Message

@pytest.mark.django_db
def test_message_creation():
    message = Message.objects.create(
        subject="Test Subject",
        body="Test Body"
    )
    assert message.subject == "Test Subject"
    assert str(message) == "Test Subject"

@pytest.mark.django_db
def test_message_list_view(client):
    Message.objects.create(subject="A", body="A body")
    Message.objects.create(subject="B", body="B body")
    url = reverse('email_messages:list')
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.context['messages']) == 2
