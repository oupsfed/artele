from aiogram import Bot, Router, types
from aiogram.filters import Text
from magic_filter import F

from service.order import (OrderCallbackFactory, order_action, order_builder,
                           order_create, order_info, order_update)

router = Router()


@router.message(Text('Заказ'))
async def order(message: types.Message):
    order_id, text = await order_info(message.from_user.id)
    builder = await order_builder(order_id)
    await message.answer(
        text,
        reply_markup=builder.as_markup()
    )


@router.callback_query(OrderCallbackFactory.filter(F.action == order_action.create))
async def callbacks_show_cart(
        callback: types.CallbackQuery,
        callback_data: OrderCallbackFactory,
        bot: Bot
):
    answer = await order_create(callback.from_user.id)
    await callback.message.delete()
    await callback.message.answer(
        answer
    )


@router.callback_query(OrderCallbackFactory.filter(F.action == order_action.remove))
async def callbacks_order_cancel(
        callback: types.CallbackQuery,
        callback_data: OrderCallbackFactory
):
    answer, text = await order_update(callback_data.order_id,
                                      status='cancelled')
    await callback.message.delete()
    await callback.message.answer(
        text
    )
