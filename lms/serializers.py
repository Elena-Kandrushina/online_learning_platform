from rest_framework import serializers
from lms.models import Course, Lesson, Subscription
from lms.validators import YouTubeValidator


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для урока"""

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'preview', 'description', 'video_link', 'course', 'owner']
        read_only_fields = ['id', 'owner']
        extra_kwargs = {'owner': {'read_only': True}}
        validators = [
            YouTubeValidator(field='video_link')
        ]


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для курса"""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'preview', 'description', 'owner', 'is_subscribed']
        read_only_fields = ['id', 'owner']
        extra_kwargs = {'owner': {'read_only': True}}

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на курс"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user,
                course=obj
            ).exists()
        return False


class CourseDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для курса с полем вывода количества уроков и уроков"""
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на курс"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user,
                course=obj
            ).exists()
        return False

    class Meta:
        model = Course
        fields = ['id', 'title', 'preview', 'description', 'lessons_count', 'lessons', 'is_subscribed', 'owner']
        read_only_fields = ['id', 'owner', 'lessons_count', 'lessons', 'is_subscribed']
