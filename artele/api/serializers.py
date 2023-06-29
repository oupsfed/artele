from rest_framework import serializers

from users.models import User
from food.models import Food, Cart
from core.models import Message


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'telegram_chat_id',
            'is_staff'
        )


class FoodSerializer(serializers.ModelSerializer):
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


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = (
            'command',
            'text',
            'description',
        )
