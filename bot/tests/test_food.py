import asyncio
import base64
import os
import shutil

import pytest
from aiogram.types import URLInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from service.food import (FOOD_COL, add_food_builder, admin_edit_food_builder,
                          encode_image, food_builder, food_info, menu_builder)

from .fixtures.food import CART_DATA, FOOD_DATA
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
        assert int(callback_data[2]) == food_id, (
            'Неправильный food_id'
        )
        assert int(callback_data[3]) == FOOD_DATA['page'], (
            'Неправильный page'
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
        'При отсутсвии изображения на товаре, '
        'должно быть изображение по умолчанию'
    )
    food_data = await food_info(FOOD_DATA['results'][2])
    assert isinstance(food_data['image'], URLInputFile), (
        'При наличии изображения на товаре, '
        'должен возвращаться объект URLInputFile'
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
        ('cartcreate',),
        ('cartremove', 'cartcreate'),
        ('foodget_all',),
        ('update_preview',),
        ('remove_preview',),
    ]
    exp_id = [
        (str(food['id']),),
        (str(food['id']), str(food['id'])),
        ('',),
        (str(food['id']),),
        (str(food['id']),),
    ]
    for row_number in range(len(builder_data)):
        for btn_number in range(len(builder_data[row_number])):
            btn = builder_data[row_number][btn_number]
            assert (btn.text ==
                    exp_text[row_number][btn_number]), (
                (f'Кнопка {btn.text}  не соответствует ожидаемому - '
                 'Не соответствует ожидаемому')
            )
            callback_data = btn.callback_data.split(':')
            assert callback_data[0] == 'food', (
                (f'Кнопка {btn.text}  не соответствует ожидаемому - '
                 'Неправильный класс CallbackFactory')
            )
            assert callback_data[1] == exp_action[row_number][btn_number], (
                (f'Кнопка {btn.text}  не соответствует ожидаемому - '
                 'Неправильный food_action')
            )
            assert callback_data[2] == exp_id[row_number][btn_number], (
                (f'Кнопка {btn.text}  не соответствует ожидаемому - '
                 'Неправильный food_id')
            )

    builder = await food_builder(food=food,
                                 cart=cart,
                                 page=2,
                                 admin=False)
    builder_data = builder.as_markup()
    builder_data = builder_data.inline_keyboard
    assert len(builder_data) == 3, (
        ('Неправильное количество строк кнопок в builder если '
         'пользователь не администратор')
    )


@pytest.mark.asyncio
async def test_edit_food_builder():
    food = FOOD_DATA['results'][0]
    builder = await admin_edit_food_builder(
        food_id=food['id']
    )
    assert isinstance(builder, InlineKeyboardBuilder), (
        'Функция должна вернуть класс InlineKeyboardBuilder'
    )
    builder_data = builder.as_markup()
    builder_data = builder_data.inline_keyboard
    assert len(builder_data) == len(FOOD_COL) + 1, (
        'Неправильное количество строк кнопок в builder'
    )
    i = 0
    for col, name in FOOD_COL.items():
        row = builder_data[i]
        assert len(row) == 1, (
            'В ряду должна быть одна кнопка'
        )
        btn = builder_data[i][0]
        exp_text = f'Изменить {name}'
        assert btn.text == exp_text, (
            f'В кнопке {btn.text} неправильный текст'
        )
        callback_data = btn.callback_data.split(':')
        assert callback_data[0] == 'food', (
            (f'Кнопка {btn.text}  не соответствует ожидаемому - '
             'Неправильный класс CallbackFactory')
        )
        assert callback_data[1] == 'update_column', (
            (f'Кнопка {btn.text}  не соответствует ожидаемому - '
             'Неправильный food_action')
        )
        assert callback_data[2] == str(food['id']), (
            (f'Кнопка {btn.text}  не соответствует ожидаемому - '
             'Неправильный food_id')
        )
        assert callback_data[3] == '1', (
            (f'Кнопка {btn.text}  не соответствует ожидаемому - '
             'Не установлено значение page по умолчанию')
        )
        assert callback_data[4] == col, (
            (f'Кнопка {btn.text}  не соответствует ожидаемому - '
             'Неправильный column')
        )
        i += 1
    back_btn = builder_data[-1][0]
    callback_data = back_btn.callback_data.split(':')
    print(back_btn)
    assert back_btn.text == 'Назад', (
        f'В кнопке {back_btn.text} неправильный текст'
    )
    assert callback_data[0] == 'food', (
        (f'Кнопка {back_btn.text}  не соответствует ожидаемому - '
         'Неправильный класс CallbackFactory')
    )
    assert callback_data[1] == 'foodget', (
        (f'Кнопка {back_btn.text}  не соответствует ожидаемому - '
         'Неправильный food_action')
    )
    assert callback_data[2] == str(food['id']), (
        (f'Кнопка {back_btn.text}  не соответствует ожидаемому - '
         'Неправильный food_id')
    )
    assert callback_data[3] == '1', (
        (f'Кнопка {back_btn.text}  не соответствует ожидаемому - '
         'Не установлено значение page по умолчанию')
    )


@pytest.mark.asyncio
async def test_add_food_builder():
    builder = await add_food_builder()
    assert isinstance(builder, InlineKeyboardBuilder), (
        'Функция должна вернуть класс InlineKeyboardBuilder'
    )
    builder_data = builder.as_markup()
    builder_data = builder_data.inline_keyboard
    assert len(builder_data) == 1, (
        'Неправильное количество строк кнопок в builder'
    )
    back_btn = builder_data[-1][0]
    callback_data = back_btn.callback_data.split(':')
    assert back_btn.text == 'Отмена', (
        f'В кнопке {back_btn.text} неправильный текст'
    )
    assert callback_data[0] == 'food', (
        (f'Кнопка {back_btn.text}  не соответствует ожидаемому - '
         'Неправильный класс CallbackFactory')
    )
    assert callback_data[1] == 'foodget_all', (
        (f'Кнопка {back_btn.text}  не соответствует ожидаемому - '
         'Неправильный food_action')
    )
    assert callback_data[3] == '1', (
        (f'Кнопка {back_btn.text}  не соответствует ожидаемому - '
         'Не установлено значение page по умолчанию')
    )


@pytest.mark.asyncio
async def test_download_encode_image():
    main_image = 'tests/fixtures/test_image.png'
    tmp_image = 'tests/fixtures/tmp.png'
    shutil.copy2(main_image, tmp_image)
    encode_data = await encode_image(tmp_image)
    assert isinstance(encode_data, str), (
        'Функция должна возвращать кодированную строку'
    )
    assert os.path.isfile(tmp_image) is False, (
        'После выполнения функции изображение должно удалиться '
        'с сервера'
    )
    with open(main_image, "rb") as img_file:
        assert encode_data == base64.b64encode(
            img_file.read()).decode('utf-8'), (
            'Изображение неправильно кодируется в base64'
        )