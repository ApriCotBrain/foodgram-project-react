from django.contrib import admin
from users.models import User


@admin.register(User)
class AdminUser(admin.ModelAdmin):
    list_display = ('id', 'username', 'password', 'email', 'is_subscribed',
                    'first_name', 'last_name')
