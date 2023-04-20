from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):

    username = models.CharField(
        max_length=150,
        unique=True,
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
    )
    first_name = models.CharField(
        max_length=150,
    )
    last_name = models.CharField(
        max_length=150,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-id']

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик')
    subscribe = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscribe',
        verbose_name='Автор рецептов')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'subscribe'],
                                    name='unique_subscribe')
        ]

    def __str__(self):
        return f'{self.user_id} {self.subscribe_id}'
