import os
from http import HTTPStatus

import pytest
from dotenv import load_dotenv
from tests.utils import (check_pagination, create_carts, create_foods,
                         create_users)

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

        response = client.post(url, data=post_data_1)
        data = response.json()
        assert data['amount'] == 2, (
            'POST-запрос к `существующему объекту cart '
            'должен увеличивать amount'
        )

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

        assert user.get('first_name') == 'Олег', (
            'Проверьте, что при GET-запросе неавторизованного '
            f'пользователя к `{url}` возвращается информация о имени '
            'пользователя.'
        )
        assert user.get('last_name') == 'Работяга', (
            'Проверьте, что при GET-запросе неавторизованного '
            f'пользователя к `{url}` возвращается информация о фамилии '
            'пользователя.'
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

        assert user.get('role') == 'guest', (
            'Проверьте, что при GET-запросе неавторизованного '
            f'пользователя к `{url}` возвращается информация о правах '
            'пользователя. Если прав нет - значением '
            'поля `role` должено быть `GUEST`.'
        )

    def test_03_cart_detail(self, client):
        users, foods, carts = create_carts(client)
        url = f'/api/cart/{carts[0]["id"]}/'
        response = client.get(url)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            'Эндпоинт `/api/cart/{cart_id}/` не найден, проверьте '
            'настройки в *urls.py*.'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            '`/api/cart/{cart_id}/` возвращает ответ со статусом 200.'
        )
        data = response.json()
        assert isinstance(data.get('id'), int), (
            'Поле `id` отсутствует или содержит некорректное значение '
            'в ответе на GET-запрос неавторизованного пользователя к '
            '`/api/cart/{cart_id}/`.'
        )
        assert data.get('food')['name'] == foods[0]['name'], (
            'Поле `food` отсутствует или содержит некорректное значение '
            'в ответе на GET-запрос неавторизованного пользователя к '
            '`/api/cart/{cart_id}/`.'
        )
        assert (data.get('user')['telegram_chat_id']
                == users[0]['telegram_chat_id']), (
            'Поле `user` отсутствует или содержит некорректное значение '
            'в ответе на GET-запрос неавторизованного пользователя к '
            '`/api/cart/{cart_id}/`.'
        )
        assert data.get('amount') == 1, (
            'Поле `amount` отсутствует или содержит некорректное значение '
            'в ответе на GET-запрос неавторизованного пользователя к '
            '`/api/cart/{cart_id}/`.'
        )
        invalid_data = {
            'user': users[1]['telegram_chat_id'],
            'food': foods[1]['id']
        }
        response = client.patch(
            url, data=invalid_data, content_type='application/json'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что PATCH-запрос к '
            '`/api/cart/{cart_id}/` возвращает ответ со статусом 200.'
        )
        updated_data = response.json()
        assert updated_data.get('amount') == 2, (
            'Проверьте что PATCH-запрос к `/api/cart/cart_id/` '
            'увеличивает количество `amount` на 1'
        )
        assert updated_data.get('food')['name'] == foods[0]['name'], (
            'Проверьте что PATCH-запрос к `/api/cart/cart_id/` '
            'запрещено менять поле `user`'
        )
        assert (updated_data.get('user')['telegram_chat_id']
                == users[0]['telegram_chat_id']), (
            'Проверьте что PATCH-запрос к `/api/cart/cart_id/` '
            'запрещено менять поле `user`'
        )
        response = client.delete(url)
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что DELETE-запрос к '
            '`/api/cart/{cart_id}/` возвращает ответ со статусом 200.'
        )
        updated_data = response.json()
        assert updated_data.get('amount') == 1, (
            'Проверьте что DELETE-запрос к `/api/cart/cart_id/` '
            'уменьшает количество `amount` на 1'
        )
        response = client.delete(url)
        updated_data = response.json()
        assert updated_data.get('amount') == 0, (
            'Проверьте что DELETE-запрос к `/api/cart/cart_id/` '
            'уменьшает количество `amount` на 1'
        )
        response = client.get(url)
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            'Проверьте что при `amount` равному нулю '
            'объект cart удаляется'
        )
