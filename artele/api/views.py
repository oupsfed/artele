from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from users.models import User
from .serializers import UserSerializer, FoodSerializer, MessageSerializer, CartSerializer
from food.models import Food, Cart
from core.models import Message


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'telegram_chat_id'


class FoodViewSet(viewsets.ModelViewSet):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    @action(
        methods=['POST'],
        detail=True,
        url_path='add',
    )
    def add_to_cart(self, request, pk):
        cart = Cart.objects.get(pk=pk)
        cart.amount += 1
        cart.save()
        serializer = self.serializer_class(data=cart)
        serializer.is_valid()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['POST'],
        detail=True,
        url_path='delete',
    )
    def delete_from_cart(self, request, pk):
        cart = Cart.objects.get(pk=pk)
        cart.amount -= 1
        cart.save()
        if cart.amount == 0:
            cart.delete()

        return Response('Успешно удалено', status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        user = get_object_or_404(User, telegram_chat_id=request.data['user'])
        food = get_object_or_404(Food, pk=request.data['food'])
        if Cart.objects.filter(user=user, food=food).exists():
            data = Cart.objects.filter(user=user, food=food).get()
            data.amount += 1
            data.save()
        else:
            data = Cart.objects.create(user=user,
                                       food=food)
        serializer = CartSerializer(data=data)
        serializer.is_valid()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk):
        cart = Cart.objects.filter(user__telegram_chat_id=pk)
        serializer = CartSerializer(data=cart, many=True)
        serializer.is_valid()
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    lookup_field = 'command'
