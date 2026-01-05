from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, filters
from rest_framework.filters import OrderingFilter
from users.models import Payment
from users.serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet для платежей с фильтрацией"""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['course', 'lesson', 'payment_method']
    ordering_fields = ['payment_date', 'amount']
    ordering = ['-payment_date']
