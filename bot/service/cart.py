from http import HTTPStatus

from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.actions import cart_action, food_action
from core.builders import encode_callback, paginate_builder
from core.factories import CartCallbackFactory, FoodCallbackFactory
from logger import logger
from service.order import OrderCallbackFactory, order_action
from utils import delete_api_answer, get_api_answer, post_api_answer


async def cart_builder(json_response: dict,
                       total_price: int):
    cart_data = json_response['results']
    page = json_response['page']
    builder = InlineKeyboardBuilder()
    rows = []
    back = encode_callback(
        CartCallbackFactory(
            action=cart_action.get_all
        )
    )
    for cart in cart_data:
        food = cart['food']
        user = cart['user']
        builder.button(
            text=f"{food['name']} - {cart['amount']} шт.",
            callback_data=FoodCallbackFactory(
                action=food_action.get,
                back=back,
                id=food['id'],
                page=page)
        )
        rows.append(1)
        builder.button(
            text="➖",
            callback_data=CartCallbackFactory(
                action=cart_action.remove,
                food_id=food['id'],
                user_id=user['telegram_chat_id'],
                page=page)
        )
        builder.button(
            text="➕",
            callback_data=CartCallbackFactory(
                action=cart_action.create,
                food_id=food['id'],
                user_id=user['telegram_chat_id'],
                page=page)
        )
        rows.append(2)
    page_buttons, builder = await paginate_builder(
        json_response,
        builder,
        CartCallbackFactory,
        cart_action.get_all
    )
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
