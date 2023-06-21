from django.core.validators import MinValueValidator
from django.db import models


class Food(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    weight = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.PositiveIntegerField(validators=[MinValueValidator(1)])

