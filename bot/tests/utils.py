FOOD_DATA = {
        "count": 8,
        "page": 2,
        "next": "http://127.0.0.1:8000/api/food/?page=3",
        "previous": "http://127.0.0.1:8000/api/food/?page=1",
        "results": [
            {
                "id": 1,
                "name": "test",
                "image": None,
                "description": "test",
                "weight": 1,
                "price": 1
            },
            {
                "id": 2,
                "name": "2",
                "image": None,
                "description": "test2",
                "weight": 12,
                "price": 12
            },
            {
                "id": 4,
                "name": "1",
                "image": "http://127.0.0.1:8000/media/temp_NPZU1dv.jpg",
                "description": "1",
                "weight": 1,
                "price": 1
            }
        ]
    }


def check_paginator(paginators_btns, page):
    callback_prev = paginators_btns[0].callback_data.split(':')
    callback_next = paginators_btns[1].callback_data.split(':')
    assert paginators_btns[0].text == '⬅️', (
        'Кнопка назад не существует или имеет неправильный текст'
    )
    assert paginators_btns[1].text == '➡️', (
        'Кнопка вперед не существует или имеет неправильный текст'
    )
    assert 'get_all' in callback_prev[1], (
        'кнопка назад возвращает неправильную callback_data_action'
    )
    assert 'get_all' in callback_next[1], (
        'кнопка вперед возвращает неправильную callback_data_action'
    )
    assert int(callback_prev[2]) == page - 1, (
        'кнопка назад возвращает неправильную callback_data_page'
    )
    assert int(callback_next[2]) == page + 1, (
        'кнопка вперед возвращает неправильную callback_data_page'
    )
