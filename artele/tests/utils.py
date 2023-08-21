from http import HTTPStatus


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
