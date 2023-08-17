import os
from http import HTTPStatus

import pytest

from dotenv import load_dotenv

from tests.utils import check_pagination

pytestmark = pytest.mark.django_db

load_dotenv()

URL = os.getenv('URL')


@pytest.mark.django_db(transaction=True)
class TestFoodAPI:

    def test_01_food_get(self, client):
        response = client.get('/api/food/')
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            'Эндпоинт `/api/food/` не найден.'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            '`/api/food/` возвращает ответ со статусом 200.'
        )

    def test_02_food_create(self, client):
        url = '/api/food/'
        food_count = 0

        assert_msg = (
            f'Если POST-запрос `{url}` '
            'содержит некорректные данные - должен вернуться ответ со '
            'статусом 400.'
        )
        data = {}
        response = client.post(url, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, assert_msg

        invalid_data = {
            'name': 'Нормально',
            'weight': 'дветыщи',
            'price': 'однатыща',
        }
        response = client.post(url, data=invalid_data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, assert_msg

        post_data_1 = {
            'name': 'Борщ',
            'weight': 200,
            'price': 100,
        }
        response = client.post(url, data=post_data_1)
        assert response.status_code == HTTPStatus.CREATED, (
            f'Если POST-запрос администратора к `{url}` '
            'содержит корректные данные - должен вернуться ответ со статусом '
            '201.'
        )
        food_count += 1

        post_data_2 = {
            'name': 'Суп',
            'weight': 100,
            'price': 200,
        }
        response = client.post(url, data=post_data_2)
        assert response.status_code == HTTPStatus.CREATED, (
            f'Если POST-запрос администратора к `{url}` '
            'содержит корректные данные - должен вернуться ответ со статусом '
            '201.'
        )
        food_count += 1
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
        check_pagination(url, data, food_count)

        expected_food_names = {post_data_1['name'], post_data_2['name']}
        food_names = {element.get('name') for element in data['results']}
        assert len(expected_food_names.intersection(food_names)) == 2, (
            f'Проверьте, что для эндпоинта `{url}` настроена пагинация. '
            'Сейчас значение параметра `results` отсутствует или содержит '
            'некорректную информацию о существующих объектах.'
        )

        for element in data['results']:
            if element['name'] == post_data_1['name']:
                food = element

        assert food.get('image') is None, (
            'Проверьте, что при GET-запросе неавторизованного '
            f'пользователя к `{url}` возвращается информация о изображении '
            'товара. Если изображения нет - значением '
            'поля `image` должено быть `None`.'
        )
        assert food.get('description') is None, (
            'Проверьте, что при GET-запросе неавторизованного '
            f'пользователя к `{url}` в ответе содержится описание '
            'товара. Если описания нет - значением '
            'поля `image` должено быть `None`.'
        )
        assert isinstance(food.get('id'), int), (
            'Проверьте, что при GET-запросе неавторизованного '
            f'пользователя к `{url}` в ответе содержатся `id` товара. '
            'Сейчас поле `id` для элементов списка `results` отсутствует или '
            'его значение не является целым числом.'
        )

        def test_03_food_detail(seld, client):
            pass
