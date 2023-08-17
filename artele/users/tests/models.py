from django.test import TestCase
from users.models import User


class UserModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            telegram_chat_id=1123
        )

    def test_show_correct_str(self):
        """Проверяем, что у моделей корректно работает __str__."""
        user = UserModelTest.user
        self.assertEqual(str(user), str(user.telegram_chat_id))