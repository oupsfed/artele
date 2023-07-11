import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from users.models import User
from food.models import Food, Cart, Order
from core.models import Message


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
    class Meta:
        model = User
        fields = (
            'name',
            'phone_number',
            'request_for_access',
            'username',
            'first_name',
            'last_name',
            'telegram_chat_id',
            'is_staff',
            'role'
        )


class FoodSerializer(serializers.ModelSerializer):
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


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    food = FoodSerializer()

    class Meta:
        model = Order
        fields = (
            'id',
            'user',
            'food',
            'amount',
            'status'
        )
        read_only_fields = ('status',)


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = (
            'command',
            'text',
            'description',
        )
