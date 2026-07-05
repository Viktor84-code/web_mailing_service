import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from email_messages.models import Message


@pytest.mark.django_db
class TestMessages:

    def test_message_creation(self):
        user = User.objects.create_user(username="testuser", password="testpass")
        message = Message.objects.create(subject="Test Subject", body="Test Body", owner=user)
        assert message.subject == "Test Subject"
        assert str(message) == "Test Subject"

    def test_message_list_view(self, client):
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        Message.objects.create(subject="A", body="A body", owner=user)
        Message.objects.create(subject="B", body="B body", owner=user)

        url = reverse("email_messages:list")
        response = client.get(url)
        assert response.status_code == 200
        assert len(response.context["messages"]) == 2
