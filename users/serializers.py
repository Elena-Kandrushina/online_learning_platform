from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from users.models import Payment, User



class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для платежей с Stripe"""

    user = serializers.StringRelatedField(read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True, allow_null=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True, allow_null=True)

    payment_method_display = serializers.CharField(
        source='get_payment_method_display',
        read_only=True
    )

    payment_status_display = serializers.CharField(
        source='get_payment_status_display',
        read_only=True
    )

    stripe_payment_link = serializers.URLField(read_only=True)

    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Payment._meta.get_field('course').remote_field.model.objects.all(),
        source='course',
        write_only=True,
        required=False,
        allow_null=True
    )

    lesson_id = serializers.PrimaryKeyRelatedField(
        queryset=Payment._meta.get_field('lesson').remote_field.model.objects.all(),
        source='lesson',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Payment
        fields = [
            'id',
            'user',
            'payment_date',
            'course',
            'course_id',
            'course_title',
            'lesson',
            'lesson_id',
            'lesson_title',
            'amount',
            'payment_method',
            'payment_method_display',
            'payment_status',
            'payment_status_display',
            'is_paid',
            'stripe_payment_link',
            'stripe_product_id',
            'stripe_price_id',
            'stripe_session_id',
        ]
        read_only_fields = [
            'id',
            'user',
            'payment_date',
            'course',
            'lesson',
            'course_title',
            'lesson_title',
            'payment_status',
            'payment_status_display',
            'is_paid',
            'stripe_payment_link',
            'stripe_product_id',
            'stripe_price_id',
            'stripe_session_id',
        ]

    def validate(self, data):
        """Валидация данных платежа"""
        course = data.get('course')
        lesson = data.get('lesson')

        if not course and not lesson:
            raise serializers.ValidationError(
                "Необходимо указать либо курс, либо урок"
            )

        if course and lesson:
            raise serializers.ValidationError(
                "Нельзя указать одновременно и курс, и урок"
            )

        payment_method = data.get('payment_method')
        amount = data.get('amount')

        if payment_method == Payment.PAYMENT_METHOD_TRANSFER:
            if not amount or amount <= 0:
                raise serializers.ValidationError(
                    "Для оплаты через Stripe сумма должна быть больше 0"
                )

        return data


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Кастомный сериализатор для получения токена по email"""


    username_field = 'email'

    def validate(self, attrs):

        email = attrs.get('email')
        password = attrs.get('password')


        user = authenticate(
            request=self.context.get('request'),
            email=email,
            password=password
        )

        if user is None:
            raise serializers.ValidationError(
                'Неверный email или пароль'
            )

        if not user.is_active:
            raise serializers.ValidationError('Учетная запись неактивна')


        data = super().validate(attrs)


        data.update({
            'user_id': user.id,
            'email': user.email,
        })

        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token


class UserPaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения платежей в профиле пользователя"""

    course_title = serializers.CharField(source='course.title', read_only=True, allow_null=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True, allow_null=True)
    payment_method_display = serializers.CharField(
        source='get_payment_method_display',
        read_only=True
    )
    payment_status_display = serializers.CharField(
        source='get_payment_status_display',
        read_only=True
    )

    class Meta:
        model = Payment
        fields = [
            'id',
            'payment_date',
            'amount',
            'payment_method',
            'payment_method_display',
            'payment_status',
            'payment_status_display',
            'is_paid',
            'course_title',
            'lesson_title',
            'stripe_payment_link'
        ]
        read_only_fields = fields

class UserSerializer(ModelSerializer):
    """Сериализатор для пользователя"""
    password = serializers.CharField(write_only=True, required=True)
    payments = UserPaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'phone_number', 'city', 'avatar', 'is_active', 'payments']
        read_only_fields = ['id', 'is_active', 'payments']

    def create(self, validated_data):
        """Создание пользователя с хешированием пароля"""

        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            phone_number=validated_data.get('phone_number'),
            city=validated_data.get('city'),
            avatar=validated_data.get('avatar'),
        )
        return user

class UserRetrieveSerializer(ModelSerializer):
    """Сериализатор для получения информации о пользователе"""
    payments = UserPaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'phone_number', 'city', 'avatar', 'is_active', 'payments']
        read_only_fields = ['id', 'email', 'is_active', 'payments']


class UserUpdateSerializer(ModelSerializer):
    """Сериализатор для обновления пользователя с ограничениями"""
    class Meta:
        model = User
        fields = ['phone_number', 'city', 'avatar']

    def update(self, instance, validated_data):
        """Обновление только разрешенных полей"""
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.city = validated_data.get('city', instance.city)
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance
