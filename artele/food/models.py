from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Food(models.Model):
    name = models.CharField(max_length=150)
    image = models.ImageField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    weight = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.PositiveIntegerField(validators=[MinValueValidator(1)])


class Cart(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='cart')
    food = models.ForeignKey(Food,
                             on_delete=models.CASCADE,
                             related_name='cart')
    amount = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)


class Order(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='order')
    food = models.ForeignKey(Food,
                             on_delete=models.CASCADE,
                             related_name='order')
    amount = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
    status = models.CharField(max_length=256,
                              choices=[('IP', 'in_progress'),
                                       ('D', 'done'),
                                       ('C', 'cancelled')],
                              default='IP')
