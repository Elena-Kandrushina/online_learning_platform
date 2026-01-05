from rest_framework.permissions import IsAuthenticated
from lms.models import Course, Lesson
from lms.serializers import CourseSerializer, LessonSerializer
from rest_framework import viewsets, generics
from users.permissions import IsNotModerator, IsOwnerOrModerator


class CourseViewSet(viewsets.ModelViewSet):
    """ Простой ViewSet с проверкой прав модераторов """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer

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

    def perform_create(self, serializer):
        """При создании курса устанавливаем владельца"""
        serializer.save(owner=self.request.user)



class LessonListCreateAPIView(generics.ListCreateAPIView):
    """Получение списка уроков и создание нового"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        """Разные права для разных методов"""
        if self.request.method == 'GET':

            permission_classes = [IsAuthenticated]
        else:

            permission_classes = [IsAuthenticated & IsNotModerator]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """При создании урока устанавливаем владельца"""
        serializer.save(owner=self.request.user)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """Получение одного урока"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

class LessonUpdateAPIView(generics.UpdateAPIView):
    """Обновление урока"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated & IsOwnerOrModerator]

class LessonDestroyAPIView(generics.DestroyAPIView):
    """Удаление урока"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated & IsNotModerator]
