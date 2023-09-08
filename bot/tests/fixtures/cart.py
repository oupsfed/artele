from tests.fixtures.user import authorize_user

CART_LIST_PAGE_1 = {
    "count": 7,
    "page": 1,
    "next": "http://127.0.0.1:8000/api/cart/?page=2&user=746696354",
    "previous": None,
    "results": [
        {
            "id": 10,
            "user": authorize_user,
            "food": {
                "id": 1,
                "name": "t23",
                "image": None,
                "description": "desc",
                "weight": 10,
                "price": 50
            },
            "amount": 3
        },
        {
            "id": 11,
            "user": authorize_user,
            "food": {
                "id": 2,
                "name": "321",
                "image": "http://127.0.0.1:8000/media/temp_zJ0biPi.jpg",
                "description": "31",
                "weight": 1,
                "price": 2
            },
            "amount": 7
        },
        {
            "id": 12,
            "user": authorize_user,
            "food": {
                "id": 3,
                "name": "111",
                "image": "http://127.0.0.1:8000/media/temp_tQ7l0PY.jpg",
                "description": "222",
                "weight": 333,
                "price": 444
            },
            "amount": 4
        }
    ]
}

CART_LIST_PAGE_2 = {
    "count": 6,
    "page": 2,
    "next": "http://127.0.0.1:8000/api/cart/?page=3&user=746696354",
    "previous": "http://127.0.0.1:8000/api/cart/?user=746696354",
    "results": [
        {
            "id": 13,
            "user": authorize_user,
            "food": {
                "id": 4,
                "name": "test",
                "image": "http://127.0.0.1:8000/media/temp_uRSK6Uw.jpg",
                "description": "123",
                "weight": 321,
                "price": 321
            },
            "amount": 4
        },
        {
            "id": 15,
            "user": authorize_user,
            "food": {
                "id": 6,
                "name": "test3",
                "image": "http://127.0.0.1:8000/media/temp_ON5mpPq.jpg",
                "description": "te",
                "weight": 32,
                "price": 12
            },
            "amount": 2
        },
        {
            "id": 16,
            "user": authorize_user,
            "food": {
                "id": 5,
                "name": "test2",
                "image": "http://127.0.0.1:8000/media/temp_RbDu7tz.jpg",
                "description": "test2",
                "weight": 111,
                "price": 222
            },
            "amount": 1
        }
    ]
}

TOTAL_PRICE = 3470
