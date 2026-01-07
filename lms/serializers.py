from rest_framework import serializers

from lms.models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для урока"""

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'preview', 'description', 'video_link', 'owner']
        read_only_fields = ['id', 'owner']
        extra_kwargs = {'owner': {'read_only': True}}


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для курса"""
    class Meta:
        model = Course
        fields = ['id', 'title', 'preview', 'description', 'owner']
        read_only_fields = ['id', 'owner']
        extra_kwargs = {'owner': {'read_only': True}}


class CourseDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для курса с полем вывода количества уроков и уроков"""
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    class Meta:
        model = Course
        fields = ['id', 'title', 'preview', 'description', 'lessons_count', 'lessons']
        read_only_fields = ['id', 'owner', 'lessons_count', 'lessons']
