import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from clients.models import Client


@pytest.mark.django_db
class TestClients:

    def test_client_creation(self):
        client = Client.objects.create(email="test@example.com", full_name="Test User", comment="Test comment")
        assert client.email == "test@example.com"
        assert str(client) == "Test User <test@example.com>"

    def test_client_list_view(self, client):
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        Client.objects.create(email="a@a.com", full_name="A", owner=user)
        Client.objects.create(email="b@b.com", full_name="B", owner=user)
        url = reverse("clients:list")
        response = client.get(url)
        assert response.status_code == 200
        assert len(response.context["clients"]) == 2


@pytest.mark.django_db
class TestClientsViewsExtended:
    """Дополнительные тесты для вьюх клиентов"""

    def test_client_create_view_post_invalid(self, client):
        """Тест создания клиента с невалидными данными (строки 28-34)"""
        User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        # Отправляем пустые данные (невалидная форма)
        data = {
            "email": "",  # пустое поле
            "full_name": "",
            "comment": "",
        }
        response = client.post("/clients/create/", data)
        assert response.status_code == 200  # форма вернулась с ошибками

    def test_client_create_view_post_valid_with_owner(self, client):
        """Тест создания клиента с owner (строки 15-21)"""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        data = {
            "email": "new@test.com",
            "full_name": "New Client",
            "comment": "Test comment",
        }
        response = client.post("/clients/create/", data)
        assert response.status_code == 302  # редирект после успешного создания

        # Проверяем, что клиент создался с правильным owner
        new_client = Client.objects.get(email="new@test.com")
        assert new_client.owner == user

    def test_client_update_view_post_valid(self, client):
        """Тест обновления клиента (строки 45-48)"""
        user = User.objects.create_user(username="testuser", password="testpass")
        client_obj = Client.objects.create(
            email="test@test.com", full_name="Test Client", comment="Old comment", owner=user
        )
        client.login(username="testuser", password="testpass")

        data = {
            "email": "updated@test.com",
            "full_name": "Updated Client",
            "comment": "New comment",
        }
        response = client.post(f"/clients/{client_obj.id}/update/", data)
        assert response.status_code == 302

        # Проверяем, что данные обновились
        client_obj.refresh_from_db()
        assert client_obj.email == "updated@test.com"
        assert client_obj.full_name == "Updated Client"

    def test_client_update_view_post_invalid(self, client):
        """Тест обновления клиента с невалидными данными (строки 45-48)"""
        user = User.objects.create_user(username="testuser", password="testpass")
        client_obj = Client.objects.create(
            email="test@test.com", full_name="Test Client", comment="Old comment", owner=user
        )
        client.login(username="testuser", password="testpass")

        # Отправляем пустые данные
        data = {
            "email": "",
            "full_name": "",
            "comment": "",
        }
        response = client.post(f"/clients/{client_obj.id}/update/", data)
        assert response.status_code == 200  # форма вернулась с ошибками

    def test_client_delete_view_get(self, client):
        """Тест GET запроса на удаление (строки 60-61)"""
        user = User.objects.create_user(username="testuser", password="testpass")
        client_obj = Client.objects.create(
            email="test@test.com", full_name="Test Client", comment="Test comment", owner=user
        )
        client.login(username="testuser", password="testpass")

        response = client.get(f"/clients/{client_obj.id}/delete/")
        assert response.status_code == 200  # страница подтверждения удаления

    def test_client_delete_view_post(self, client):
        """Тест POST запроса на удаление (строки 60-61)"""
        user = User.objects.create_user(username="testuser", password="testpass")
        client_obj = Client.objects.create(
            email="test@test.com", full_name="Test Client", comment="Test comment", owner=user
        )
        client.login(username="testuser", password="testpass")

        response = client.post(f"/clients/{client_obj.id}/delete/")
        assert response.status_code == 302  # редирект после удаления

        # Проверяем, что клиент удален
        with pytest.raises(Client.DoesNotExist):
            Client.objects.get(id=client_obj.id)

    def test_client_list_view_ordering(self, client):
        """Тест сортировки списка клиентов (строки 15-21)"""
        user = User.objects.create_user(username="testuser", password="testpass")
        client.login(username="testuser", password="testpass")

        Client.objects.create(email="b@test.com", full_name="B Client", owner=user)
        Client.objects.create(email="a@test.com", full_name="A Client", owner=user)

        response = client.get("/clients/")
        assert response.status_code == 200

        # Проверяем, что клиенты отсортированы по email
        clients = response.context["clients"]
        assert clients[0].email == "a@test.com"
        assert clients[1].email == "b@test.com"
