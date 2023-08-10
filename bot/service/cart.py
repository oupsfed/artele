import logging
from http import HTTPStatus
from typing import Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.utils import get_api_answer, post_api_answer


class CartCallbackFactory(CallbackData, prefix='cart'):
    action: str
    cart_id: Optional[int]
    food_id: Optional[int]
    user_id: Optional[int]
    page: Optional[int]


async def cart_builder(user_id: int,
                       page: int = 1):
    answer = get_api_answer(
        'cart/',
        params={
            'user__telegram_chat_id': user_id,
            'page': page
        })
    answer = answer.json()
    cart_list = answer['results']
    builder = InlineKeyboardBuilder()
    cart_sum = get_api_answer(f'cart/{user_id}/sum/')
    cart_sum = cart_sum.json()
    rows = []
    for cart in cart_list:
        food = cart['food']
        builder.button(
            text=f"{food['name']} - {cart['amount']} шт.",
            callback_data=CartCallbackFactory(
                action='cart_food',
                cart_id=food['id'],
                page=page)
        )
        rows.append(1)
        builder.button(
            text="➖",
            callback_data=CartCallbackFactory(
                action='delete',
                food_id=food['id'],
                user_id=user_id,
                page=page)
        )
        builder.button(
            text="➕",
            callback_data=CartCallbackFactory(
                action='add',
                food_id=food['id'],
                user_id=user_id,
                page=page)
        )
        rows.append(2)
    page_buttons = 0
    if answer['previous']:
        builder.button(
            text="⬅️",
            callback_data=CartCallbackFactory(
                action='cart',
                page=page - 1)
        )
        page_buttons += 1
    if answer['next']:
        builder.button(
            text="➡️",
            callback_data=CartCallbackFactory(
                action='cart',
                page=page + 1)
        )
        page_buttons += 1
    if page_buttons > 0:
        rows.append(page_buttons)
    builder.button(
        text=f"Заказать - {cart_sum} ₽",
        callback_data=CartCallbackFactory(
            action='order')
    )
    rows.append(1)
    builder.adjust(*rows)
    return builder


async def add_to_cart(user_id: int,
                      food_id: int):
    data = {
        'user': user_id,
        'food': food_id
    }
    answer = post_api_answer('cart/',
                             data=data)
    if answer.status_code == HTTPStatus.CREATED:
        logging.info('chat_id - {user.id}: добавил товар в корзину')
    else:
        logging.error(f'Произошла ошибка при добавлении товара в корзину:'
                      f'{data} \n {answer.json()}')


async def remove_from_cart(user_id: int,
                           food_id: int):
    data = {
        'user__telegram_chat_id': user_id,
        'food__id': food_id
    }
    answer = get_api_answer('cart/',
                            params=data)
    answer = answer.json()
    if answer['count'] != 1:
        logging.info(f'Ошибка при запросе к корзине {user_id}')
        return
    cart_id = answer['results'][0]['id']
    answer = post_api_answer(f'cart/{cart_id}/delete/', data={})
    if answer.status_code == HTTPStatus.OK:
        logging.info(f'chat_id - {user_id}: удалил товар из корзины')
    else:
        logging.error(f'Произошла ошибка при удалении товара из корзин:'
                      f'{data} \n {answer.json()}')
