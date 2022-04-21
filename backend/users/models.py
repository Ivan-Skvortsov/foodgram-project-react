from django.db import models
from django.contrib.auth.models import AbstractUser


from django.core.validators import RegexValidator


username_validator = RegexValidator(
    '^[\\w.@+-]+$',
    'Username must contain only letters, numbers and symbols . @ + -'
)


class FoodgramUser(AbstractUser):
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Эл. почта'
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Имя пользователя',
        validators=[username_validator]
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия'
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя'
    )
    subscribed_to = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='subscribed_by',
        blank=True,
        verbose_name='Подписки пользователя'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']
