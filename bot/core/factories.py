from typing import Optional

from aiogram.filters.callback_data import CallbackData


class ArteleCallbackData(CallbackData, prefix='artele'):
    action: str
    back: Optional[str]
    id: Optional[int]
    page: int = 1


class FoodCallbackFactory(ArteleCallbackData, prefix='food'):
    column: Optional[str]


class CartCallbackFactory(ArteleCallbackData, prefix='cart'):
    food_id: Optional[int]
    user_id: Optional[int]


class OrderCallbackFactory(ArteleCallbackData, prefix='order'):
    order_id: Optional[int]


class OrderListCallbackFactory(ArteleCallbackData, prefix='ord_list'):
    order_id: Optional[int]


class UserListCallbackFactory(ArteleCallbackData, prefix='user_list'):
    user_id: Optional[int]


class AccessCallbackFactory(ArteleCallbackData, prefix='access'):
    user_id: Optional[int]
