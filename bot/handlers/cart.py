import logging
from http import HTTPStatus
from typing import Optional

from aiogram.types import URLInputFile
from aiogram.utils.markdown import hide_link
from aiogram import Router, types
from aiogram.filters import Command, Text
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from magic_filter import F
from utils import (check_permissions, delete_api_answer, get_api_answer,
                   post_api_answer)

router = Router()


class CartCallbackFactory(CallbackData, prefix='menu'):
    action: str
    cart_id: Optional[int]


@router.message(Text('Корзина'))
async def menu(message: types.Message):
    main_message = get_api_answer('message/cart/')
    main_message = main_message.json()
    answer = get_api_answer(f'cart/{message.from_user.id}')
    answer = answer.json()
    cart_list = answer
    builder = InlineKeyboardBuilder()
    cart_sum = 0
    rows = []
    for cart in cart_list:
        food = cart['food']
        cart_sum += food['price'] * cart['amount']
        builder.button(
            text=f"{food['name']} - {cart['amount']} шт.",
            callback_data=CartCallbackFactory(
                action='show',
                cart_id=food['id'])
        )
        rows.append(1)
        builder.button(
            text=f"-1 шт.",
            callback_data=CartCallbackFactory(
                action='delete',
                cart_id=cart['id'])
        )
        builder.button(
            text=f"+1 шт.",
            callback_data=CartCallbackFactory(
                action='add',
                cart_id=cart['id'])
        )
        rows.append(2)
    builder.button(
        text=f"Заказать - {cart_sum} ₽",
        callback_data=CartCallbackFactory(
            action='order')
    )
    rows.append(1)
    builder.adjust(*rows)
    await message.answer(
        main_message['text'],
        reply_markup=builder.as_markup()
    )


@router.callback_query(CartCallbackFactory.filter(F.action == 'cart'))
async def callbacks_show_cart(
        callback: types.CallbackQuery,
        callback_data: CartCallbackFactory
):
    main_message = get_api_answer('message/cart/')
    main_message = main_message.json()
    answer = get_api_answer(f'cart/{callback.from_user.id}')
    answer = answer.json()
    cart_list = answer
    builder = InlineKeyboardBuilder()
    cart_sum = 0
    rows = []
    for cart in cart_list:
        food = cart['food']
        cart_sum += food['price'] * cart['amount']
        builder.button(
            text=f"{food['name']} - {cart['amount']} шт.",
            callback_data=CartCallbackFactory(
                action='show',
                cart_id=food['id'])
        )
        rows.append(1)
        builder.button(
            text=f"-1 шт.",
            callback_data=CartCallbackFactory(
                action='delete',
                cart_id=cart['id'])
        )
        builder.button(
            text=f"+1 шт.",
            callback_data=CartCallbackFactory(
                action='add',
                cart_id=cart['id'])
        )
        rows.append(2)
    builder.button(
        text=f"Заказать - {cart_sum} ₽",
        callback_data=CartCallbackFactory(
            action='order')
    )
    rows.append(1)
    builder.adjust(*rows)
    await callback.message.answer(
        main_message['text'],
        reply_markup=builder.as_markup()
    )


@router.callback_query(CartCallbackFactory.filter(F.action == 'show'))
async def callbacks_show_cart(
        callback: types.CallbackQuery,
        callback_data: CartCallbackFactory
):
    answer = get_api_answer(f'food/{callback_data.cart_id}')
    food = answer.json()
    text = (f"<b>{food['name']}</b> \n"
            f"{food['description']} \n"
            f"Вес: {food['weight']} г. \n"
            f"Цена: {food['price']} ₽"
            f"")
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Назад',
        callback_data=CartCallbackFactory(
            action='cart'
        ))
    builder.adjust(1)
    if food['image']:
        image_from_url = URLInputFile(food['image'])
        await callback.message.answer_photo(
            image_from_url,
            caption=text,
            reply_markup=builder.as_markup()
        )
    else:
        await callback.message.answer(
            text,
            reply_markup=builder.as_markup()
        )
    await callback.message.delete()


@router.callback_query(CartCallbackFactory.filter(F.action == 'add'))
async def callbacks_show_cart(
        callback: types.CallbackQuery,
        callback_data: CartCallbackFactory
):
    post_api_answer(f'cart/{callback_data.cart_id}/add/', data={})
    main_message = get_api_answer('message/cart/')
    main_message = main_message.json()
    answer = get_api_answer(f'cart/{callback.from_user.id}')
    answer = answer.json()
    cart_list = answer
    builder = InlineKeyboardBuilder()
    cart_sum = 0
    rows = []
    for cart in cart_list:
        food = cart['food']
        cart_sum += food['price'] * cart['amount']
        builder.button(
            text=f"{food['name']} - {cart['amount']} шт.",
            callback_data=CartCallbackFactory(
                action='show',
                cart_id=food['id'])
        )
        rows.append(1)
        builder.button(
            text=f"-1 шт.",
            callback_data=CartCallbackFactory(
                action='delete',
                cart_id=cart['id'])
        )
        builder.button(
            text=f"+1 шт.",
            callback_data=CartCallbackFactory(
                action='add',
                cart_id=cart['id'])
        )
        rows.append(2)
    builder.button(
        text=f"Заказать - {cart_sum} ₽",
        callback_data=CartCallbackFactory(
            action='order')
    )
    rows.append(1)
    builder.adjust(*rows)
    await callback.message.delete()
    await callback.message.answer(
        main_message['text'],
        reply_markup=builder.as_markup()
    )


@router.callback_query(CartCallbackFactory.filter(F.action == 'delete'))
async def callbacks_show_cart(
        callback: types.CallbackQuery,
        callback_data: CartCallbackFactory
):
    post_api_answer(f'cart/{callback_data.cart_id}/delete/', data={})
    main_message = get_api_answer('message/cart/')
    main_message = main_message.json()
    answer = get_api_answer(f'cart/{callback.from_user.id}')
    answer = answer.json()
    cart_list = answer
    builder = InlineKeyboardBuilder()
    cart_sum = 0
    rows = []
    for cart in cart_list:
        food = cart['food']
        cart_sum += food['price'] * cart['amount']
        builder.button(
            text=f"{food['name']} - {cart['amount']} шт.",
            callback_data=CartCallbackFactory(
                action='show',
                cart_id=food['id'])
        )
        rows.append(1)
        builder.button(
            text=f"-1 шт.",
            callback_data=CartCallbackFactory(
                action='delete',
                cart_id=cart['id'])
        )
        builder.button(
            text=f"+1 шт.",
            callback_data=CartCallbackFactory(
                action='add',
                cart_id=cart['id'])
        )
        rows.append(2)
    builder.button(
        text=f"Заказать - {cart_sum} ₽",
        callback_data=CartCallbackFactory(
            action='order')
    )
    rows.append(1)
    builder.adjust(*rows)
    await callback.message.delete()
    await callback.message.answer(
        main_message['text'],
        reply_markup=builder.as_markup()
    )