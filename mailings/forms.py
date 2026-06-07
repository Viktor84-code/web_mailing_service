from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Mailing


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        first_sent_at = cleaned_data.get('first_sent_at')
        end_at = cleaned_data.get('end_at')

        if first_sent_at and end_at:
            if first_sent_at >= end_at:
                raise ValidationError('Дата начала должна быть раньше даты окончания.')
            if first_sent_at < timezone.now():
                raise ValidationError('Дата начала не может быть в прошлом.')
        return cleaned_data
