from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from users.models import User


@shared_task
def deactivate_inactive_users():
    """Фоновая задача для блокировки пользователей, которые не заходили в систему более месяца"""
    try:

        thirty_days_ago = timezone.now() - timedelta(days=30)
        inactive_users = User.objects.filter(
            is_active=True,
            last_login__lt=thirty_days_ago
        )

        count = inactive_users.update(is_active=False)

        return {'message': f'Заблокировано {count} неактивных пользователей'}

    except Exception as e:
        return {
            'error': str(e)
        }
