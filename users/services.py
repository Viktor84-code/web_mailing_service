from django.contrib.auth import login

from mailings.models import Mailing, MailingAttempt


class UserService:
    """Сервис для работы с пользователями"""

    @staticmethod
    def register_user(request, form):
        """
        Регистрация нового пользователя.
        Автоматически логинит после регистрации.
        """
        user = form.save()
        login(request, user)
        return user

    @staticmethod
    def get_profile_stats(user):
        """
        Получение статистики для профиля пользователя.
        Возвращает словарь с данными.
        """
        user_mailings = Mailing.objects.filter(owner=user)

        # Количество рассылок
        total_mailings = user_mailings.count()

        # Количество попыток
        total_attempts = MailingAttempt.objects.filter(
            mailing__in=user_mailings
        ).count()

        # Успешные попытки
        success_attempts = MailingAttempt.objects.filter(
            mailing__in=user_mailings,
            status='success'
        ).count()

        # Отправленные сообщения
        sent_messages = Mailing.objects.filter(
            owner=user,
            is_sent=True
        ).count()

        return {
            'total_mailings': total_mailings,
            'total_attempts': total_attempts,
            'success_attempts': success_attempts,
            'failed_attempts': total_attempts - success_attempts,
            'sent_messages': sent_messages,
        }
