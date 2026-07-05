from django import forms
from django.core.exceptions import ValidationError

from .models import Message


class MessageForm(forms.ModelForm):
    """Форма для создания/редактирования сообщения."""

    class Meta:
        model = Message
        fields = ["subject", "body"]
        widgets = {
            "subject": forms.TextInput(attrs={"class": "form-control", "placeholder": "Введите тему письма"}),
            "body": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Введите текст письма"}),
        }
        labels = {
            "subject": "Тема",
            "body": "Текст письма",
        }
        help_texts = {
            "subject": "Максимум 255 символов",
        }

    def clean_subject(self):
        """Валидация темы: не должна быть пустой или состоять только из пробелов."""
        subject = self.cleaned_data.get("subject")
        if subject and not subject.strip():
            raise ValidationError("Тема не может состоять только из пробелов")
        return subject

    def clean_body(self):
        """Валидация текста: не должен быть пустым."""
        body = self.cleaned_data.get("body")
        if body and not body.strip():
            raise ValidationError("Текст письма не может состоять только из пробелов")
        return body

    def clean(self):
        """Общая валидация формы."""
        cleaned_data = super().clean()
        subject = cleaned_data.get("subject")
        body = cleaned_data.get("body")

        # Проверка что оба поля заполнены
        if not subject and not body:
            raise ValidationError("Заполните хотя бы одно поле")

        return cleaned_data
