from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import User


class UserRegisterForm(UserCreationForm):
    """Форма регистрации пользователя с дополнительной валидацией."""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Введите email"}),
        label="Email",
    )

    class Meta:
        model = User
        fields = ["email", "password1", "password2"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Введите имя пользователя"}),
        }
        labels = {
            "username": "Имя пользователя",
            "password1": "Пароль",
            "password2": "Подтверждение пароля",
        }
        help_texts = {
            "username": "Обязательное поле. Не более 150 символов.",
        }

    def __init__(self, *args, **kwargs):
        """Добавляет классы для всех полей."""
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ["email", "username"]:
                field.widget.attrs.update({"class": "form-control"})

    def clean_email(self):
        """Проверяет уникальность email."""
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким email уже существует.")
        return email

    def save(self, commit=True):
        """Сохраняет пользователя с email."""
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
