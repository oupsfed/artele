from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = 'user', _('User')
        GUEST = 'guest', _('Guest')
        ADMIN = 'admin', _('Admin')

    phone_number = models.PositiveIntegerField(blank=True,
                                               null=True,
                                               verbose_name='Номер телефона')
    request_for_access = models.BooleanField(default=False,
                                             verbose_name='Заявка')
    username = models.CharField(max_length=100,
                                blank=True,
                                null=True,
                                verbose_name='Псевдоним')
    first_name = models.CharField(max_length=100,
                                  blank=True,
                                  null=True,
                                  default='Неизвестный',
                                  verbose_name='Имя')
    last_name = models.CharField(max_length=100,
                                 blank=True,
                                 null=True,
                                 default='Пользователь',
                                 verbose_name='Фамилия')
    telegram_chat_id = models.IntegerField(unique=True,
                                           verbose_name='Телеграмм id')
    role = models.CharField(max_length=16,
                            choices=Role.choices,
                            default=Role.GUEST,
                            verbose_name='Права пользователя')
    USERNAME_FIELD = 'telegram_chat_id'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
