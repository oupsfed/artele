from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Food(models.Model):
    name = models.CharField(max_length=56,
                            verbose_name='Имя')
    image = models.ImageField(blank=True,
                              null=True,
                              verbose_name='Изображение')
    description = models.TextField(blank=True,
                                   null=True,
                                   verbose_name='Описание')
    weight = models.PositiveIntegerField(validators=[MinValueValidator(1)],
                                         verbose_name='Вес в граммах')
    price = models.PositiveIntegerField(validators=[MinValueValidator(1)],
                                        verbose_name='Цена в рублях')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='cart',
                             verbose_name='Владелец')
    food = models.ForeignKey(Food,
                             on_delete=models.CASCADE,
                             related_name='cart',
                             verbose_name='Товар')
    amount = models.PositiveIntegerField(validators=[MinValueValidator(1)],
                                         default=1,
                                         verbose_name='Количество')

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        return self.user.name


class Order(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='order',
                             verbose_name='Владелец')
    food = models.ManyToManyField(Food,
                                  through='FoodOrder',
                                  verbose_name='Список товаров')
    status = models.CharField(max_length=256,
                              choices=[('IP', 'in_progress'),
                                       ('D', 'done'),
                                       ('C', 'cancelled')],
                              default='IP',
                              verbose_name='Статус заказа')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return self.user.name


class FoodOrder(models.Model):
    food = models.ForeignKey(Food,
                             on_delete=models.CASCADE,
                             verbose_name='Товар')
    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              verbose_name='Заказ')
    amount = models.PositiveIntegerField(validators=[MinValueValidator(1)],
                                         default=1,
                                         verbose_name='Количество')
