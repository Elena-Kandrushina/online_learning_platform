from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import User, Payment



@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = ('email', 'phone_number', 'city', 'is_staff', 'is_active')
    search_fields = ('email', 'phone_number', 'city')
    list_filter = ('is_staff', 'is_active', 'city')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('phone_number', 'city', 'avatar')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )


    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'phone_number', 'city', 'is_staff', 'is_active'),
        }),
    )

    ordering = ('email',)



@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = ('id', 'user', 'course', 'lesson', 'amount', 'payment_method', 'payment_date')
    list_filter = ('payment_method', 'payment_date', 'course')
    search_fields = ('user__email', 'course__title', 'lesson__title')
    readonly_fields = ('payment_date',)


    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'amount', 'payment_method', 'payment_date')
        }),
        ('Оплаченный контент', {
            'fields': ('course', 'lesson'),
            'description': 'Укажите либо курс, либо урок'
        }),
    )


