from rest_framework import serializers

from lms.models import Course, Lesson


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для курса"""
    class Meta:
        model = Course
        fields = ['id', 'title', 'preview', 'description']


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для урока"""
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'preview', 'description', 'video_link', 'course']
