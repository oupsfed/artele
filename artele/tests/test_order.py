import os
from http import HTTPStatus

import pytest
from dotenv import load_dotenv

from tests.utils import (check_pagination, create_carts, create_foods,
                         create_single_order, create_users)

pytestmark = pytest.mark.django_db

load_dotenv()

URL = os.getenv('URL')


@pytest.mark.django_db(transaction=True)
class TestOrderAPI:

    def test_01_order_get(self, client):
        response = client.get('/api/order/')
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            'Эндпоинт `/api/order/` не найден.'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            '`/api/order/` возвращает ответ со статусом 200.'
        )

    def test_02_order_create(self, client):
        url = '/api/order/'
        order_count = 0
        users, foods, carts = create_carts(client)

        assert_msg = (
            f'Если POST-запрос `{url}` '
            'содержит некорректные данные - должен вернуться ответ со '
            'статусом 400.'
        )
        data = {}
        response = client.post(url, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, assert_msg

        invalid_data = {
            'user': 'пользователь',
            'status': 'D'
        }
        response = client.post(url, data=invalid_data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, assert_msg
        post_data_1 = {
            'user': users[0]['telegram_chat_id']
        }
        response = client.post(url, data=post_data_1)
        assert response.status_code == HTTPStatus.CREATED, (
            f'Если POST-запрос к `{url}` '
            'содержит корректные данные - должен вернуться ответ со статусом '
            '201.'
        )
        assert isinstance(response.json().get('id'), int), (
            f'Проверьте, при POST-запросе администратора к `{url}` '
            'в ответе возвращаются данные созданного объекта. Сейчас поле '
            '`id` отсутствует или не является целым числом.'
        )
        order_count += 1
        response = client.post(url, data=post_data_1)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'Если заказ уже существует то нельзя создать повторный заказ'
        )
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            f'`{url}` возвращает ответ со статусом 200.'
        )
        data = response.json()
        for element in data:
            if element['user']['telegram_chat_id'] == post_data_1['user']:
                data = element
                food = element['food'][0]
        assert data.get('total_price') == 500, (
            'Проверьте, что при GET-запросе неавторизованного '
            f'пользователя к `{url}` возвращается информация о стоимости заказа '
            'поле `total_price` отсутствует или указано неверное значение.'
        )
        assert data.get('food') is not None, (
            'Проверьте, что при GET-запросе неавторизованного '
            f'пользователя к `{url}` возвращается информация о '
            f'заказанных товарах '
            'поле `food` отсутствует или указано неверное значение.'
        )
        assert food.get('amount') == 1, (
            'Проверьте, что при GET-запросе неавторизованного '
            f'пользователя к `{url}` возвращается информация о '
            f'количестве заказанных товаров '
            'поле `food__amount` отсутствует или указано неверное значение.'
        )

    def test_03_order_detail(self, client):
        order = create_single_order(client)
        response = client.get(f'/api/order/{order["id"]}/')
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            'Эндпоинт `/api/order/{order_id}/` не найден, проверьте '
            'настройки в *urls.py*.'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            '`/api/order/{order_id}/` возвращает ответ со статусом 200.'
        )
        data = response.json()
        assert isinstance(data.get('id'), int), (
            'Поле `id` отсутствует или содержит некорректное значение '
            'в ответе на GET-запрос неавторизованного пользователя к '
            '`/api/order/{order_id}/`.'
        )
        assert data.get('status') == 'IP', (
            'Поле `status` отсутствует или содержит некорректное значение '
            'в ответе на GET-запрос неавторизованного пользователя к '
            '`/api/order/{order_id}/`.'
        )
        assert data.get('total_price') == 500, (
            'Поле `total_price` отсутствует или содержит некорректное значение '
            'в ответе на GET-запрос неавторизованного пользователя к '
            '`/api/order/{order_id}/`.'
        )
        update_data = {
            'status': 'C'
        }
        response = client.patch(
            f'/api/order/{order["id"]}/', data=update_data, content_type='application/json'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что PATCH-запрос к '
            '`/api/order/{order_id}/` возвращает ответ со статусом 200.'
        )
        data = response.json()
        assert data.get('status') == update_data['status'], (
            'Проверьте, что PATCH-запрос администратора к '
            '`/api/order/{order_id}/` возвращает изменённые данные '
            'произведения. Сейчас поле `status` отсутствует в ответе или '
            'содержит некорректное значение.'
        )
        response = client.get(f'/api/order/{order["id"]}/')
        data = response.json()
        assert data.get('status') == update_data['status'], (
            'Проверьте, что PATCH-запрос администратора к '
            '`/api/order/{order_id/` может изменять значение поля '
            '`status` заказа.'
        )
        response = client.delete(f'/api/order/{order["id"]}/')
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            'Проверьте, что DELETE-запрос администратора к '
            '`/api/order/{order_id}/` возвращает ответ со статусом 405.'
        )
        response = client.get(f'/api/order/{order["id"]}/')
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            'Проверьте, что DELETE-запрос администратора к '
            '`/api/order/{order_id}/` не удаляет объект из базы.'
        )
