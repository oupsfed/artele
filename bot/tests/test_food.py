import asyncio
import pytest

from service.food import menu_builder

from .utils import check_paginator, FOOD_DATA

pytest_plugins = ('pytest_asyncio',)


@pytest.mark.asyncio
async def test_menu_builder():
    food_list = FOOD_DATA['results']
    builder = await menu_builder(FOOD_DATA,
                                 admin=True)
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
