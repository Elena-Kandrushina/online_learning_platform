from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from lms.models import Course, Lesson
from users.models import Payment

User = get_user_model()


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми платежами'

    def handle(self, *args, **kwargs):

        Payment.objects.all().delete()

        users = User.objects.all()
        courses = Course.objects.all()
        lessons = Lesson.objects.all()

        if not users.exists() or not courses.exists() or not lessons.exists():
            self.stdout.write(
                self.style.ERROR('Необходимо сначала создать пользователей, курсы и уроки!')
            )
            return

        payments_data = [
            {
                'user': users[0],
                'course': courses[0] if courses else None,
                'lesson': None,
                'amount': 15000.00,
                'payment_method': Payment.PAYMENT_METHOD_TRANSFER
            },
            {
                'user': users[1 % len(users)],
                'course': None,
                'lesson': lessons[0] if lessons else None,
                'amount': 2500.00,
                'payment_method': Payment.PAYMENT_METHOD_CASH
            },
            {
                'user': users[0],
                'course': courses[1 % len(courses)] if len(courses) > 1 else courses[0],
                'lesson': None,
                'amount': 20000.00,
                'payment_method': Payment.PAYMENT_METHOD_TRANSFER
            },
            {
                'user': users[2 % len(users)],
                'course': None,
                'lesson': lessons[1 % len(lessons)] if len(lessons) > 1 else lessons[0],
                'amount': 3000.00,
                'payment_method': Payment.PAYMENT_METHOD_TRANSFER
            },
            {
                'user': users[1 % len(users)],
                'course': courses[0],
                'lesson': None,
                'amount': 15000.00,
                'payment_method': Payment.PAYMENT_METHOD_CASH
            },
        ]

        created_count = 0
        for payment_data in payments_data:
            try:
                Payment.objects.create(**payment_data)
                created_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Ошибка при создании платежа: {e}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Успешно создано {created_count} платежей')
        )
