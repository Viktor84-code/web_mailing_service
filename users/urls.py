from django.contrib.auth import views as auth_views
from django.urls import path

from .views import ProfileView, RegisterView, UserListView, UserToggleBlockView

app_name = "users"

urlpatterns = [
    # Регистрация и профиль
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="users/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(template_name="registration/logged_out.html"), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    # Восстановление пароля
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(template_name="registration/password_reset_form.html"),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"),
        name="password_reset_complete",
    ),
    # Управление пользователями (только для менеджеров)
    path("list/", UserListView.as_view(), name="user_list"),
    path("<int:pk>/toggle-block/", UserToggleBlockView.as_view(), name="user_toggle_block"),
]
