from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from lms.models import Course, Lesson, Subscription
from lms.paginators import CoursePaginator, LessonPaginator
from lms.serializers import CourseSerializer, LessonSerializer, CourseDetailSerializer
from rest_framework import viewsets, generics, status
from users.permissions import IsNotModerator, IsOwnerOrModerator
from lms.tasks import send_course_update_notification


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для курсов с проверкой прав модераторов и фильтрацией по владельцу"""

    serializer_class = CourseSerializer
    pagination_class = CoursePaginator

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия"""
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseSerializer

    def get_permissions(self):
        """Определяем права доступа для каждого действия"""
        if self.action == 'create':
            permission_classes = [IsAuthenticated & IsNotModerator]
        elif self.action == 'destroy':
            permission_classes = [IsAuthenticated & IsNotModerator]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAuthenticated & IsOwnerOrModerator]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Фильтрация курсов по владельцу"""
        user = self.request.user

        if not user.is_authenticated:
            return Course.objects.none()

        if user.is_superuser or user.groups.filter(name='moderators').exists():
            return Course.objects.all()

        return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        """При создании курса устанавливаем владельца"""
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        """При обновлении курса отправляем уведомления подписчикам"""

        instance = serializer.save()
        send_course_update_notification.delay(instance.id)
        return instance


class LessonListCreateAPIView(generics.ListCreateAPIView):
    """Получение списка уроков и создание нового с фильтрацией по владельцу"""
    serializer_class = LessonSerializer
    pagination_class = LessonPaginator

    def get_permissions(self):
        """Разные права для разных методов"""
        if self.request.method == 'GET':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated & IsNotModerator]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Фильтрация уроков по владельцу"""
        user = self.request.user

        if not user.is_authenticated:
            return Lesson.objects.none()

        if user.is_superuser or user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()

        return Lesson.objects.filter(owner=user)

    def perform_create(self, serializer):
        """При создании урока устанавливаем владельца"""
        serializer.save(owner=self.request.user)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """Получение одного урока с фильтрацией по владельцу"""
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Фильтрация уроков по владельцу"""
        user = self.request.user

        if not user.is_authenticated:
            return Lesson.objects.none()

        if user.is_superuser or user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()

        return Lesson.objects.filter(owner=user)


class LessonUpdateAPIView(generics.UpdateAPIView):
    """Обновление урока с фильтрацией по владельцу"""
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated & IsOwnerOrModerator]

    def get_queryset(self):
        """Фильтрация уроков по владельцу"""
        user = self.request.user

        if not user.is_authenticated:
            return Lesson.objects.none()

        if user.is_superuser or user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()

        return Lesson.objects.filter(owner=user)

    def perform_update(self, serializer):
        """При обновлении урока отправляем уведомления подписчикам курса"""
        instance = serializer.save()
        if instance.course:
            send_course_update_notification.delay(instance.course.id)

        return instance


class LessonDestroyAPIView(generics.DestroyAPIView):
    """Удаление урока с фильтрацией по владельцу"""
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated & IsNotModerator]

    def get_queryset(self):
        """Фильтрация уроков по владельцу"""
        user = self.request.user

        if not user.is_authenticated:
            return Lesson.objects.none()

        if user.is_superuser or user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()

        return Lesson.objects.filter(owner=user)


class SubscriptionAPIView(APIView):
    """API для управления подписками на курсы"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        course_id = request.data.get('course_id')

        if not course_id:
            return Response(
                {'error': 'course_id обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        course = get_object_or_404(Course, id=course_id)
        subscription = Subscription.objects.filter(user=user, course=course)

        if subscription.exists():

            subscription.delete()
            message = 'подписка удалена'
            subscribed = False
        else:

            Subscription.objects.create(user=user, course=course)
            message = 'подписка добавлена'
            subscribed = True

        return Response({
            'message': message,
            'subscribed': subscribed,
            'course_id': course_id,
            'course_title': course.title
        })

