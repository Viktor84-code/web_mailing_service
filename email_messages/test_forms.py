import pytest
from django.contrib.auth.models import User

from email_messages.forms import MessageForm
from email_messages.models import Message


@pytest.mark.django_db
class TestMessageForm:
    def test_form_valid(self):
        form = MessageForm(data={
            'subject': 'Test Subject',
            'body': 'Test Body',
        })
        assert form.is_valid()

    def test_form_invalid_empty_subject(self):
        form = MessageForm(data={
            'subject': '',
            'body': 'Test Body',
        })
        assert not form.is_valid()
        assert 'subject' in form.errors

    def test_form_invalid_empty_body(self):
        form = MessageForm(data={
            'subject': 'Test Subject',
            'body': '',
        })
        assert not form.is_valid()
        assert 'body' in form.errors

    def test_form_save_with_owner(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        form = MessageForm(data={
            'subject': 'Test Subject',
            'body': 'Test Body',
        })
        message = form.save(commit=False)
        message.owner = user
        message.save()
        assert Message.objects.count() == 1
        assert message.subject == 'Test Subject'
        assert message.owner == user
