import os
from http import HTTPStatus

import pytest

from dotenv import load_dotenv

from tests.utils import check_pagination, create_foods, create_users

pytestmark = pytest.mark.django_db

load_dotenv()

URL = os.getenv('URL')


@pytest.mark.django_db(transaction=True)
class TestCartAPI:

    def test_01_cart_get(self, client):
        response = client.get('/api/cart/')
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            'Эндпоинт `/api/cart/` не найден.'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            '`/api/food/` возвращает ответ со статусом 200.'
        )

    def test_02_cart_create(self, client):
        url = '/api/cart/'
        cart_count = 0
        users = create_users(client)
        foods = create_foods(client)

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
            'food': 'еда',
        }
        response = client.post(url, data=invalid_data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, assert_msg

        post_data_1 = {
            'user': users[0]['telegram_chat_id'],
            'food': foods[0]['id'],
        }
        response = client.post(url, data=post_data_1)
        assert response.status_code == HTTPStatus.CREATED, (
            f'Если POST-запрос администратора к `{url}` '
            'содержит корректные данные - должен вернуться ответ со статусом '
            '201.'
        )
        cart_count += 1

        post_data_2 = {
            'user': users[1]['telegram_chat_id'],
            'food': foods[1]['id'],
        }
        response = client.post(url, data=post_data_2)
        assert response.status_code == HTTPStatus.CREATED, (
            f'Если POST-запрос администратора к `{url}` '
            'содержит корректные данные - должен вернуться ответ со статусом '
            '201.'
        )
        cart_count += 1
        assert isinstance(response.json().get('id'), int), (
            f'Проверьте, при POST-запросе администратора к `{url}` '
            'в ответе возвращаются данные созданного объекта. Сейчас поле '
            '`id` отсутствует или не является целым числом.'
        )
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            f'`{url}` возвращает ответ со статусом 200.'
        )
        data = response.json()
        check_pagination(url, data, cart_count)

        for element in data['results']:
            if element['user']['telegram_chat_id'] == post_data_1['user']:
                user = element['user']

        assert user.get('name') is None, (
            'Проверьте, что при GET-запросе неавторизованного '
            f'пользователя к `{url}` возвращается информация о имени '
            'пользователя. Если имени нет - значением '
            'поля `name` должено быть `None`.'
        )
        assert user.get('phone_number') is None, (
            'Проверьте, что при GET-запросе неавторизованного '
            f'пользователя к `{url}` возвращается информация о номере '
            'пользователя. Если номера нет - значением '
            'поля `phone_number` должено быть `None`.'
        )
        assert user.get('request_for_access') is False, (
            'Проверьте, что при GET-запросе неавторизованного '
            f'пользователя к `{url}` возвращается информация о заявке '
            'пользователя. Если заявки нет - значением '
            'поля `request_for_access` должено быть `False`.'
        )

        assert user.get('role') == 'GUEST', (
            'Проверьте, что при GET-запросе неавторизованного '
            f'пользователя к `{url}` возвращается информация о правах '
            'пользователя. Если прав нет - значением '
            'поля `role` должено быть `GUEST`.'
        )
