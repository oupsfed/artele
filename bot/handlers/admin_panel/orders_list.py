from aiogram import Bot, F, Router, types
from aiogram.filters import Text

from middlewares.role import IsAdminMessageMiddleware
from service.order import order_update
from service.orders_list import (OrderListCallbackFactory, download_pdf,
                                 order_list_builder, order_list_by_food,
                                 order_list_by_user, order_update_builder,
                                 order_user_builder, order_user_info,
                                 orders_list_actions)

router = Router()
router.message.middleware(IsAdminMessageMiddleware())


@router.message(Text('Оформленные заказы'))
async def user_list(message: types.Message,
                    bot: Bot):
    text = await order_list_by_food()
    builder = await order_list_builder()
    await message.answer(
        text,
        reply_markup=builder.as_markup()
    )


@router.callback_query(OrderListCallbackFactory.filter(F.action == orders_list_actions.filter_by_food))
async def callbacks_show_food(
        callback: types.CallbackQuery,
        callback_data: OrderListCallbackFactory
):
    text = await order_list_by_food()
    builder = await order_list_builder()
    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup()
    )


@router.callback_query(OrderListCallbackFactory.filter(F.action == orders_list_actions.filter_by_user))
async def callbacks_show_food(
        callback: types.CallbackQuery,
        callback_data: OrderListCallbackFactory
):
    text = await order_list_by_user()
    builder = await order_list_builder(by_user=True)
    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup()
    )


@router.callback_query(OrderListCallbackFactory.filter(F.action == orders_list_actions.download))
async def callbacks_show_food(
        callback: types.CallbackQuery,
        callback_data: OrderListCallbackFactory
):
    pdf_from_url = await download_pdf()
    await callback.message.answer_document(pdf_from_url)


@router.callback_query(OrderListCallbackFactory.filter(F.action == orders_list_actions.update))
async def callbacks_show_food(
        callback: types.CallbackQuery,
        callback_data: OrderListCallbackFactory
):
    builder = await order_update_builder()
    text = 'Выберите пользователя:'
    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup()
    )


@router.callback_query(OrderListCallbackFactory.filter(F.action == orders_list_actions.get))
async def callbacks_show_food(
        callback: types.CallbackQuery,
        callback_data: OrderListCallbackFactory
):
    text = await order_user_info(callback_data.order_id)
    builder = await order_user_builder(callback_data.order_id)
    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup()
    )


@router.callback_query(OrderListCallbackFactory.filter(F.action == orders_list_actions.order_done))
async def callbacks_show_food(
        callback: types.CallbackQuery,
        callback_data: OrderListCallbackFactory
):
    answer, text = await order_update(order_id=callback_data.order_id,
                                      status='done')
    await callback.message.answer(
        text
    )
    await callback.message.delete()


@router.callback_query(OrderListCallbackFactory.filter(F.action == orders_list_actions.order_cancel))
async def callbacks_show_food(
        callback: types.CallbackQuery,
        callback_data: OrderListCallbackFactory
):
    answer, text = await order_update(order_id=callback_data.order_id,
                                      status='cancelled')
    await callback.message.answer(
        text
    )
    await callback.message.delete()
