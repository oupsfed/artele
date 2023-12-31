import base64

from django.core.files.base import ContentFile
from django.db.models import F
from food.models import Cart, Food, FoodOrder, Order
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.models import User


class Base64ImageField(serializers.ImageField):
    """Сериализатор для изображений base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
        else:
            imgstr = data
            ext = 'jpg'
        name = 'temp'
        data = ContentFile(base64.b64decode(imgstr), name=f'{name}.{ext}')
        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор пользователей с дополнительными строками

    phone_number: int - номер телефона указанный при подаче заявки
    telegram_chat_id: int -  chat_id пользователя в телеграмм
    role: [Guest, User, Admin] - статус пользователя
    """
    class Meta:
        model = User
        fields = (
            'telegram_chat_id',
            'phone_number',
            'request_for_access',
            'username',
            'first_name',
            'last_name',
            'role'
        )


class FoodSerializer(serializers.ModelSerializer):
    """
    Сериализатор товаров

    name: str - название товара
    image: str(base64) - изображение в формате base64
    description: str -  описание товара
    weight: int - вес в граммах
    price: int - цена товара
    """
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Food
        fields = (
            'id',
            'name',
            'image',
            'description',
            'weight',
            'price'
        )


class CartSerializer(serializers.ModelSerializer):
    """
    Сериализатор корзины

    user: User - владелец корзины
    food: Food - товар в корзине
    amount: int -  количество единиц товара в корзине
    """
    user = UserSerializer()
    food = FoodSerializer()

    class Meta:
        model = Cart
        fields = (
            'id',
            'user',
            'food',
            'amount'
        )
        read_only_fields = ('amount',)


class CartCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор создания корзины

    user: int - telegram_chat_id пользователя
    food: int - id товара
    """
    user = serializers.IntegerField()
    food = serializers.IntegerField()

    class Meta:
        model = Cart
        fields = (
            'user',
            'food',
        )

    def to_representation(self, instance):
        serializer = CartSerializer(instance,
                                    context=self.context)
        return serializer.data

    def validate_user(self, value):
        if not isinstance(value, int):
            raise ValidationError(
                'id пользователя не может быть строкой')
        exist = User.objects.get(telegram_chat_id=value).exists()
        if not exist:
            raise ValidationError(
                'пользователя не существует'
            )
        return value

    def validate_food(self, value):
        if not isinstance(value, int):
            raise ValidationError(
                'id товара не может быть строкой')
        exist = Food.objects.get(pk=value).exists()
        if not exist:
            raise ValidationError(
                'Товар не существует'
            )
        return value


class OrderSerializer(serializers.ModelSerializer):
    """
    Сериализатор заказов

    user: User - владелец заказа
    food: list[Food] - список товаров в заказе
    status: [in progress, done, cancelled] -  статус заказа
    total_price: int - общая цена заказа
    """
    user = UserSerializer()
    food = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id',
            'user',
            'food',
            'status',
            'total_price'
        )
        read_only_fields = (
            'user',
            'food',
            'total_price'
        )

    def get_food(self, obj):
        return obj.food.values(
            'id',
            'name',
            'price',
            'weight',
            amount=F('foodorder__amount'),
        ).annotate(
            total_weight=F('weight') * F('foodorder__amount'),
            total_price=F('price') * F('foodorder__amount')
        )

    def get_total_price(self, obj):
        order_data = FoodOrder.objects.filter(
            order=obj
        )
        total_price = 0
        for order in order_data:
            total_price += order.food.price * order.amount
        return total_price


class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор создания заказа

    user: int - telegram_chat_id пользователя
    status: [in progress, done, cancelled] -  статус заказа
    """
    user = serializers.IntegerField()

    class Meta:
        model = Order
        fields = (
            'user',
            'status',
        )

    def validate_user(self, value):
        is_order_exist = Order.objects.filter(user__telegram_chat_id=value,
                                              status='in_progress').exists()
        if is_order_exist:
            raise ValidationError(
                'Заказ уже существует')
        return value

    def to_representation(self, instance):
        serializer = OrderSerializer(instance,
                                     context=self.context)
        return serializer.data

    def create(self, validated_data):
        user_id = validated_data.pop('user')
        user = User.objects.get(telegram_chat_id=user_id)
        cart_list = Cart.objects.filter(user=user)
        order = Order.objects.create(
            user=user
        )
        for cart in cart_list:
            FoodOrder.objects.create(
                food=cart.food,
                order=order,
                amount=cart.amount
            )
            cart.delete()
        return order

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance
