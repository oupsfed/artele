from tests.fixtures.user import admin_user

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


CART_DATA = {
    "count": 1,
    "page": 1,
    "next": None,
    "previous": None,
    "results": [
        {
            "id": 10,
            "user": admin_user,
            "food": {
                "id": 1,
                "name": "t23",
                "image": None,
                "description": "desc",
                "weight": 10,
                "price": 50
            },
            "amount": 3
        }
    ]
}