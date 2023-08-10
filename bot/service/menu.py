import logging
from http import HTTPStatus
from typing import Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.types import URLInputFile, InputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.utils import get_api_answer, post_api_answer


class MenuCallbackFactory(CallbackData, prefix='menu'):
    action: str
    food_id: Optional[int]
    page: Optional[int] = 1


async def menu_builder(page: int = 1):
    answer = get_api_answer('food/',
                            params={
                                'page': page
                            })
    answer = answer.json()
    food_list = answer['results']
    builder = InlineKeyboardBuilder()
    rows = []
    for food in food_list:
        builder.button(
            text=f"{food['name']} - {food['price']} ₽",
            callback_data=MenuCallbackFactory(
                action='food',
                food_id=food['id'],
                page=page)
        )
        rows.append(1)
    page_buttons = 0
    if answer['previous']:
        builder.button(
            text="⬅️",
            callback_data=MenuCallbackFactory(
                action='menu',
                page=page - 1)
        )
        page_buttons += 1
    if answer['next']:
        builder.button(
            text="➡️",
            callback_data=MenuCallbackFactory(
                action='menu',
                page=page + 1)
        )
        page_buttons += 1
    rows.append(page_buttons)
    builder.adjust(*rows)
    return builder


async def food_info(food_id: int):
    answer = get_api_answer(f'food/{food_id}')
    food = answer.json()
    text = (f"<b>{food['name']}</b> \n"
            f"{food['description']} \n"
            f"Вес: {food['weight']} г. \n"
            f"Цена: {food['price']} ₽")
    food_image = URLInputFile('https://agentura-soft.ru/images/noImage.png')
    if food['image']:
        food_image = URLInputFile(food['image'])
    return {
        'text': text,
        'image': food_image
    }


async def food_builder(user_id: int,
                       food_id: int,
                       page: int = 1):
    cart = get_api_answer(
        'cart/',
        params={
            'user__telegram_chat_id': user_id,
            'food__id': food_id
        }).json()
    cart = cart['results']
    amount = 0
    food_price = 0
    if cart:
        amount = cart[0]['amount']
        food_price = cart[0]['food']['price']
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f'{amount} шт. ({amount * food_price} ₽)',
        callback_data=MenuCallbackFactory(
            action='add_to_cart',
            food_id=food_id
        )
    )
    builder.button(
        text=f'➖',
        callback_data=MenuCallbackFactory(
            action='remove_from_cart',
            food_id=food_id
        )
    )
    builder.button(
        text=f'➕',
        callback_data=MenuCallbackFactory(
            action='add_to_cart',
            food_id=food_id
        )
    )
    builder.button(
        text='↩️',
        callback_data=MenuCallbackFactory(
            action='menu',
            page=page
        )
    )
    builder.adjust(1, 2, 1)
    return builder


async def food_add_to_cart(user_id: int,
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


async def food_remove_from_cart(user_id: int,
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
