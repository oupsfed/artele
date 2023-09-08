import pytest
from aiogram.utils.keyboard import InlineKeyboardBuilder
from core.actions import food_action, order_action
from service.cart import cart_builder

from .fixtures.cart import CART_LIST_PAGE_2, TOTAL_PRICE
from .utils import check_paginator

pytest_plugins = ('pytest_asyncio',)


@pytest.mark.asyncio
async def test_cart_builder():
    builder = await cart_builder(CART_LIST_PAGE_2,
                                 TOTAL_PRICE)
    assert isinstance(builder, InlineKeyboardBuilder), (
        'Функция должна вернуть класс InlineKeyboardBuilder'
    )
    builder_data = builder.as_markup()
    builder_data = builder_data.inline_keyboard
    cart_data = CART_LIST_PAGE_2['results']
    rows_number = len(cart_data) * 2 + 2
    assert len(builder_data) == rows_number, (
        'Неправильное количество кнопок в menu_buillder'
    )
    print(builder_data)
    cart_number = 0
    for row_number in range(len(cart_data) * 2):
        if len(builder_data[row_number]) == 1:
            btn = builder_data[row_number][0]
            cart_item = cart_data[cart_number]
            cart_number += 1
            exp_text = (f'{cart_item["food"]["name"]} - '
                        f'{cart_item["amount"]} шт.')
            assert btn.text == exp_text, (
                f'У кнопки {btn.text} текст не соответствует ожидаемому'
            )
            callback_data = btn.callback_data.split(':')
            assert callback_data[0] in str(food_action), (
                f'У кнопки {btn.text} CallbackFactory не соответствует ожидаемому'
            )
            assert callback_data[1] == food_action.get, (
                f'У кнопки {btn.text} food_action не соответствует ожидаемому'
            )
            assert callback_data[2] == str(cart_item['food']['id']), (
                f'У кнопки {btn.text} food_id не соответствует ожидаемому'
            )
        else:
            btn_minus = builder_data[row_number][0]
            btn_plus = builder_data[row_number][1]
            assert btn_minus.text == '➖', (
                f'У кнопки {btn_minus.text} текст не соответствует ожидаемому'
            )
            assert btn_plus.text == '➕', (
                f'У кнопки {btn_plus.text} текст не соответствует ожидаемому'
            )
    check_paginator(builder_data[-2], CART_LIST_PAGE_2['page'])
    btn_order = builder_data[-1][0]
    assert btn_order.text == f'Заказать - {TOTAL_PRICE} ₽', (
        f'У кнопки {btn_order} тект не соответствует ожидаемому'
    )
    callback_data = btn_order.callback_data.split(':')
    assert callback_data[0] in str(order_action), (
        f'У кнопки {btn_order.text} CallbackFactory не соответствует ожидаемому'
    )
    assert callback_data[1] == order_action.create, (
        f'У кнопки {btn_order.text} food_action не соответствует ожидаемому'
    )