from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from users.models import User
from .serializers import UserSerializer, FoodSerializer, MessageSerializer, CartSerializer, OrderSerializer
from food.models import Food, Cart, Order
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
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('user__telegram_chat_id',)
    pagination_class = PageNumberPagination
    pagination_class.page_size = 3

    @action(
        methods=['GET'],
        detail=True,
        url_path='sum',
    )
    def cart_sum(self, request, pk):
        user = User.objects.get(telegram_chat_id=pk)
        cart_list = Cart.objects.filter(user=user)
        cart_sum = 0
        for cart in cart_list:
            cart_sum += cart.amount * cart.food.price
        return Response(cart_sum, status=status.HTTP_200_OK)

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

    @action(
        methods=['POST'],
        detail=True,
        url_path='order',
    )
    def cart_order(self, request, pk):
        user = User.objects.get(telegram_chat_id=pk)
        is_order_exist = Order.objects.filter(user=user,
                                              status='IP').exists()
        if is_order_exist:
            return Response('У вас уже есть созданный заказ',
                            status=status.HTTP_400_BAD_REQUEST)
        cart_list = Cart.objects.filter(user=user)
        for cart in cart_list:
            Order.objects.create(
                food=cart.food,
                user=cart.user,
                amount=cart.amount
            )
            cart.delete()
        return Response('Заказ успешно создан', status=status.HTTP_201_CREATED)

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


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('status', 'user__telegram_chat_id')

    @action(
        methods=['POST'],
        detail=True,
        url_path='cancel',
    )
    def cancel_order(self, request, pk):
        user = User.objects.get(telegram_chat_id=pk)
        order_list = Order.objects.filter(user=user)
        for order_pos in order_list:
            order_pos.status = 'C'
            order_pos.save()
        return Response('Успешно удалено', status=status.HTTP_200_OK)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    lookup_field = 'command'
