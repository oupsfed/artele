from http import HTTPStatus
from typing import Optional

from aiogram.types import URLInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.utils import Action, get_api_answer, post_api_answer, ArteleCallbackData

orders_list_actions = Action('ord_list')
orders_list_actions.filter_by_user = 'by_user'
orders_list_actions.filter_by_food = 'by_food'
orders_list_actions.download = 'download'
orders_list_actions.order_done = 'ord_done'
orders_list_actions.order_cancel = 'ord_cancel'


class OrderListCallbackFactory(ArteleCallbackData, prefix='ord_list'):
    food_list: Optional[int]
    user_name: Optional[str]


async def order_list_by_food():
    answer = get_api_answer('order_list/download/').json()
    order_count = len(answer['by_user'])
    text = (f'На данный момент оформлено {order_count} заказов.\n'
            f'Всего было заказано: \n')
    for name, amount in answer['by_food'].items():
        text += f'{name} - {amount} шт.\n'
    text += 'Вы можете посмотреть отдельно что заказал каждый покупатель'
    return text


async def order_list_by_user():
    answer = get_api_answer('order_list/download/').json()
    order_count = len(answer['by_user'])
    text = f'На данный момент оформлено {order_count} заказов:\n'
    for name, food_list in answer['by_user'].items():
        text += f'<b>{name}</b>:\n'
        for food_name, amount in food_list.items():
            text += f'{food_name} - {amount} шт.\n'
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
    answer = get_api_answer('order_list/download/').json()
    builder = InlineKeyboardBuilder()
    for name, food_list in answer['by_user'].items():
        builder.button(
            text=name,
            callback_data=OrderListCallbackFactory(
                action=orders_list_actions.get,
                user_name=name
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


async def order_user_info(user_name: str):
    answer = get_api_answer('order_list/',
                            params={
                                'user__name': user_name,
                                'status': 'IP'
                            }).json()
    text = f'Заказ пользователя {user_name}:\n'
    for order in answer:
        text += f'- {order["food"]["name"]} - {order["amount"]} шт.\n'
    return text


async def order_user_builder(user_name: str):
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Выполнен',
        callback_data=OrderListCallbackFactory(
            action=orders_list_actions.order_done,
            user_name=user_name
        )
    )
    builder.button(
        text='Отменить заказ',
        callback_data=OrderListCallbackFactory(
            action=orders_list_actions.order_cancel,
            user_name=user_name
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


async def order_done(user_name: str):
    answer = post_api_answer('order/done/',
                             data={
                                 'user_name': user_name
                             })
    return answer.json()


async def order_cancel(user_name: str):
    answer = post_api_answer('order/cancel/',
                             data={
                                 'user_name': user_name
                             })
    if answer.status_code == HTTPStatus.NO_CONTENT:
        return 'Заказ успешно удален'
    return 'Произошла ошибка при удалении товара'


async def download_pdf():
    pdf_from_url = URLInputFile(
        'http://127.0.0.1:8000/media/order.pdf',
        filename='Заказы.pdf'
    )
    return pdf_from_url
