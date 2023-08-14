from aiogram import Router, types
from aiogram.filters import Text
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from magic_filter import F

from bot.utils import get_api_answer, post_api_answer

router = Router()


class OrderCallbackFactory(CallbackData, prefix='order'):
    action: str


@router.message(Text('Заказ'))
async def order(message: types.Message):
    answer = get_api_answer(
        'order/',
        params={'status': 'IP',
                'user__telegram_chat_id': message.from_user.id}
    )
    order_list = answer.json()
    builder = InlineKeyboardBuilder()
    text = 'Ваш заказ: \n'
    for order_pos in order_list:
        food = order_pos['food']
        text += f' - {food["name"]} ({order_pos["amount"]} шт.) \n'
    builder.button(
        text="Отменить заказ",
        callback_data=OrderCallbackFactory(
            action='cancel')
    )
    builder.adjust(1)
    await message.answer(
        text,
        reply_markup=builder.as_markup()
    )


@router.callback_query(OrderCallbackFactory.filter(F.action == 'cancel'))
async def callbacks_show_cart(
        callback: types.CallbackQuery,
        callback_data: OrderCallbackFactory
):
    answer = post_api_answer(f'order/{callback.from_user.id}/cancel/',
                             data={})
    await callback.message.delete()
    await callback.message.answer(
        answer.json()
    )
