import os
from http import HTTPStatus

import pytest
from dotenv import load_dotenv

from tests.utils import check_pagination, create_foods

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

    def test_03_food_detail(self, client):
        foods = create_foods(client)
        response = client.get(f'/api/food/{foods[0]["id"]}/')
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            'Эндпоинт `/api/food/{food_id}/` не найден, проверьте '
            'настройки в *urls.py*.'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что GET-запрос неавторизованного пользователя к '
            '`/api/food/{food_id}/` возвращает ответ со статусом 200.'
        )
        data = response.json()
        assert isinstance(data.get('id'), int), (
            'Поле `id` отсутствует или содержит некорректное значение '
            'в ответе на GET-запрос неавторизованного пользователя к '
            '`/api/food/{food_id}/`.'
        )
        assert data.get('name') == foods[0]['name'], (
            'Поле `name` отсутствует или содержит некорректное значение '
            'в ответе на GET-запрос неавторизованного пользователя к '
            '`/api/food/{food_id}/`.'
        )
        assert data.get('weight') == foods[0]['weight'], (
            'Поле `weight` отсутствует или содержит некорректное значение '
            'в ответе на GET-запрос неавторизованного пользователя к '
            '`/api/food/{food_id}/`.'
        )
        assert data.get('price') == foods[0]['price'], (
            'Поле `price` отсутствует или содержит некорректное значение '
            'в ответе на GET-запрос неавторизованного пользователя к '
            '`/api/food/{food_id}/`.'
        )
        assert data.get('description') == foods[0]['description'], (
            'Поле `description` отсутствует или содержит некорректное значение '
            'в ответе на GET-запрос неавторизованного пользователя к '
            '`/api/food/{food_id}/`.'
        )
        assert 'http:' in data.get('image'), (
            'Поле `image` отсутствует или содержит некорректное значение '
            'в ответе на GET-запрос неавторизованного пользователя к '
            '`/api/food/{food_id}/`.'
        )

        update_data = {
            'name': 'Новоеназвание',
            'image': None,
            'description': 'Новоеие',
            'weight': 1000,
            'price': 500,
        }
        path = f'/api/food/{foods[0]["id"]}/'
        response = client.patch(
            path, data=update_data, content_type='application/json'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что PATCH-запрос администратора к '
            '`/food/{food_id}/` возвращает ответ со статусом 200.'
        )
        data = response.json()
        assert data.get('name') == update_data['name'], (
            'Проверьте, что PATCH-запрос администратора к '
            '`/food/{food_id}/` возвращает изменённые данные '
            'произведения. Сейчас поле `name` отсутствует в ответе или '
            'содержит некорректное значение.'
        )
        response = client.get(f'/api/food/{foods[0]["id"]}/')
        data = response.json()
        assert data.get('weight') == update_data['weight'], (
            'Проверьте, что PATCH-запрос к '
            '`/api/food/{food_id}/` может изменять значение поля '
            '`weight` товара.'
        )
        assert data.get('name') == update_data['name'], (
            'Проверьте, что PATCH-запрос к '
            '`/api/v1/titles/{title_id}/` может изменять значение поля '
            '`name` товара.'
        )
        assert data.get('price') == update_data['price'], (
            'Проверьте, что PATCH-запрос к '
            '`/api/food/{food_id}/` может изменять значение поля '
            '`price` товара.'
        )
        assert data.get('description') == update_data['description'], (
            'Проверьте, что PATCH-запрос к '
            '`/api/food/{food_id}/` может изменять значение поля '
            '`description` товара.'
        )
        assert data.get('image') is None, (
            'Проверьте, что PATCH-запрос к '
            '`/api/food/{food_id}/` может изменять значение поля '
            '`image` товара.'
        )

        response = client.delete(f'/api/food/{foods[0]["id"]}/')
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Проверьте, что DELETE-запрос администратора к '
            '`/api/foods/{title_id}/` возвращает ответ со статусом 204.'
        )
        response = client.get('/api/food/')
        test_data = response.json()['results']
        assert len(test_data) == len(foods) - 1, (
            'Проверьте, что DELETE-запрос администратора к '
            '`/api/v1/titles/{title_id}/` удаляет произведение из базы данных.'
        )

    def test_04_name_validation(self, client):
        url = '/api/food/'

        data = {
            'name': 'It`s Over 9000!' + '!' * 50,
            'price': 100,
            'weight': 50
        }
        response = client.post(url, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Убедитесь, что при обработке POST-запроса к '
            f'`{url}` проверяется длина поля `name`: название произведения '
            'не может быть длиннее 56 символов.'
        )

        data = {
            'name': 'Cуп',
            'price': 100,
            'weight': 50,
        }
        response = client.post(url, data=data)
        assert response.status_code == HTTPStatus.CREATED, (
            f'Если POST-запрос к `{url}` '
            'содержит корректные данные - должен вернуться ответ со статусом '
            '201.'
        )
        idx = response.json().get('id')
        assert idx, (
            f'Проверьте, что ответ на успешный POST-запрос к `{url}` '
            'содержит `id` созданного товара.'
        )

        response = client.patch(f'{url}{idx}/', data={
            'name': ('longname' + 'e' * 56)
        }, content_type='application/json')
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Проверьте, что при обработке PATCH-запрос администратора к '
            f'`{url}` проверяется длина поля `name`: название товара не '
            'может быть длиннее 56 символов.'
        )

    def test_05_price_validation(self, client):
        url = '/api/food/'

        data = {
            'name': 'It`s Over 9000!',
            'price': -1,
            'weight': 100
        }
        response = client.post(url, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Убедитесь, что при обработке POST-запроса к '
            f'`{url}` проверяется поле `price`: цена товара '
            'не может быть отрицательным числом.'
        )

        data = {
            'name': 'It`s Over 9000!',
            'price': 'тыща',
            'weight': 100
        }
        response = client.post(url, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Убедитесь, что при обработке POST-запроса к '
            f'`{url}` проверяется поле `price`: цена товара '
            'не может быть строкой.'
        )
        data = {
            'name': 'Cуп',
            'price': 100,
            'weight': 50,
        }
        response = client.post(url, data=data)
        assert response.status_code == HTTPStatus.CREATED, (
            f'Если POST-запрос к `{url}` '
            'содержит корректные данные - должен вернуться ответ со статусом '
            '201.'
        )
        idx = response.json().get('id')
        assert idx, (
            f'Проверьте, что ответ на успешный POST-запрос к `{url}` '
            'содержит `id` созданного товара.'
        )

        response = client.patch(f'{url}{idx}/', data={
            'price': -100
        }, content_type='application/json')
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Проверьте, что при обработке PATCH-запрос администратора к '
            f'`{url}` проверяется длина поля `price`: цена товара '
            'не может быть отрицательным числом.'
        )

        response = client.patch(f'{url}{idx}/', data={
            'price': 'asd'
        }, content_type='application/json')
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Проверьте, что при обработке PATCH-запрос администратора к '
            f'`{url}` проверяется длина поля `price`: цена товара '
            'не может быть cтрокой.'
        )

    def test_06_weight_validation(self, client):
        url = '/api/food/'

        data = {
            'name': 'It`s Over 9000!',
            'price': 100,
            'weight': -1
        }
        response = client.post(url, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Убедитесь, что при обработке POST-запроса к '
            f'`{url}` проверяется поле `weight`: вес товара '
            'не может быть отрицательным числом.'
        )

        data = {
            'name': 'It`s Over 9000!',
            'price': 100,
            'weight': 'фыв'
        }
        response = client.post(url, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Убедитесь, что при обработке POST-запроса к '
            f'`{url}` проверяется поле `weight`: вес товара '
            'не может быть строкой.'
        )
        data = {
            'name': 'Cуп',
            'price': 100,
            'weight': 50,
        }
        response = client.post(url, data=data)
        assert response.status_code == HTTPStatus.CREATED, (
            f'Если POST-запрос к `{url}` '
            'содержит корректные данные - должен вернуться ответ со статусом '
            '201.'
        )
        idx = response.json().get('id')
        assert idx, (
            f'Проверьте, что ответ на успешный POST-запрос к `{url}` '
            'содержит `id` созданного товара.'
        )

        response = client.patch(f'{url}{idx}/', data={
            'weight': -100
        }, content_type='application/json')
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Проверьте, что при обработке PATCH-запрос администратора к '
            f'`{url}` проверяется длина поля `weight`: вес товара '
            'не может быть отрицательным числом.'
        )

        response = client.patch(f'{url}{idx}/', data={
            'weight': 'asd'
        }, content_type='application/json')
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Проверьте, что при обработке PATCH-запрос администратора к '
            f'`{url}` проверяется длина поля `weight`: вес товара '
            'не может быть cтрокой.'
        )
