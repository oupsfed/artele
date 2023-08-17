from aiogram import Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Text
from aiogram.utils.keyboard import InlineKeyboardBuilder
from magic_filter import F

from logger import logger
from service.cart import (CartCallbackFactory, add_to_cart, cart_action,
                          cart_builder, remove_from_cart)
from service.food import food_info

router = Router()

MAIN_MESSAGE = 'Корзина:'


@router.message(Text('Корзина'))
async def menu(message: types.Message):
    builder = await cart_builder(
        user_id=message.from_user.id,
        page=1
    )
    await message.answer(
        MAIN_MESSAGE,
        reply_markup=builder.as_markup()
    )


@router.callback_query(CartCallbackFactory.filter(F.action == cart_action.get_all))
async def callbacks_show_cart(
        callback: types.CallbackQuery,
        callback_data: CartCallbackFactory
):
    builder = await cart_builder(
        user_id=callback.from_user.id,
        page=callback_data.page
    )
    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(
            MAIN_MESSAGE,
            reply_markup=builder.as_markup()
        )
    else:
        await callback.message.edit_reply_markup(
            reply_markup=builder.as_markup()
        )


@router.callback_query(CartCallbackFactory.filter(F.action == cart_action.get))
async def callbacks_show_cart(
        callback: types.CallbackQuery,
        callback_data: CartCallbackFactory
):
    food_data = await food_info(callback_data.food_id)
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Назад',
        callback_data=CartCallbackFactory(
            action=cart_action.get_all,
            page=callback_data.page
        ))
    builder.adjust(1)
    await callback.message.answer_photo(
        food_data['image'],
        caption=food_data['text'],
        reply_markup=builder.as_markup()
    )
    await callback.message.delete()


@router.callback_query(CartCallbackFactory.filter(F.action == cart_action.create))
async def callbacks_add_to_cart(
        callback: types.CallbackQuery,
        callback_data: CartCallbackFactory
):
    user_id = callback.from_user.id
    food_id = callback_data.food_id
    await add_to_cart(
        user_id=user_id,
        food_id=food_id
    )
    builder = await cart_builder(
        user_id=callback.from_user.id,
        page=callback_data.page
    )
    await callback.message.edit_reply_markup(
        reply_markup=builder.as_markup()
    )


@router.callback_query(CartCallbackFactory.filter(F.action == cart_action.remove))
async def callbacks_delete_from_cart(
        callback: types.CallbackQuery,
        callback_data: CartCallbackFactory
):
    user = callback.from_user
    food_id = callback_data.food_id
    await remove_from_cart(
        user.id,
        food_id
    )
    builder = await cart_builder(
        user_id=callback.from_user.id,
        page=callback_data.page
    )
    try:
        await callback.message.edit_reply_markup(
            reply_markup=builder.as_markup()
        )
    except TelegramBadRequest:
        logger.info('Пользователь пытается сделать '
                    'количетсво продуктов отрицательным')
