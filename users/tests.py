from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserRegistrationTest(TestCase):
    """Тесты регистрации пользователя."""

    def setUp(self):
        self.client = Client()
        self.register_url = reverse("users:register")

    def test_register_view_get(self):
        """GET запрос на регистрацию."""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/register.html")

    def test_register_view_post_valid(self):
        """POST запрос с валидными данными."""
        data = {
            "email": "test@test.com",
            "password1": "TestPass123!",
            "password2": "TestPass123!",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after login
        self.assertTrue(User.objects.filter(email="test@test.com").exists())

    def test_register_view_post_invalid(self):
        """POST запрос с невалидными данными."""
        data = {
            "email": "test@test.com",
            "password1": "test",
            "password2": "test",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email="test@test.com").exists())


class UserProfileTest(TestCase):
    """Тесты профиля пользователя."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email="user@test.com", password="TestPass123!")
        self.profile_url = reverse("users:profile")

    def test_profile_view_requires_login(self):
        """Профиль требует авторизации."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)

    def test_profile_view_authenticated(self):
        """Профиль доступен авторизованному пользователю."""
        self.client.login(email="user@test.com", password="TestPass123!")
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/profile.html")


class UserListViewTest(TestCase):
    """Тесты списка пользователей для менеджера."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email="user@test.com", password="TestPass123!")
        self.manager = User.objects.create_user(email="manager@test.com", password="TestPass123!")
        group, _ = Group.objects.get_or_create(name="Менеджер")
        self.manager.groups.add(group)

        self.user_list_url = reverse("users:user_list")

    def test_user_list_requires_login(self):
        """Список пользователей требует авторизации."""
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, 302)

    def test_user_list_requires_manager(self):
        """Список пользователей доступен только менеджеру."""
        self.client.login(email="user@test.com", password="TestPass123!")
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, 302)

    def test_user_list_manager_access(self):
        """Менеджер видит список пользователей."""
        self.client.login(email="manager@test.com", password="TestPass123!")
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/user_list.html")


class UserToggleBlockTest(TestCase):
    """Тесты блокировки пользователя."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email="user@test.com", password="TestPass123!")
        self.manager = User.objects.create_user(email="manager@test.com", password="TestPass123!")
        group, _ = Group.objects.get_or_create(name="Менеджер")
        self.manager.groups.add(group)

        self.toggle_url = reverse("users:user_toggle_block", args=[self.user.pk])

    def test_toggle_block_requires_manager(self):
        """Блокировка доступна только менеджеру."""
        self.client.login(email="user@test.com", password="TestPass123!")
        response = self.client.post(self.toggle_url)
        self.assertEqual(response.status_code, 302)

    def test_toggle_block_manager_access(self):
        """Менеджер может блокировать пользователя."""
        self.client.login(email="manager@test.com", password="TestPass123!")
        response = self.client.post(self.toggle_url)
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_toggle_block_cannot_block_self(self):
        """Нельзя заблокировать себя."""
        toggle_self_url = reverse("users:user_toggle_block", args=[self.manager.pk])
        self.client.login(email="manager@test.com", password="TestPass123!")
        response = self.client.post(toggle_self_url)
        self.assertEqual(response.status_code, 302)
        self.manager.refresh_from_db()
        self.assertTrue(self.manager.is_active)

    def test_toggle_block_cannot_block_superuser(self):
        """Нельзя заблокировать суперпользователя."""
        superuser = User.objects.create_superuser(email="admin@test.com", password="TestPass123!")
        toggle_super_url = reverse("users:user_toggle_block", args=[superuser.pk])
        self.client.login(email="manager@test.com", password="TestPass123!")
        response = self.client.post(toggle_super_url)
        self.assertEqual(response.status_code, 302)
        superuser.refresh_from_db()
        self.assertTrue(superuser.is_active)


class UserViewsTest(TestCase):
    """Тесты для вьюх пользователей."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email="testuser@test.com", password="TestPass123!")
        self.login_url = reverse("users:login")
        self.logout_url = reverse("users:logout")
        self.profile_url = reverse("users:profile")
        self.register_url = reverse("users:register")

    def test_login_view_get(self):
        """GET запрос на вход."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/login.html")

    def test_login_view_post_valid(self):
        """POST запрос с валидными данными."""
        data = {"email": "testuser@test.com", "password": "TestPass123!"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after login

    def test_logout_view(self):
        """Выход из системы."""
        self.client.login(email="testuser@test.com", password="TestPass123!")
        response = self.client.post(self.logout_url)  # POST, а не GET
        self.assertEqual(response.status_code, 302)
