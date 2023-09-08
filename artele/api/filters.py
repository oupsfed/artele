from django_filters import rest_framework as filters
from food.models import Cart, Order


class CartFilter(filters.FilterSet):
    """
    Фильтр для корзины
    user - telegram_chat_id пользователя
    food - id товара.
    """
    user = filters.CharFilter(field_name='user__telegram_chat_id')
    food = filters.CharFilter(field_name='food__id')

    class Meta:
        model = Cart
        fields = ['user', 'food']


class OrderFilter(filters.FilterSet):
    """
    Фильтр для заказов
    user - telegram_chat_id пользователя
    status - статус заказа
    """
    user = filters.CharFilter(field_name='user__telegram_chat_id')
    status = filters.CharFilter(field_name='status')

    class Meta:
        model = Order
        fields = ['user', 'status']