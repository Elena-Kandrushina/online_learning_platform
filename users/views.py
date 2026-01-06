from rest_framework import viewsets
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


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet для платежей с фильтрацией"""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["course", "lesson", "payment_method"]
    ordering_fields = ["payment_date", "amount"]
    ordering = ["-payment_date"]

    def get_queryset(self):
        """Фильтрация платежей по пользователю"""
        user = self.request.user

        if user.is_superuser or user.groups.filter(name="moderators").exists():
            return Payment.objects.all()
        return Payment.objects.filter(user=user)

    def perform_create(self, serializer):
        """Автоматическое назначение пользователя при создании платежа"""
        serializer.save(user=self.request.user)


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
