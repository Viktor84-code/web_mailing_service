"""Формы для приложения mailings."""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Mailing


class MailingForm(forms.ModelForm):
    """Форма для создания и редактирования рассылки."""

    class Meta:
        model = Mailing
        fields = ["message", "recipients", "first_sent_at", "end_at"]
        widgets = {
            "first_sent_at": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
            "end_at": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
            "message": forms.Select(attrs={"class": "form-control"}),
            "recipients": forms.SelectMultiple(attrs={"class": "form-control"}),
        }
        labels = {
            "message": "Сообщение",
            "recipients": "Получатели",
            "first_sent_at": "Дата и время начала",
            "end_at": "Дата и время окончания",
        }
        help_texts = {
            "first_sent_at": "Укажите дату и время начала рассылки",
            "end_at": "Укажите дату и время окончания рассылки",
        }

    def __init__(self, *args, **kwargs):
        """Исключаем из выбора уже отправленные рассылки при редактировании."""
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Если рассылка уже отправлена, запрещаем редактирование
            if self.instance.is_sent:
                for field in self.fields:
                    self.fields[field].disabled = True
                self.help_texts = {"": "Рассылка уже отправлена, редактирование запрещено"}

    def clean(self):
        """Валидация дат."""
        cleaned_data = super().clean()
        first_sent_at = cleaned_data.get("first_sent_at")
        end_at = cleaned_data.get("end_at")

        # Проверка что даты заполнены
        if not first_sent_at or not end_at:
            return cleaned_data

        # Проверка что начало раньше окончания
        if first_sent_at >= end_at:
            raise ValidationError(
                "Дата начала должна быть раньше даты окончания."
            )

        return cleaned_data
