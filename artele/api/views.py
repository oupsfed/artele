from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from fpdf import FPDF
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from core.models import Message
from food.models import Cart, Food, Order
from users.models import User

from .serializers import (CartSerializer, FoodSerializer, MessageSerializer,
                          OrderSerializer, UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'telegram_chat_id'
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('request_for_access', 'role')


class AuthorizedUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(role='USER')
    serializer_class = UserSerializer
    pagination_class = None
    lookup_field = 'telegram_chat_id'
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('request_for_access',)


class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(role='ADMIN')
    serializer_class = UserSerializer
    pagination_class = None
    lookup_field = 'telegram_chat_id'
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('request_for_access',)


class FoodViewSet(viewsets.ModelViewSet):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('user__telegram_chat_id',
                        'food__id')
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
        detail=False,
        url_path='cancel',
    )
    def order_cancel(self, request, *args, **kwargs):
        if 'user_id' in request.data:
            user_id = request.data['user_id']
            Order.objects.filter(status='IP',
                                 user__telegram_chat_id=user_id
                                 ).update(
                status='C'
            )
        if 'user_name' in request.data:
            user_name = request.data['user_name']
            Order.objects.filter(status='IP',
                                 user__name=user_name
                                 ).update(
                status='C'
            )
        return Response('Успешно удалено', status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['POST'],
        detail=False,
        url_path='done',
    )
    def order_done(self, request, *args, **kwargs):
        user_name = request.data['user_name']
        Order.objects.filter(status='IP',
                             user__name=user_name
                             ).update(
            status='D'
        )
        return Response('Успешно выполнено', status=status.HTTP_200_OK)


class OrderListViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('status', 'user__name')

    @action(
        methods=['GET'],
        detail=False,
        url_path='download',
    )
    def download(self, request):
        order_list = Order.objects.filter(status='IP')
        user_list = {}
        food_list = {}
        for order in order_list:
            if order.user.name not in user_list:
                user_list[order.user.name] = {}
            if order.food.name not in user_list[order.user.name]:
                user_list[order.user.name][order.food.name] = 0
            user_list[order.user.name][order.food.name] += order.amount
            if order.food.name not in food_list:
                food_list[order.food.name] = 0
            food_list[order.food.name] += order.amount
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
        pdf.set_font('DejaVu', '', 18)
        pdf.cell(200, 10, txt="Список заказов", ln=1, align="C")
        pdf.cell(200, 10, txt="Всего", ln=1, align="C")

        pdf.set_font('DejaVu', '', 14)
        pdf.cell(20, 10, '№ п/п', 1, align="C")
        pdf.cell(120, 10, 'Название', 1, align="C")
        pdf.cell(40, 10, 'Количество', 1, ln=1, align="C")
        i = 0
        for name, amount in food_list.items():
            i += 1
            pdf.cell(20, 10, f'{i}.', 1, align="C")
            pdf.cell(120, 10, name, 1, align="C")
            pdf.cell(40, 10, f'{amount} шт.', 1, ln=1, align="C")

        pdf.set_font('DejaVu', '', 18)
        pdf.cell(200, 20, txt="По каждому покупателю", ln=1, align="C")
        pdf.set_font('DejaVu', '', 14)
        for user_name, food_data in user_list.items():
            i = 0
            pdf.cell(200, 10, txt=user_name, ln=1, align="C")
            pdf.cell(20, 10, '№ п/п', 1, align="C")
            pdf.cell(120, 10, 'Название', 1, align="C")
            pdf.cell(40, 10, 'Количество', 1, ln=1, align="C")
            for name, amount in food_data.items():
                i += 1
                pdf.cell(20, 10, f'{i}.', 1, align="C")
                pdf.cell(120, 10, name, 1, align="C")
                pdf.cell(40, 10, f'{amount} шт.', 1, ln=1, align="C")
        pdf.output("media/order.pdf")
        return Response({
            'by_food': food_list,
            'by_user': user_list
        })


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    lookup_field = 'command'
