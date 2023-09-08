from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.actions import cart_action, food_action
from core.builders import paginate_builder
from core.factories import CartCallbackFactory, FoodCallbackFactory
from service.order import OrderCallbackFactory, order_action


async def cart_builder(json_response: dict,
                       total_price: int):
    cart_data = json_response
    page = 1
    if 'results' in json_response:
        cart_data = json_response['results']
        page = json_response['page']
    builder = InlineKeyboardBuilder()
    rows = []
    for cart in cart_data:
        food = cart['food']
        user = cart['user']
        builder.button(
            text=f"{food['name']} - {cart['amount']} шт.",
            callback_data=FoodCallbackFactory(
                action=food_action.get,
                id=food['id'],
                page=page)
        )
        rows.append(1)
        builder.button(
            text="➖",
            callback_data=CartCallbackFactory(
                action=cart_action.remove,
                food_id=food['id'],
                user_id=user['telegram_chat_id'],
                page=page)
        )
        builder.button(
            text="➕",
            callback_data=CartCallbackFactory(
                action=cart_action.create,
                food_id=food['id'],
                user_id=user['telegram_chat_id'],
                page=page)
        )
        rows.append(2)
    page_buttons, builder = await paginate_builder(
        json_response,
        builder,
        CartCallbackFactory,
        cart_action.get_all
    )
    if page_buttons > 0:
        rows.append(page_buttons)
    builder.button(
        text=f"Заказать - {total_price} ₽",
        callback_data=OrderCallbackFactory(
            action=order_action.create)
    )
    rows.append(1)
    builder.adjust(*rows)
    return builder
