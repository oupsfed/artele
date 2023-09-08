from aiogram.types import URLInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from core.actions import orders_list_actions
from core.factories import OrderListCallbackFactory
from utils import URL, get_api_answer


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
        text += f'<b>{order["user"]["fullname"]}</b>:\n'
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
        builder.button(
            text=order['user']['fullname'],
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
    text = f'Заказ пользователя {answer["user"]["fullname"]}:\n'
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
