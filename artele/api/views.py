import os
from http import HTTPStatus

from django.db.models import F, Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from fpdf import FPDF
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from food.models import Cart, Food, Order
from users.models import User

from .filters import CartFilter, OrderFilter
from .serializers import (CartCreateSerializer, FoodSerializer,
                          OrderCreateSerializer, OrderSerializer,
                          UserSerializer)


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
    serializer_class = CartCreateSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CartFilter
    pagination_class = PageNumberPagination
    pagination_class.page_size = 3

    def create(self, request, *args, **kwargs):
        if 'user' not in request.data or 'food' not in request.data:
            return Response('Недостаточно данных для создания',
                            status=status.HTTP_400_BAD_REQUEST)
        user_id = str(request.data['user'])
        food_id = str(request.data['food'])
        if not user_id.isdigit() or not food_id.isdigit():
            return Response('id еды или пользователя должны быть целыми числами',
                            status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(User, telegram_chat_id=user_id)
        food = get_object_or_404(Food, pk=food_id)
        if Cart.objects.filter(user=user, food=food).exists():
            data = Cart.objects.filter(user=user, food=food).get()
            data.amount += 1
            data.save()
        else:
            data = Cart.objects.create(user=user,
                                       food=food)
        serializer = self.get_serializer(data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        cart = self.get_object()
        cart.amount -= 1
        cart.save()
        if cart.amount == 0:
            cart.delete()
        serializer = self.get_serializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        cart = self.get_object()
        cart.amount += 1
        cart.save()
        serializer = self.get_serializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   viewsets.GenericViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = OrderFilter

    @action(
        methods=['GET'],
        detail=False,
        url_path='filter_by_food',
    )
    def filter_by_food(self, request):
        order_data = Order.objects.filter(status='IP')
        order_data = order_data.values(
            food_id=F('food__id'),
            food_name=F('food__name'),
            food_price=F('food__price'),
            weight=F('food__weight')
        ).annotate(
            amount=Sum('foodorder__amount'),
            total_weight=F('food__weight') * Sum('foodorder__amount'),
            total_price=F('food__price') * Sum('foodorder__amount'),
        )
        return Response(order_data)

    @action(
        methods=['GET'],
        detail=False,
        url_path='download',
    )
    def download(self, request):
        order_data = Order.objects.filter(status='IP')
        filtered_by_food_data = order_data.values(
            food_id=F('food__id'),
            food_name=F('food__name'),
        ).annotate(
            amount=Sum('foodorder__amount')
        )
        pdf = FPDF()
        pdf.add_page()
        font = os.path.isfile('./static/font/DejaVuSansCondensed.ttf')
        if not font:
            raise FileExistsError('Шрифт не найден')
        pdf.add_font('DejaVu', '', './static/font/DejaVuSansCondensed.ttf', uni=True)
        pdf.set_font('DejaVu', '', 18)
        pdf.cell(200, 10, txt="Список заказов", ln=1, align="C")
        pdf.cell(200, 10, txt="Всего", ln=1, align="C")

        pdf.set_font('DejaVu', '', 14)
        pdf.cell(20, 10, '№ п/п', 1, align="C")
        pdf.cell(120, 10, 'Название', 1, align="C")
        pdf.cell(40, 10, 'Количество', 1, ln=1, align="C")
        i = 0
        for food in filtered_by_food_data:
            i += 1
            pdf.cell(20, 10, f'{i}.', 1, align="C")
            pdf.cell(120, 10, food['food_name'], 1, align="C")
            pdf.cell(40, 10, f'{food["amount"]} шт.', 1, ln=1, align="C")

        pdf.set_font('DejaVu', '', 18)
        pdf.cell(200, 20, txt="По каждому покупателю", ln=1, align="C")
        pdf.set_font('DejaVu', '', 14)
        for order in order_data:
            i = 0
            pdf.cell(200, 10, txt=order.user.name, ln=1, align="C")
            pdf.cell(20, 10, '№ п/п', 1, align="C")
            pdf.cell(120, 10, 'Название', 1, align="C")
            pdf.cell(40, 10, 'Количество', 1, ln=1, align="C")
            for food_item in order.food.values(food_id=F('id'),
                                               food_name=F('name'),
                                               amount=F('foodorder__amount')):
                i += 1
                pdf.cell(20, 10, f'{i}.', 1, align="C")
                pdf.cell(120, 10, food_item["food_name"], 1, align="C")
                pdf.cell(40, 10, f'{food_item["amount"]} шт.', 1, ln=1, align="C")
        pdf.output("media/order.pdf")
        serializer = OrderSerializer(data=order_data, many=True)
        serializer.is_valid()
        return Response({
            'filtered_by_food': filtered_by_food_data,
            'filtered_by_user': serializer.data

        }, status=HTTPStatus.OK)
