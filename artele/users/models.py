from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    name = models.CharField(max_length=256, null=True, blank=True)
    phone_number = models.CharField(max_length=12, blank=True, null=True)
    request_for_access = models.BooleanField(default=False)
    username = models.CharField(max_length=100,
                                blank=True,
                                null=True
                                )
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    telegram_chat_id = models.IntegerField(unique=True)
    role = models.CharField(max_length=16,
                            choices={
                                ('ADMIN', 'Admin'),
                                ('USER', 'User'),
                                ('GUEST', 'Guest')
                            },
                            default='GUEST')
    USERNAME_FIELD = 'telegram_chat_id'

    def __str__(self):
        return f'{self.telegram_chat_id}'
