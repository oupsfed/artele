from typing import Optional

from aiogram import Bot, F, Router, types
from aiogram.filters import Text
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import URLInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.middlewares.role import IsAdminMessageMiddleware
from bot.utils import get_api_answer

router = Router()
router.message.middleware(IsAdminMessageMiddleware())


class SendMessage(StatesGroup):
    direct = State()
    all = State()


class AddFood(StatesGroup):
    name = State()
    description = State()
    weight = State()
    price = State()
    image = State()


class OrderListCallbackFactory(CallbackData, prefix='orderlist'):
    action: str
    food_list: Optional[int]
    user_name: Optional[str]
    page: Optional[int]


@router.message(Text('Оформленные заказы'))
async def user_list(message: types.Message,
                    bot: Bot):
    answer = get_api_answer('order_list/download/').json()
    order_count = len(answer['by_user'])
    text = (f'На данный момент оформлено {order_count} заказов.\n'
            f'Всего было заказано: \n')
    for name, amount in answer['by_food'].items():
        text += f'{name} - {amount} шт.\n'
    text += 'Вы можете посмотреть отдельно что заказал каждый покупатель'
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Отфильтровать по пользователям',
        callback_data=OrderListCallbackFactory(
            action='filter_by_user',
        )
    )
    builder.button(
        text='Скачать список заказов документом',
        callback_data=OrderListCallbackFactory(
            action='download_pdf',
        )
    )
    builder.button(
        text='Отметить заказы',
        callback_data=OrderListCallbackFactory(
            action='edit_orders',
        )
    )
    builder.adjust(1)
    await message.answer(
        text,
        reply_markup=builder.as_markup()
    )


@router.callback_query(OrderListCallbackFactory.filter(F.action == 'filter_by_food'))
async def callbacks_show_food(
        callback: types.CallbackQuery,
        callback_data: OrderListCallbackFactory
):
    answer = get_api_answer('order_list/download/').json()
    order_count = len(answer['by_user'])
    print(len(answer['by_user']))
    text = (f'На данный момент оформлено {order_count} заказов.\n'
            f'Всего было заказано: \n')
    for name, amount in answer['by_food'].items():
        text += f'{name} - {amount} шт.\n'
    text += 'Вы можете посмотреть отдельно что заказал каждый покупатель'
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Отфильтровать по пользователям',
        callback_data=OrderListCallbackFactory(
            action='filter_by_user',
        )
    )
    builder.button(
        text='Скачать список заказов документом',
        callback_data=OrderListCallbackFactory(
            action='download_pdf',
        )
    )
    builder.adjust(1)
    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup()
    )


@router.callback_query(OrderListCallbackFactory.filter(F.action == 'filter_by_user'))
async def callbacks_show_food(
        callback: types.CallbackQuery,
        callback_data: OrderListCallbackFactory
):
    answer = get_api_answer('order_list/download/').json()
    order_count = len(answer['by_user'])
    text = f'На данный момент оформлено {order_count} заказов:\n'
    for name, food_list in answer['by_user'].items():
        text += f'<b>{name}</b>:\n'
        for food_name, amount in food_list.items():
            text += f'{food_name} - {amount} шт.\n'
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Отфильтровать по позициям',
        callback_data=OrderListCallbackFactory(
            action='filter_by_food',
        )
    )
    builder.button(
        text='Скачать список заказов документом',
        callback_data=OrderListCallbackFactory(
            action='download_pdf',
        )
    )
    builder.adjust(1)
    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup()
    )


@router.callback_query(OrderListCallbackFactory.filter(F.action == 'download_pdf'))
async def callbacks_show_food(
        callback: types.CallbackQuery,
        callback_data: OrderListCallbackFactory
):
    pdf_from_url = URLInputFile(
        'http://127.0.0.1:8000/media/order.pdf',
        filename='Заказы.pdf'
    )
    await callback.message.answer_document(pdf_from_url)


@router.callback_query(OrderListCallbackFactory.filter(F.action == 'edit_orders'))
async def callbacks_show_food(
        callback: types.CallbackQuery,
        callback_data: OrderListCallbackFactory
):
    answer = get_api_answer('order_list/download/').json()
    builder = InlineKeyboardBuilder()
    for name, food_list in answer['by_user'].items():
        print(name)
        builder.button(
            text=name,
            callback_data=OrderListCallbackFactory(
                action='show',
                user_name=name
            )
        )
    builder.button(
        text='Назад',
        callback_data=OrderListCallbackFactory(
            action='filter_by_food',
        )
    )
    builder.adjust(1)
    text = 'Выберите пользователя:'
    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup()
    )


@router.callback_query(OrderListCallbackFactory.filter(F.action == 'show'))
async def callbacks_show_food(
        callback: types.CallbackQuery,
        callback_data: OrderListCallbackFactory
):
    user_name = callback_data.user_name
    answer = get_api_answer('order_list/',
                            params={
                                'user__name': user_name,
                                'status': 'IP'
                            }).json()
    text = f'Заказ пользователя {user_name}:\n'
    for order in answer:
        text += f'- {order["food"]["name"]} - {order["amount"]} шт.\n'
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Выполнен',
        callback_data=OrderListCallbackFactory(
            action='order_done',
        )
    )
    builder.button(
        text='Отменить заказ',
        callback_data=OrderListCallbackFactory(
            action='order_cancel',
        )
    )
    builder.button(
        text='Назад',
        callback_data=OrderListCallbackFactory(
            action='edit_orders',
        )
    )
    builder.adjust(2, 1)
    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup()
    )
