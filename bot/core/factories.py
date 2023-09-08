from typing import Optional

from aiogram.filters.callback_data import CallbackData


class ArteleCallbackData(CallbackData, prefix='artele'):
    """
    Основной Callback который содержит:
     action: str - строку действия
     id: Optional[int] - id объекта
     page: int - страницу по умолчанию 1
    """
    action: str
    id: Optional[int]
    page: int = 1


class FoodCallbackFactory(ArteleCallbackData, prefix='food'):
    """
    Callback товаров который содержит дополнительные поля:
     column: Optional[str] - поле товара
    """
    column: Optional[str]


class CartCallbackFactory(ArteleCallbackData, prefix='cart'):
    """
    Callback корзины который содержит дополнительные поля:
     food_id: Optional[int] - id товара
     user_id: Optional[int] - telegram_chat_id пользователя
    """
    food_id: Optional[int]
    user_id: Optional[int]


class OrderCallbackFactory(ArteleCallbackData, prefix='order'):
    """
    Callback заказа без дополнительных полей.
    """
    pass


class OrderListCallbackFactory(ArteleCallbackData, prefix='ord_list'):
    """
    Callback списка заказов без дополнительных полей.
    """
    pass


class UserListCallbackFactory(ArteleCallbackData, prefix='user_list'):
    """
    Callback списка пользователей без дополнительных полей.
    """
    pass


class AccessCallbackFactory(ArteleCallbackData, prefix='access'):
    """
    Callback доступа пользователей без дополнительных полей.
    """
    pass
