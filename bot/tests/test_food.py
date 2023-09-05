import asyncio
import pytest
from aiogram.types import URLInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from service.food import menu_builder, food_info, food_builder
from .fixtures.food import FOOD_DATA, CART_DATA
from .utils import check_paginator


pytest_plugins = ('pytest_asyncio',)


@pytest.mark.asyncio
async def test_menu_builder():
    food_list = FOOD_DATA['results']
    builder = await menu_builder(FOOD_DATA,
                                 admin=True)
    assert isinstance(builder, InlineKeyboardBuilder), (
        'Функция должна вернуть класс InlineKeyboardBuilder'
    )
    builder_data = builder.as_markup()
    builder_data = builder_data.inline_keyboard
    assert len(builder_data) == 5, (
        'Неправильное количество кнопок в menu_buillder'
    )
    for food_number in range(len(food_list)):
        food_id = food_list[food_number]['id']
        callback_data = builder_data[food_number][0].callback_data.split(':')
        expected_btn_txt = (f"{food_list[food_number]['name']} "
                            f"- {food_list[food_number]['price']} ₽")
        assert builder_data[food_number][0].text == expected_btn_txt, (
            'Неправильное название кнопок'
        )
        assert callback_data[0] == 'food', (
            'Неправильный класс CallbackFactory'
        )
        assert callback_data[1] == 'foodget', (
            'Неправильный food_action'
        )
        assert int(callback_data[2]) == FOOD_DATA['page'], (
            'Неправильный page'
        )
        assert int(callback_data[3]) == food_id, (
            'Неправильный food_id'
        )
    assert builder_data[-1][0].text == 'Добавить товар', (
        'Кнопка администатора "Добавить товар" отсутствует'
        'или имеет неправильный текст'
    )
    admin_callback = builder_data[-1][0].callback_data.split(':')
    assert admin_callback[0] == 'food', (
        'Неправильный класс CallbackFactory '
        'у кнопки администратора "Добавить Товар"'
    )
    assert admin_callback[1] == 'create_preview', (
        'Неправильный action '
        'у кнопки администратора "Добавить Товар"'
    )
    check_paginator(builder_data[-2], FOOD_DATA['page'])


@pytest.mark.asyncio
async def test_food_info():
    food_data = await food_info(FOOD_DATA['results'][0])
    expected_text = ('<b>test</b> \n'
                     'test \n'
                     'Вес: 1 г. \n'
                     'Цена: 1 ₽')
    assert 'text' in food_data, (
        'поле "text" отсутствует'
    )
    assert 'image' in food_data, (
        'поле "image" отсутствует'
    )
    assert food_data['text'] == expected_text, (
        'Текст сообщения не соответствует ожидаемому'
    )
    assert isinstance(food_data['image'], URLInputFile), (
        'Изображение не соответствует ожидаемому'
    )


@pytest.mark.asyncio
async def test_food_builder():
    food = FOOD_DATA['results'][0]
    cart = CART_DATA
    cart_data = cart['results'][0]
    builder = await food_builder(food=food,
                                 cart=cart,
                                 page=2,
                                 admin=True)
    assert isinstance(builder, InlineKeyboardBuilder), (
        'Функция должна вернуть класс InlineKeyboardBuilder'
    )
    builder_data = builder.as_markup()
    builder_data = builder_data.inline_keyboard
    assert len(builder_data) == 5, (
        'Неправильное количество строк кнопок в builder'
    )
    amount = cart_data['amount']
    total_price = amount * food['price']
    exp_text = [
        (f'{amount} шт. ({total_price} ₽)',),
        ('➖', '➕'),
        ('↩️',),
        ('Редактировать товар',),
        ('Удалить товар',),
    ]
    exp_action = [
        (f'cartcreate',),
        ('cartremove', 'cartcreate'),
        ('foodget_all',),
        ('update_preview',),
        ('remove_preview',),
    ]
    for row_number in range(len(builder_data)):
        for btn_number in range(len(builder_data[row_number])):
            btn = builder_data[row_number][btn_number]
            print(btn)
            assert (btn.text ==
                    exp_text[row_number][btn_number]), (
                f'Кнопка номер {btn_number} в ряду {row_number}'
                'Не соответствует ожидаемому'
            )
            callback_data = btn.callback_data.split(':')
            assert callback_data[0] == 'food', (
                f'Кнопка номер {btn_number} в ряду {row_number}'
                'Неправильный класс CallbackFactory'
            )
            assert callback_data[1] == exp_action[row_number][btn_number], (
                f'Кнопка номер {btn_number} в ряду {row_number}'
                'Неправильный food_action'
            )
            print(callback_data)
            exp_id = food['id']
            if btn.text == '↩️':
                pass
            assert int(callback_data[2]) == food['id'], (
                f'Кнопка номер {btn_number} в ряду {row_number}'
                'Неправильный food_id'
            )

    # for food_number in range(len(food_list)):
    #     food_id = food_list[food_number]['id']
    #     callback_data = builder_data[food_number][0].callback_data.split(':')
    #     expected_btn_txt = (f"{food_list[food_number]['name']} "
    #                         f"- {food_list[food_number]['price']} ₽")
    #     assert builder_data[food_number][0].text == expected_btn_txt, (
    #         'Неправильное название кнопок'
    #     )
    #
    # assert builder_data[-1][0].text == 'Добавить товар', (
    #     'Кнопка администатора "Добавить товар" отсутствует'
    #     'или имеет неправильный текст'
    # )
    # admin_callback = builder_data[-1][0].callback_data.split(':')
    # assert admin_callback[0] == 'food', (
    #     'Неправильный класс CallbackFactory '
    #     'у кнопки администратора "Добавить Товар"'
    # )
    # assert admin_callback[1] == 'create_preview', (
    #     'Неправильный action '
    #     'у кнопки администратора "Добавить Товар"'
    # )