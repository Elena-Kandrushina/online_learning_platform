from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Course, Subscription


@shared_task
def send_course_update_notification(course_id):
    """Асинхронная отправка уведомлений об обновлении курса всем подписанным пользователям"""
    try:
        course = Course.objects.get(id=course_id)

        subscriptions = Subscription.objects.filter(course=course).select_related('user')

        if not subscriptions.exists():
            return f'Нет подписчиков на курс {course.title}'

        emails = [subscription.user.email for subscription in subscriptions if subscription.user.email]

        if not emails:
            return f'Нет валидных адресов {course.title}'

        subject = f'Обновление курса: {course.title}'

        message = f'Здравствуйте! Курс {course.title} был обновлен. Проверьте и ознакомьтесь с изменениями'

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=emails,
            fail_silently=False,
        )

        return f'Уведомления успешно отправлены {len(emails)} подписчикам курса {course.title}'

    except Course.DoesNotExist:
        return f'Курса с {course_id} не существуетt'
    except Exception as e:
        return f'Error sending notifications: {str(e)}'
