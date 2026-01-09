from rest_framework import viewsets, serializers
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from users.models import Payment, User
from users.permissions import IsOwnerOrModerator
from users.serializers import (
    PaymentSerializer,
    UserSerializer,
    CustomTokenObtainPairSerializer,
    UserUpdateSerializer,
    UserRetrieveSerializer,
)
from users.services import create_payment_in_stripe


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet для платежей с фильтрацией"""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["course", "lesson", "payment_method", "payment_status", "is_paid"]
    ordering_fields = ["payment_date", "amount"]
    ordering = ["-payment_date"]

    def get_queryset(self):
        """Фильтрация платежей по пользователю"""

        if getattr(self, 'swagger_fake_view', False):
            return Payment.objects.none()

        user = self.request.user

        if user.is_superuser or user.groups.filter(name="moderators").exists():
            return Payment.objects.all()

        if user.is_authenticated:
            return Payment.objects.filter(user=user)

        return Payment.objects.none()

    def perform_create(self, serializer):
        """Автоматическое назначение пользователя при создании платежа"""

        payment = serializer.save(user=self.request.user)

        if payment.payment_method == Payment.PAYMENT_METHOD_TRANSFER:
            try:
                stripe_data = create_payment_in_stripe(payment)

                payment.stripe_product_id = stripe_data['stripe_product_id']
                payment.stripe_price_id = stripe_data['stripe_price_id']
                payment.stripe_session_id = stripe_data['stripe_session_id']
                payment.stripe_payment_link = stripe_data['stripe_payment_link']
                payment.save()

            except Exception as e:
                payment.delete()
                raise serializers.ValidationError(
                    f"Ошибка при создании платежа в Stripe: {str(e)}"
                )


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для пользователей с полным CRUD"""

    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return UserSerializer
        elif self.action in ["update", "partial_update"]:
            return UserUpdateSerializer
        return UserRetrieveSerializer

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        elif self.action in ["update", "partial_update", "destroy", "retrieve"]:
            return [IsOwnerOrModerator()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name="moderators").exists():
            return User.objects.all()
        return User.objects.filter(id=user.id)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Кастомное представление для получения токенов по email"""

    serializer_class = CustomTokenObtainPairSerializer
