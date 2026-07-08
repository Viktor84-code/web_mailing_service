import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from email_messages.models import Message

User = get_user_model()


@pytest.mark.django_db
class TestMessages:

    def test_message_creation(self):
        user = User.objects.create_user(email="testuser@test.com", password="testpass")
        message = Message.objects.create(subject="Test Subject", body="Test Body", owner=user)
        assert message.subject == "Test Subject"
        assert str(message) == "Test Subject"

    def test_message_list_view(self, client):
        user = User.objects.create_user(email="testuser@test.com", password="testpass")
        client.login(email="testuser@test.com", password="testpass")

        Message.objects.create(subject="A", body="A body", owner=user)
        Message.objects.create(subject="B", body="B body", owner=user)

        url = reverse("email_messages:list")
        response = client.get(url)
        assert response.status_code == 200
        assert len(response.context["messages"]) == 2
