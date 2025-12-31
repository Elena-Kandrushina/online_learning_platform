from rest_framework import serializers
from users.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для платежей"""

    user = serializers.StringRelatedField(read_only=True)
    course = serializers.StringRelatedField(read_only=True)
    lesson = serializers.StringRelatedField(read_only=True)

    payment_method_display = serializers.CharField(
        source='get_payment_method_display',
        read_only=True
    )

    class Meta:
        model = Payment
        fields = [
            'id',
            'user',
            'payment_date',
            'course',
            'lesson',
            'amount',
            'payment_method',
            'payment_method_display'
        ]
        read_only_fields = ['id', 'payment_date']
