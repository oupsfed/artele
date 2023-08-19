from aiogram import Bot, F, Router, types
from aiogram.filters import Text
from aiogram.utils.keyboard import InlineKeyboardBuilder
from middlewares.role import IsAdminMessageMiddleware
from service.access import (AccessCallbackFactory, access_action,
                            access_create, access_get_builder, access_get_info,
                            access_list_builder, access_remove)

router = Router()
router.message.middleware(IsAdminMessageMiddleware())


@router.message(Text('Заявки на вступление'))
async def access_list(message: types.Message):
    text = 'Заявки на доступ к оформлению заказов'
    builder = await access_list_builder()
    await message.answer(
        text,
        reply_markup=builder.as_markup()
    )


@router.callback_query(AccessCallbackFactory.filter(F.action == access_action.get))
async def callbacks_show_request(
        callback: types.CallbackQuery,
        callback_data: AccessCallbackFactory
):
    text = await access_get_info(callback_data.user_id)
    builder = await access_get_builder(callback_data.user_id)
    await callback.message.edit_reply_markup(
        text,
        reply_markup=builder.as_markup()
    )


@router.callback_query(AccessCallbackFactory.filter(F.action == access_action.create))
async def callbacks_accepct_request(
        callback: types.CallbackQuery,
        callback_data: AccessCallbackFactory,
        bot: Bot
):
    text = await access_create(callback_data.user_id)
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Назад',
        callback_data=AccessCallbackFactory(
            action=access_action.get_all,
            page=callback_data.page)
    )
    builder.adjust(1)
    await callback.message.answer(text,
                                  reply_markup=builder.as_markup())
    await callback.message.delete()


@router.callback_query(AccessCallbackFactory.filter(F.action == access_action.remove))
async def callbacks_accepct_request(
        callback: types.CallbackQuery,
        callback_data: AccessCallbackFactory,
        bot: Bot
):
    text = await access_remove(callback_data.user_id)
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Назад',
        callback_data=AccessCallbackFactory(
            action=access_action.get_all,
            page=callback_data.page)
    )
    builder.adjust(1)
    await callback.message.answer(text,
                                  reply_markup=builder.as_markup())
    await callback.message.delete()


@router.callback_query(AccessCallbackFactory.filter(F.action == access_action.get_all))
async def callbacks_accepct_request(
        callback: types.CallbackQuery,
        callback_data: AccessCallbackFactory,
        bot: Bot
):
    builder = await access_list_builder(callback_data.page)
    await callback.message.edit_reply_markup(
        "Заявки на доступ к оформлению заказа",
        reply_markup=builder.as_markup()
    )
