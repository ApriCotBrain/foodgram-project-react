from django.contrib.auth.models import AbstractUser
from django.db import models


# class CustomUserManager(UserManager):
#
#     def get_by_natural_key(self, username):
#         return self.get(
#             Q(**{self.model.USERNAME_FIELD: username}) |
#             Q(**{self.model.EMAIL_FIELD: username})
#         )


class User(AbstractUser):
    ADMIN = 'admin'
    USER = 'user'
    USER_ROLES = [
        (ADMIN, 'admin'),
        (USER, 'user'),
    ]
    username = models.CharField(
        max_length=150,
        unique=True,
        db_index=True
    )
    email = models.EmailField(
        max_length=254,
        unique=True
    )
    first_name = models.CharField(
        max_length=150,
    )
    last_name = models.CharField(
        max_length=150,
    )
    password = models.CharField(
        max_length=150,
    )
    role = models.CharField(
        'Роль пользователя',
        max_length=20,
        choices=USER_ROLES,
        default=USER
    )
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=100,
        blank=True
    )
    #objects = CustomUserManager()
    is_subscribed = models.BooleanField(
        default=False
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_user(self):
        return self.role == self.USER

    @property
    def is_admin(self):
        return self.role == self.ADMIN
