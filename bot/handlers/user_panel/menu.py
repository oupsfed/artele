import logging

from aiogram import Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Text
from magic_filter import F

from bot.service.cart import add_to_cart, remove_from_cart
from bot.service.menu import (MenuCallbackFactory, food_builder, food_info,
                              menu_builder)

router = Router()

MAIN_MESSAGE = 'Меню:'


@router.message(Text('Меню'))
async def menu(message: types.Message):
    builder = await menu_builder(page=1)
    await message.answer(
        MAIN_MESSAGE,
        reply_markup=builder.as_markup()
    )


@router.callback_query(MenuCallbackFactory.filter(F.action == 'food'))
async def callbacks_show_food(
        callback: types.CallbackQuery,
        callback_data: MenuCallbackFactory
):
    food_id = callback_data.food_id
    food_data = await food_info(food_id)
    builder = await food_builder(
        callback.from_user.id,
        food_id,
        callback_data.page
    )
    await callback.message.answer_photo(
        food_data['image'],
        caption=food_data['text'],
        reply_markup=builder.as_markup()
    )
    await callback.message.delete()


@router.callback_query(MenuCallbackFactory.filter(F.action == 'menu'))
async def callbacks_show_page(
        callback: types.CallbackQuery,
        callback_data: MenuCallbackFactory
):
    builder = await menu_builder(page=callback_data.page)
    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(
            MAIN_MESSAGE,
            reply_markup=builder.as_markup()
        )
    else:
        await callback.message.edit_reply_markup(
            MAIN_MESSAGE,
            reply_markup=builder.as_markup()
        )


@router.callback_query(MenuCallbackFactory.filter(F.action == 'add_to_cart'))
async def callbacks_add_to_cart(
        callback: types.CallbackQuery,
        callback_data: MenuCallbackFactory
):
    user_id = callback.from_user.id
    food_id = callback_data.food_id
    await add_to_cart(
        user_id=user_id,
        food_id=food_id
    )
    builder = await food_builder(
        user_id=user_id,
        food_id=food_id,
        page=callback_data.page
    )
    await callback.message.edit_reply_markup(
        reply_markup=builder.as_markup()
    )


@router.callback_query(MenuCallbackFactory.filter(F.action == 'remove_from_cart'))
async def callbacks_remove_from_cart(
        callback: types.CallbackQuery,
        callback_data: MenuCallbackFactory
):
    user = callback.from_user
    food_id = callback_data.food_id
    await remove_from_cart(
        user.id,
        food_id
    )
    builder = await food_builder(
        callback.from_user.id,
        food_id,
        callback_data.page
    )
    try:
        await callback.message.edit_reply_markup(
            reply_markup=builder.as_markup()
        )
    except TelegramBadRequest:
        logging.info('Пользователь пытается сделать '
                     'количетсво продуктов отрицательным')
