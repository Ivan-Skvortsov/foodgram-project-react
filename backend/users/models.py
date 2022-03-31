from django.db import models
from django.contrib.auth.models import AbstractUser


class FoodgramUser(AbstractUser):
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Эл. почта'
    )
    username = models.CharField(  # TODO: validation ^[\w.@+-]+\z
        max_length=150,
        unique=True,
        verbose_name='Уникальный юзернейм'
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Фамилия'
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Имя'
    )
    subscribed_to = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='subscribed_by',
        blank=True,
        verbose_name='Подписки пользователя'
    )
