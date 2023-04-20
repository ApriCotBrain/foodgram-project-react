from django.contrib import admin
from django.contrib.auth import get_user_model

from users.models import Subscription

User = get_user_model()


@admin.register(User)
class AdminCustomUser(admin.ModelAdmin):
    list_display = ('id',
                    'username',
                    'password',
                    'email',
                    'first_name',
                    'last_name'
                    )
    list_filter = ('username', 'email',)


@admin.register(Subscription)
class AdminSubscriptions(admin.ModelAdmin):
    list_display = ('id', 'subscribe', 'user')
