from django.contrib import admin
from lms.models import Course, Lesson


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):

    list_display = ('id', 'title', 'lessons_count')
    list_filter = ('title',)
    search_fields = ('title', 'description')


    def lessons_count(self, obj):
        return obj.lessons.count()

    lessons_count.short_description = 'Количество уроков'


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):


    list_display = ('id', 'title', 'course', 'video_link')
    list_filter = ('course',)
    search_fields = ('title', 'description', 'course__title')
    raw_id_fields = ('course',)

