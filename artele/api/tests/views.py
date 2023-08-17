import json
import os

from django.test import Client, TestCase
from django.urls import reverse
from dotenv import load_dotenv
from users.models import User
from food.models import Food, Cart

from api.views import CartViewSet

load_dotenv()

URL = os.getenv('URL')
HEADERS = {'Content-type': 'application/json',
           'Content-Encoding': 'utf-8'}


class CartApiViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.path = f'{URL}api/cart/'
        cls.user = User.objects.create(
            telegram_chat_id=123
        )
        cls.food = Food.objects.create(
            name='tests-food',
            weight=1,
            price=10
        )

    def setUp(self):
        self.client = Client()

    def test_cart_get(self):
        """
        Проверяем, что при get запросе на api/cart
        получаем список всех объектов cart
        """
        user = CartApiViewsTest.user
        food = CartApiViewsTest.food
        path = CartApiViewsTest.path
        answer = self.client.get(
            path
        ).json()
        self.assertEqual(
            answer['count'], 0
        )
        Cart.objects.create(
            user=user,
            food=food
        )
        answer = self.client.get(
            path
        ).json()
        self.assertEqual(
            answer['count'], 1
        )

    def test_cart_post(self):
        """
        Проверяем, что при правильного post запроса на api/cart
        создается новый объект cart или увеличивается amount
        у существующего
        """
        user = CartApiViewsTest.user
        food = CartApiViewsTest.food
        path = CartApiViewsTest.path
        data = {
            'user': user.telegram_chat_id,
            'food': food.id
        }
        self.client.post(
            path=path,
            data=data
        )
        cart = Cart.objects.all()
        self.assertEqual(cart.count(), 1)
        self.client.post(
            path=path,
            data=data
        )
        cart = Cart.objects.all()
        self.assertEqual(cart.count(), 1)
        self.assertEqual(cart.first().amount, 2)

    def test_cart_sum(self):
        """
        Проверка, что сумма корзины считается верно
        """
        user = CartApiViewsTest.user
        food = CartApiViewsTest.food
        path = CartApiViewsTest.path
        path = f'{path}{user.telegram_chat_id}/sum/'
        Cart.objects.create(
            user=user,
            food=food
        )
        answer = self.client.get(
            path=path
        ).json()
        self.assertEqual(answer, 10)
        Cart.objects.create(
            user=user,
            food=food
        )
        answer = self.client.get(
            path=path
        ).json()
        self.assertEqual(answer, 20)

    def test_add_to_cart(self):
        """
        Проверка, функции add_to_cart
        """
        user = CartApiViewsTest.user
        food = CartApiViewsTest.food
        path = CartApiViewsTest.path
        cart = Cart.objects.create(
            user=user,
            food=food
        )
        path = f'{path}{cart.id}/add/'
        answer = self.client.post(
            path=path
        ).json()
        self.assertEqual(answer['amount'], 2)
        answer = self.client.post(
            path=path
        ).json()
        self.assertEqual(answer['amount'], 3)

    def test_remove_from_cart(self):
        """
        Проверка, функции remove_from_cart
        """
        user = CartApiViewsTest.user
        food = CartApiViewsTest.food
        path = CartApiViewsTest.path
        cart = Cart.objects.create(
            user=user,
            food=food,
            amount=2
        )
        path = f'{path}{cart.id}/delete/'
        answer = self.client.post(
            path=path
        ).json()
        self.assertEqual(answer['amount'], 1)
        answer = self.client.post(
            path=path
        ).json()
        self.assertEqual(answer['amount'], 0)
