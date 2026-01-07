from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from lms.models import Course, Lesson


class Command(BaseCommand):
    help = 'Создает группы пользователей с разрешениями'

    def handle(self, *args, **options):
        moderators_group, created = Group.objects.get_or_create(name='moderators')

        course_content_type = ContentType.objects.get_for_model(Course)
        lesson_content_type = ContentType.objects.get_for_model(Lesson)

        can_view_course = Permission.objects.get(
            codename='view_course',
            content_type=course_content_type
        )
        can_change_course = Permission.objects.get(
            codename='change_course',
            content_type=course_content_type
        )


        can_view_lesson = Permission.objects.get(
            codename='view_lesson',
            content_type=lesson_content_type
        )
        can_change_lesson = Permission.objects.get(
            codename='change_lesson',
            content_type=lesson_content_type
        )


        moderators_group.permissions.add(
            can_view_course,
            can_change_course,
            can_view_lesson,
            can_change_lesson
        )

        moderators_group.save()

        self.stdout.write(
            self.style.SUCCESS('Группа "moderators" успешно создана с разрешениями!')
        )
