from http import HTTPStatus

check_name_and_slug_patterns = (
    (
        {
            'name': 'a' * 256 + 'simbols',
            'slug': 'longname'
        },
        ((
             'Проверьте, что при обработке POST-запроса к `{url}` проверяется '
             'длина поля `name`: название произведения не '
             'должно быть длиннее 256 символов.'
         ),)
    ),
    (
        {
            'name': 'longslug',
            'slug': 'l' * 50 + 'simbols'
        },
        ((
             'Проверьте, что при обработке POST-запроса к `{url}` проверяется '
             'длина поля `slug`: его содержимое не должно быть длиннее 50 '
             'символов.'
         ),)
    ),
    (
        {
            'name': 'brokenslug',
            'slug': ':-)'
        },
        ((
             'Проверьте, что при обработке POST-запроса к `{url}` содержание '
             'поля `slug` проверяется на соответствие паттерну, указанному в '
             'спецификации: ^[-a-zA-Z0-9_]+$'
         ),)
    )
)
invalid_data_for_username_and_email_fields = [
    (
        {
            'email': ('a' * 244) + '@yamdb.fake',
            'username': 'valid-username'
        },
        ((
             'Проверьте, что при обработке {request_method}-запроса к `{url}` '
             'проверяется длина поля `email`: его содержимое не должно быть '
             'длиннее 254 символа.'
         ),)
    ),
    (
        {
            'email': 'valid-email@yamdb.fake',
            'username': ('a' * 151)
        },
        ((
             'Проверьте, что при обработке {request_method}-запроса к `{url}` '
             'проверяется длина поля `username`: его содержимое не должно быть '
             'длиннее 150 символов.'
         ),)
    ),
    (
        {
            'email': 'valid-email@yamdb.fake',
            'username': '|-|aTa|_|_|a'
        },
        ((
             'Проверьте, что при обработке {request_method}-запроса к `{url}` '
             'содержание поля `username` проверяется на соответствие '
             'паттерну, указанному в спецификации: ^[\\w.@+-]+\\z'
         ),)
    )
]
invalid_data_for_user_patch_and_creation = (
    invalid_data_for_username_and_email_fields.copy()
)
invalid_data_for_user_patch_and_creation.extend([
    (
        {
            'email': 'valid-email@yamdb.fake',
            'username': 'validname',
            'first_name': 'toolong' + 'g' * 144
        },
        ((
             'Проверьте, что при обработке POST-запроса к `{url}` '
             'проверяется длина поля `first_name`: его содержимое не должно '
             'быть длиннее 150 символов.'
         ),)
    ),
    (
        {
            'email': 'valid-email@yamdb.fake',
            'username': 'validname',
            'last_name': 'toolong' + 'g' * 144
        },
        ((
             'Проверьте, что при обработке POST-запроса к `{url}` '
             'проверяется длина поля `last_name`: его содержимое не должно '
             'быть длиннее 150 символов.'
         ),)
    )
])


def check_pagination(url, respons_data, expected_count, post_data=None):
    expected_keys = ('count', 'next', 'previous', 'results')
    for key in expected_keys:
        assert key in respons_data, (
            f'Проверьте, что для эндпоинта `{url}` настроена '
            f'пагинация и ответ на GET-запрос содержит ключ {key}.'
        )
    assert respons_data['count'] == expected_count, (
        f'Проверьте, что для эндпоинта `{url}` настроена '
        f'пагинация. Сейчас ключ `count` содержит некорректное значение.'
    )
    assert isinstance(respons_data['results'], list), (
        f'Проверьте, что для эндпоинта `{url}` настроена '
        'пагинация. Значением ключа `results` должен быть список.'
    )
    assert len(respons_data['results']) == expected_count, (
        f'Проверьте, что для эндпоинта `{url}` настроена пагинация. Сейчас '
        'ключ `results` содержит некорректное количество элементов.'
    )
    if post_data:
        assert post_data in respons_data['results'], (
            f'Проверьте, что для эндпоинта `{url}` настроена пагинация. '
            'Значение параметра `results` отсутствует или содержит '
            'некорректную информацию о существующем объекте.'
        )


def check_permissions(client, url, data, user_role, objects,
                      expected_status):
    sufix = 'slug' if 'slug' in objects[0] else 'id'

    response = client.post(url, data=data)
    assert response.status_code == expected_status, (
        f'Проверьте, что POST-запрос {user_role} к `{url}` возвращает ответ '
        f'со статусом {expected_status}.'
    )
    response = client.patch(f'{url}{objects[0][sufix]}/', data=data)
    assert response.status_code == expected_status, (
        f'Проверьте, что PATCH-запрос {user_role} к `{url}<{sufix}>/` '
        f'возвращает ответ со статусом {expected_status}.'
    )
    response = client.delete(f'{url}{objects[0][sufix]}/')
    assert response.status_code == expected_status, (
        f'Проверьте, что DELETE-запрос {user_role} к `{url}<{sufix}>/` '
        f'возвращает ответ со статусом {expected_status}'
    )


def create_single_review(client, title_id, text, score):
    data = {'text': text, 'score': score}
    response = client.post(
        f'/api/v1/titles/{title_id}/reviews/', data=data
    )
    assert response.status_code == HTTPStatus.CREATED, (
        'Если POST-запрос авторизованного пользователя к '
        '`/api/v1/titles/{title_id}/reviews/` содержит корректные данные - '
        'должен вернуться ответ со статусом 201.'
    )
    return response


def create_single_cart(client, food_id, user_id):
    data = {'user': user_id,
            'food': food_id}
    response = client.post(
        f'/api/cart/',
        data=data
    )
    assert response.status_code == HTTPStatus.CREATED, (
        'Если POST-запрос авторизованного пользователя к '
        '`/api/cart/` содержит '
        'корректные данные - должен вернуться ответ со статусом 201.'
    )
    return response


def create_categories(admin_client):
    data1 = {
        'name': 'Фильм',
        'slug': 'films'
    }
    response = admin_client.post('/api/v1/categories/', data=data1)
    assert response.status_code == HTTPStatus.CREATED, (
        'Если POST-запрос администратора к `/api/v1/categories/` '
        'содержит корректные данные - должен вернуться ответ со статусом 201.'
    )
    data2 = {
        'name': 'Книги',
        'slug': 'books'
    }
    admin_client.post('/api/v1/categories/', data=data2)
    return [data1, data2]


def create_users(client):
    url = '/api/users/'
    result = []
    data = {
        'telegram_chat_id': 1,
        'first_name': 'Олег',
        'last_name': 'Работяга',
        'username': 'oleg',
    }
    result.append(data)
    response = client.post(url, data=data)
    assert response.status_code == HTTPStatus.CREATED, (
        'Если POST-запрос к `/api/users/` содержит '
        'корректные данные - должен вернуться ответ со статусом 201.'
    )
    data = {
        'telegram_chat_id': 2,
    }
    result.append(data)
    response = client.post(url, data=data)
    assert response.status_code == HTTPStatus.CREATED, (
        'Если POST-запрос к `/api/users/` содержит '
        'корректные данные - должен вернуться ответ со статусом 201.'
    )
    data = {
        'telegram_chat_id': 3,
    }
    result.append(data)
    client.post(url, data=data)
    return result


def create_foods(client):
    result = []
    data = {
        'name': 'Суп',
        'weight': 100,
        'price': 200,
        'description': 'Вкусный суп',
        'image': 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAA'
                 'AAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII='
    }
    response = client.post('/api/food/', data=data)
    assert response.status_code == HTTPStatus.CREATED, (
        'Если POST-запрос к `/api/food/` содержит '
        'корректные данные - должен вернуться ответ со статусом 201.'
    )
    data['id'] = response.json()['id']
    result.append(data)
    data = {
        'name': 'Борщ',
        'weight': 200,
        'price': 300,
        'description': 'Вкусный борщ',
        'image': 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAA'
                 'AC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII='
    }
    response = client.post('/api/food/', data=data)
    data['id'] = response.json()['id']
    result.append(data)
    return result


def create_carts(client):
    foods = create_foods(client)
    users = create_users(client)
    result = []
    for food in foods:
        response = create_single_cart(
            client=client,
            user_id=users[0]['telegram_chat_id'],
            food_id=food['id']
        )
        result.append(response.json())
    return users, foods, result


def create_single_order(client):
    users, foods, carts = create_carts(client)
    url = '/api/order/'
    post_data_1 = {
        'user': users[0]['telegram_chat_id']
    }
    response = client.post(url, data=post_data_1)
    return response.json()


def check_fields(obj_type, url_pattern, obj, expected_data, detail=False):
    obj_types = {
        'comment': 'комментария(ев) к отзыву',
        'review': 'отзыва(ов)'
    }
    results_in_msg = ' в ключе `results`'
    if detail:
        results_in_msg = ''
    for field in expected_data:
        assert obj.get(field) == expected_data[field], (
            f'Проверьте, что ответ на GET-запрос к `{url_pattern}` содержит '
            f'данные {obj_types[obj_type]}{results_in_msg}. Поле '
            f'`{field}` не найдено или содержит некорректные данные.'
        )
    assert obj.get('pub_date'), (
        f'Проверьте, что ответ на GET-запрос к `{url_pattern}` содержит '
        f'данные {obj_types[obj_type]}{results_in_msg}. Поле `pub_date` не '
        'найдено.'
    )
    assert isinstance(obj.get('id'), int), (
        f'Проверьте, что ответ на GET-запрос к `{url_pattern}` содержит '
        f'данные {obj_types[obj_type]}{results_in_msg}. Поле `id` не '
        'найдено или не является целым числом.'
    )
