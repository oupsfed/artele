from http import HTTPStatus
from typing import Optional

from aiogram.utils.keyboard import InlineKeyboardBuilder

from logger import logger
from middlewares.role import is_guest
from service.message import send_message_to_admin
from utils import (Action, ArteleCallbackData, get_api_answer,
                   patch_api_answer, post_api_answer)

order_action = Action('order')


class OrderCallbackFactory(ArteleCallbackData, prefix='order'):
    order_id: Optional[int]


async def order_info(user_id: int):
    answer = get_api_answer(
        'order/',
        params={'status': 'IP',
                'user': user_id}
    )
    order = answer.json()
    if len(order) == 0:
        return 0, 'В данный момент у вас нет оформленных заказов'
    order = order[0]
    text = 'Ваш заказ: \n'
    for food in order['food']:
        text += (f' - {food["name"]} '
                 f'({food["amount"]} шт.) - '
                 f'{food["price"] * food["amount"]} ₽\n')
    text += f'Итого: {order["total_price"]} ₽'
    return order['id'], text


async def order_builder(order_id: int):
    builder = InlineKeyboardBuilder()
    if order_id == 0:
        return builder
    builder.button(
        text="Отменить заказ",
        callback_data=OrderCallbackFactory(
            action=order_action.remove,
            order_id=order_id)
    )
    builder.adjust(1)
    return builder


async def order_create(user_id: int):
    if is_guest(user_id):
        answer = (
            'Недостаточно прав для оформления заказа \n'
            'Подайте заявку на доступ к заказам'
        )
    else:
        data = {
            'user': user_id
        }
        answer = post_api_answer('order/',
                                 data=data)
        if answer.status_code == HTTPStatus.CREATED:
            await send_message_to_admin(
                'Добавлен новый заказ'
            )
            logger.info(f'{user_id}: добавил новый заказ')
        else:
            logger.error('Произошла ошибка при создании заказа \n'
                         f'{answer.json()}')
    return answer


async def order_update(order_id: int,
                       status: str = 'IP'):
    status_data = {
        'IP': 'в работе',
        'C': 'отменен',
        'D': 'выполнен'
    }
    answer = patch_api_answer(f'order/{order_id}/',
                              data={
                                  'status': status
                              })
    if answer.status_code == HTTPStatus.OK:
        text = f'Заказ №{order_id} {status_data[status]}'
        await send_message_to_admin(
            text
        )
        logger.info(text)
    else:
        text = 'Произошла ошибка- обратитесь к администратору'
        logger.error(f'{text} \n'
                     f'{answer.json()}')

    return answer, text
