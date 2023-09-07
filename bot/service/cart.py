from http import HTTPStatus
from typing import Optional

from aiogram.utils.keyboard import InlineKeyboardBuilder

from logger import logger
from service.order import OrderCallbackFactory, order_action
from utils import (Action, ArteleCallbackData, delete_api_answer,
                   get_api_answer, post_api_answer)

cart_action = Action('cart')


class CartCallbackFactory(ArteleCallbackData, prefix='cart'):
    cart_id: Optional[int]
    food_id: Optional[int]
    user_id: Optional[int]


async def cart_builder(user_id: int,
                       page: int = 1):
    answer = get_api_answer(
        'cart/',
        params={
            'user': user_id,
            'page': page
        })
    answer = answer.json()
    cart_data = answer['results']
    builder = InlineKeyboardBuilder()
    total_price = 0
    rows = []
    for cart in cart_data:
        food = cart['food']
        total_price += food['price'] * cart['amount']
        builder.button(
            text=f"{food['name']} - {cart['amount']} шт.",
            callback_data=CartCallbackFactory(
                action=cart_action.get,
                food_id=food['id'],
                page=page)
        )
        rows.append(1)
        builder.button(
            text="➖",
            callback_data=CartCallbackFactory(
                action=cart_action.remove,
                food_id=food['id'],
                user_id=user_id,
                page=page)
        )
        builder.button(
            text="➕",
            callback_data=CartCallbackFactory(
                action=cart_action.create,
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
                action=cart_action.get_all,
                page=page - 1)
        )
        page_buttons += 1
    if answer['next']:
        builder.button(
            text="➡️",
            callback_data=CartCallbackFactory(
                action=cart_action.get_all,
                page=page + 1)
        )
        page_buttons += 1
    if page_buttons > 0:
        rows.append(page_buttons)
    builder.button(
        text=f"Заказать - {total_price} ₽",
        callback_data=OrderCallbackFactory(
            action=order_action.create)
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
        logger.info(f'{user_id}: добавил товар в корзину')
    else:
        logger.error(f'Произошла ошибка при добавлении товара в корзину:'
                     f'{data} \n {answer.json()}')


async def remove_from_cart(user_id: int,
                           food_id: int):
    data = {
        'user': user_id,
        'food': food_id
    }
    answer = get_api_answer('cart/',
                            params=data)
    answer = answer.json()
    if answer['count'] != 1:
        logger.info(f'Ошибка при запросе к корзине {user_id}')
        return
    cart_id = answer['results'][0]['id']
    answer = delete_api_answer(f'cart/{cart_id}/')
    if answer.status_code == HTTPStatus.OK:
        logger.info(f'{user_id}: удалил товар из корзины')
    else:
        logger.error(f'Произошла ошибка при удалении товара из корзин:'
                     f'{data} \n {answer.json()}')
