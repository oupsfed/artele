import logging
from http import HTTPStatus

from aiogram import Bot, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Text
from aiogram.utils.keyboard import InlineKeyboardBuilder
from magic_filter import F

from bot.middlewares.role import is_guest
from bot.service.cart import (CartCallbackFactory, add_to_cart, cart_builder,
                              remove_from_cart)
from bot.service.menu import food_info
from bot.utils import send_message_to_admin, get_api_answer, post_api_answer

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


@router.callback_query(CartCallbackFactory.filter(F.action == 'cart'))
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


@router.callback_query(CartCallbackFactory.filter(F.action == 'cart_food'))
async def callbacks_show_cart(
        callback: types.CallbackQuery,
        callback_data: CartCallbackFactory
):
    answer = get_api_answer(f'food/{callback_data.cart_id}')
    food = answer.json()
    food_data = await food_info(food['id'])
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Назад',
        callback_data=CartCallbackFactory(
            action='cart',
            page=callback_data.page
        ))
    builder.adjust(1)
    await callback.message.answer_photo(
        food_data['image'],
        caption=food_data['text'],
        reply_markup=builder.as_markup()
    )
    await callback.message.delete()


@router.callback_query(CartCallbackFactory.filter(F.action == 'add'))
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


@router.callback_query(CartCallbackFactory.filter(F.action == 'delete'))
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
        logging.info('Пользователь пытается сделать '
                     'количетсво продуктов отрицательным')


@router.callback_query(CartCallbackFactory.filter(F.action == 'order'))
async def callbacks_show_cart(
        callback: types.CallbackQuery,
        callback_data: CartCallbackFactory,
        bot: Bot
):
    if is_guest(callback.from_user.id):
        answer = (
            'Недостаточно прав для оформления заказа \n'
            'Подайте заявку на доступ к заказам'
        )
    else:
        answer = post_api_answer(f'cart/{callback.from_user.id}/order/',
                                 data={})
        if answer.status_code == HTTPStatus.CREATED:
            await send_message_to_admin(
                bot,
                'Добавлен новый заказ'
            )
    await callback.message.delete()
    await callback.message.answer(
        answer.json()
    )
