from typing import Optional

from aiogram.types import URLInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils import URL, Action, ArteleCallbackData, get_api_answer

orders_list_actions = Action('ord_list')
orders_list_actions.filter_by_user = 'by_user'
orders_list_actions.filter_by_food = 'by_food'
orders_list_actions.download = 'download'
orders_list_actions.order_done = 'ord_done'
orders_list_actions.order_cancel = 'ord_cancel'


class OrderListCallbackFactory(ArteleCallbackData, prefix='ord_list'):
    order_id: Optional[int]


async def order_list_by_food():
    answer = get_api_answer('order/filter_by_food/').json()
    text = 'Всего было заказано: \n'
    for food in answer:
        text += (f'{food["food_name"]} - <b>{food["amount"]} шт. '
                 f'({food["total_weight"]} г.)</b>\n')
    return text


async def order_list_by_user():
    answer = get_api_answer('order/',
                            params={
                                'status': 'in_progress'
                            }).json()
    order_count = len(answer)
    text = f'На данный момент оформлено {order_count} заказов:\n'
    for order in answer:
        username = (f"{order['user']['first_name']} "
                    f"{order['user']['last_name']}")
        text += f'<b>{username}</b>:\n'
        for food_pos in order["food"]:
            text += (f'{food_pos["name"]} - <b>{food_pos["amount"]} шт. '
                     f'({food_pos["total_weight"]} г.)</b>\n')
    return text


async def order_list_builder(by_user=False):
    builder = InlineKeyboardBuilder()
    btn_text = 'Отфильтровать по пользователям'
    btn_action = orders_list_actions.filter_by_user
    if by_user:
        btn_text = 'Отфильтровать по позициям'
        btn_action = orders_list_actions.filter_by_food
    builder.button(
        text=btn_text,
        callback_data=OrderListCallbackFactory(
            action=btn_action,
        )
    )
    builder.button(
        text='Скачать список заказов документом',
        callback_data=OrderListCallbackFactory(
            action=orders_list_actions.download,
        )
    )
    builder.button(
        text='Отметить заказы',
        callback_data=OrderListCallbackFactory(
            action=orders_list_actions.update,
        )
    )
    builder.adjust(1)
    return builder


async def order_update_builder():
    answer = get_api_answer('order/',
                            params={
                                'status': 'in_progress'
                            }).json()
    builder = InlineKeyboardBuilder()
    for order in answer:
        username = (f"{order['user']['first_name']} "
                    f"{order['user']['last_name']}")
        builder.button(
            text=username,
            callback_data=OrderListCallbackFactory(
                action=orders_list_actions.get,
                order_id=order['id']
            )
        )
    builder.button(
        text='Назад',
        callback_data=OrderListCallbackFactory(
            action=orders_list_actions.filter_by_food,
        )
    )
    builder.adjust(1)
    return builder


async def order_user_info(order_id: int):
    answer = get_api_answer(f'order/{order_id}/').json()
    username = (f"{answer['user']['first_name']} "
                f"{answer['user']['last_name']}")
    text = f'Заказ пользователя {username}:\n'
    for food in answer['food']:
        text += (f'{food["name"]} - <b>{food["amount"]} шт. '
                 f'({food["total_weight"]} г.)</b>\n')
    return text


async def order_user_builder(order_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Выполнен',
        callback_data=OrderListCallbackFactory(
            action=orders_list_actions.order_done,
            order_id=order_id
        )
    )
    builder.button(
        text='Отменить заказ',
        callback_data=OrderListCallbackFactory(
            action=orders_list_actions.order_cancel,
            order_id=order_id
        )
    )
    builder.button(
        text='Назад',
        callback_data=OrderListCallbackFactory(
            action=orders_list_actions.update,
        )
    )
    builder.adjust(2, 1)
    return builder


async def download_pdf():
    get_api_answer('order/download/')
    pdf_url = f'{URL}media/order.pdf'
    return URLInputFile(
        pdf_url,
        filename='Заказы.pdf'
    )
