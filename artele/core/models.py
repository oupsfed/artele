from django.db import models


class Message(models.Model):
    command = models.CharField(max_length=16)
    text = models.TextField()
    description = models.TextField(blank=True, null=True)
