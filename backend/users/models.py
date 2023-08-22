from django.core import validators
from django.db import models
from django.contrib.auth.models import AbstractUser

MAX_EMAIL_LENGTH = 254
MAX_NAME_LENGTH = 150


class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        max_length=MAX_EMAIL_LENGTH,
        verbose_name='Адрес электронной почты',
    )
    username = models.CharField(
        unique=True,
        max_length=MAX_NAME_LENGTH,
        validators=[
            validators.RegexValidator(
                r'^[\w.@+-]+\Z', 'Введите правильный юзернейм.', 'invalid'
            ),
        ],
        verbose_name='Уникальный юзернейм',
    )
    first_name = models.CharField(
        max_length=MAX_NAME_LENGTH, verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=MAX_NAME_LENGTH, verbose_name='Фамилия'
    )
    password = models.CharField(
        max_length=MAX_NAME_LENGTH, verbose_name='Пароль'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'], name='unique_follow_user_author'
            ),
        ]
