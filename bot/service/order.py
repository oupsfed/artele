from http import HTTPStatus

from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.middlewares.role import is_guest
from bot.service.message import send_message_to_admin
from bot.utils import Action, get_api_answer, post_api_answer

order_action = Action('order')


class OrderCallbackFactory(CallbackData, prefix='order'):
    action: str


async def order_info(user_id: int):
    answer = get_api_answer(
        'order/',
        params={'status': 'IP',
                'user__telegram_chat_id': user_id}
    )
    order_list = answer.json()
    text = 'Ваш заказ: \n'
    for order_pos in order_list:
        food = order_pos['food']
        text += f' - {food["name"]} ({order_pos["amount"]} шт.) \n'
    return text


async def order_builder():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Отменить заказ",
        callback_data=OrderCallbackFactory(
            action=order_action.remove)
    )
    builder.adjust(1)
    return builder


async def order_create(user_id: int,
                       bot):
    if is_guest(user_id):
        answer = (
            'Недостаточно прав для оформления заказа \n'
            'Подайте заявку на доступ к заказам'
        )
    else:
        answer = post_api_answer(f'cart/{user_id}/order/',
                                 data={})
        if answer.status_code == HTTPStatus.CREATED:
            await send_message_to_admin(
                'Добавлен новый заказ'
            )
    return answer
