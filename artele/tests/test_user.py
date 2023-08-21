import os

import pytest
from dotenv import load_dotenv
from tests.utils import (check_pagination, create_carts, create_foods,
                         create_single_order, create_users)
from users.models import User

pytestmark = pytest.mark.django_db

load_dotenv()

URL = os.getenv('URL')


@pytest.mark.django_db(transaction=True)
class TestUserAPI:

    def test_01_user_str(self, client):
        users = create_users(client)
        user = User.objects.get(telegram_chat_id=1)
        assert str(user) == 'Неизвестный пользователь', (
            'Проверьте что str пользователя выводит его '
            'name'
        )
