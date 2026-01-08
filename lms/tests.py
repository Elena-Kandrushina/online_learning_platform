from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from users.models import User
from .models import Course, Lesson, Subscription


class LessonTestCase(TestCase):
    """Тесты для CRUD операций с уроками"""

    def setUp(self):
        """Настройка тестовых данных"""

        self.user_owner = User.objects.create(
            email='owner@test.com',
            password='testpass123'
        )
        self.user_moderator = User.objects.create(
            email='moderator@test.com',
            password='testpass123'
        )
        self.user_moderator.groups.create(name='moderators')

        self.user_other = User.objects.create(
            email='other@test.com',
            password='testpass123'
        )
        self.user_superuser = User.objects.create_superuser(
            email='admin@test.com',
            password='adminpass123'
        )

        self.course = Course.objects.create(
            title='Тестовый курс',
            description='Описание тестового курса',
            owner=self.user_owner
        )

        self.lesson = Lesson.objects.create(
            title='Тестовый урок',
            description='Описание тестового урока',
            course=self.course,
            video_link='https://www.youtube.com/watch?v=test123',
            owner=self.user_owner
        )

        self.client = APIClient()

    def test_lesson_list_authenticated(self):
        """Тест получения списка уроков аутентифицированным пользователем"""
        self.client.force_authenticate(user=self.user_owner)

        response = self.client.get(reverse('lms:lesson-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Тестовый урок')

    def test_lesson_list_unauthenticated(self):
        """Тест получения списка уроков неаутентифицированным пользователем"""
        response = self.client.get(reverse('lms:lesson-list-create'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_lesson_create_owner(self):
        """Тест создания урока владельцем"""
        self.client.force_authenticate(user=self.user_owner)

        data = {
            'title': 'Новый урок',
            'description': 'Описание нового урока',
            'video_link': 'https://www.youtube.com/watch?v=new123',
            'course': self.course.id
        }

        response = self.client.post(
            reverse('lms:lesson-list-create'),
            data=data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_lesson_create_moderator_denied(self):
        """Тест создания урока модератором (должно быть запрещено)"""
        self.client.force_authenticate(user=self.user_moderator)

        data = {
            'title': 'Урок от модератора',
            'description': 'Описание',
            'video_link': 'https://www.youtube.com/watch?v=mod123',
            'course': self.course.id
        }

        response = self.client.post(
            reverse('lms:lesson-list-create'),
            data=data
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_create_invalid_youtube_link(self):
        """Тест создания урока с невалидной ссылкой (не YouTube)"""
        self.client.force_authenticate(user=self.user_owner)

        data = {
            'title': 'Урок с плохой ссылкой',
            'description': 'Описание',
            'video_link': 'https://vimeo.com/12345',
            'course': self.course.id
        }

        response = self.client.post(
            reverse('lms:lesson-list-create'),
            data=data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('video_link', response.data)

    def test_lesson_retrieve_owner(self):
        """Тест получения урока владельцем"""
        self.client.force_authenticate(user=self.user_owner)

        response = self.client.get(
            reverse('lms:lesson-retrieve', kwargs={'pk': self.lesson.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Тестовый урок')

    def test_lesson_retrieve_moderator(self):
        """Тест получения урока модератором"""
        self.client.force_authenticate(user=self.user_moderator)

        response = self.client.get(
            reverse('lms:lesson-retrieve', kwargs={'pk': self.lesson.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lesson_retrieve_other_user(self):
        """Тест получения урока другим пользователем"""
        self.client.force_authenticate(user=self.user_other)

        response = self.client.get(
            reverse('lms:lesson-retrieve', kwargs={'pk': self.lesson.id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_lesson_update_owner(self):
        """Тест обновления урока владельцем"""
        self.client.force_authenticate(user=self.user_owner)

        data = {
            'title': 'Обновленный урок',
            'description': 'Обновленное описание',
            'video_link': 'https://youtu.be/updated123',
            'course': self.course.id
        }

        response = self.client.put(
            reverse('lms:lesson-update', kwargs={'pk': self.lesson.id}),
            data=data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Обновленный урок')

    def test_lesson_update_moderator(self):
        """Тест обновления урока модератором"""
        self.client.force_authenticate(user=self.user_moderator)

        data = {
            'title': 'Урок обновлен модератором',
            'description': 'Описание',
            'video_link': 'https://www.youtube.com/watch?v=modupdate',
            'course': self.course.id
        }

        response = self.client.put(
            reverse('lms:lesson-update', kwargs={'pk': self.lesson.id}),
            data=data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lesson_update_other_user_denied(self):
        """Тест обновления урока другим пользователем (должно быть запрещено)"""
        self.client.force_authenticate(user=self.user_other)

        data = {
            'title': 'Попытка чужого обновления',
            'description': 'Описание',
            'video_link': 'https://www.youtube.com/watch?v=hack123'
        }

        response = self.client.put(
            reverse('lms:lesson-update', kwargs={'pk': self.lesson.id}),
            data=data
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_lesson_delete_owner(self):
        """Тест удаления урока владельцем"""
        self.client.force_authenticate(user=self.user_owner)

        response = self.client.delete(
            reverse('lms:lesson-destroy', kwargs={'pk': self.lesson.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_lesson_delete_moderator_denied(self):
        """Тест удаления урока модератором (должно быть запрещено)"""
        self.client.force_authenticate(user=self.user_moderator)

        response = self.client.delete(
            reverse('lms:lesson-destroy', kwargs={'pk': self.lesson.id})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_delete_superuser(self):
        """Тест удаления урока суперпользователем"""
        self.client.force_authenticate(user=self.user_superuser)

        response = self.client.delete(
            reverse('lms:lesson-destroy', kwargs={'pk': self.lesson.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)


class SubscriptionTestCase(TestCase):
    """Тесты для функционала подписки на курсы"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.user = User.objects.create(
            email='user@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create(
            email='user2@test.com',
            password='testpass123'
        )

        self.superuser = User.objects.create_superuser(
            email='super@test.com',
            password='superpass123'
        )

        self.course = Course.objects.create(
            title='Курс для подписки',
            description='Описание',
            owner=self.superuser
        )

        self.client = APIClient()

    def test_subscribe_authenticated(self):
        """Тест добавления подписки аутентифицированным пользователем"""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse('lms:subscription'),
            data={'course_id': self.course.id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'подписка добавлена')
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_unsubscribe_authenticated(self):
        """Тест удаления подписки"""

        Subscription.objects.create(user=self.user, course=self.course)

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse('lms:subscription'),
            data={'course_id': self.course.id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'подписка удалена')
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_subscribe_unauthenticated(self):
        """Тест добавления подписки неаутентифицированным пользователем"""
        response = self.client.post(
            reverse('lms:subscription'),
            data={'course_id': self.course.id}
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_subscribe_without_course_id(self):
        """Тест добавления подписки без указания course_id"""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse('lms:subscription'),
            data={}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_subscribe_to_nonexistent_course(self):
        """Тест добавления подписки на несуществующий курс"""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse('lms:subscription'),
            data={'course_id': 9999}  # Несуществующий ID
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_subscription_field_in_course_detail(self):
        """Тест наличия поля is_subscribed в детальной информации о курсе"""

        self.client.force_authenticate(user=self.superuser)

        Subscription.objects.create(user=self.superuser, course=self.course)

        response = self.client.get(
            reverse('lms:course-detail', kwargs={'pk': self.course.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('is_subscribed', response.data)
        self.assertTrue(response.data['is_subscribed'])

    def test_subscription_field_for_non_subscribed(self):
        """Тест поля is_subscribed для неподписанного пользователя"""

        self.client.force_authenticate(user=self.superuser)

        response = self.client.get(
            reverse('lms:course-detail', kwargs={'pk': self.course.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('is_subscribed', response.data)
        self.assertFalse(response.data['is_subscribed'])

    def test_subscription_field_for_non_subscribed(self):
        """Тест поля is_subscribed для неподписанного пользователя"""

        course2 = Course.objects.create(
            title='Курс для user2',
            description='Описание',
            owner=self.user2
        )

        self.client.force_authenticate(user=self.user2)

        response = self.client.get(
            reverse('lms:course-detail', kwargs={'pk': course2.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('is_subscribed', response.data)
        self.assertFalse(response.data['is_subscribed'])
