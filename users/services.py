import logging

from django.contrib.auth import login
from django.db.models import Count, Q

from mailings.models import Mailing

logger = logging.getLogger(__name__)


class UserService:
    """Сервис для работы с пользователями."""

    @staticmethod
    def create_user(form):
        """
        Создает нового пользователя.
        Возвращает созданного пользователя.
        """
        try:
            user = form.save()
            logger.info(f"Создан новый пользователь: { user.email } (ID: {user.id})")
            return user
        except Exception as e:
            logger.error(f"Ошибка при создании пользователя: {e}")
            raise

    @staticmethod
    def login_user(request, user):
        """
        Авторизует пользователя.
        """
        login(request, user)
        logger.info(f"Пользователь {user.email} авторизован")

    @staticmethod
    def get_profile_stats(user):
        """
        Получение статистики для профиля пользователя.
        Возвращает словарь с данными.
        """
        # Для менеджеров и суперпользователей показываем всю статистику
        if user.is_superuser or user.groups.filter(name="Менеджер").exists():
            mailings = Mailing.objects.all()
        else:
            mailings = Mailing.objects.filter(owner=user)

        # Агрегируем данные одним запросом
        stats = mailings.aggregate(
            total_mailings=Count("id"),
            sent_messages=Count("id", filter=Q(is_sent=True)),
            total_attempts=Count("attempts"),
            success_attempts=Count("attempts", filter=Q(attempts__status="success")),
        )

        total_attempts = stats["total_attempts"] or 0
        success_attempts = stats["success_attempts"] or 0

        return {
            "total_mailings": stats["total_mailings"] or 0,
            "sent_messages": stats["sent_messages"] or 0,
            "total_attempts": total_attempts,
            "success_attempts": success_attempts,
            "failed_attempts": total_attempts - success_attempts,
        }

    @staticmethod
    def get_user_mailings(user):
        """
        Возвращает рассылки пользователя с учетом прав.
        """
        if user.is_superuser or user.groups.filter(name="Менеджер").exists():
            return Mailing.objects.all().select_related("message", "owner")
        return Mailing.objects.filter(owner=user).select_related("message", "owner")
