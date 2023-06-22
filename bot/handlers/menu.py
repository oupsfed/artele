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


class MenuCallbackFactory(CallbackData, prefix='menu'):
    action: str
    food_id: Optional[int]
    page: Optional[int]


@router.message(Text('Меню'))
async def menu(message: types.Message):
    main_message = get_api_answer('message/menu/')
    main_message = main_message.json()
    answer = get_api_answer('food/')
    answer = answer.json()
    food_list = answer['results']
    builder = InlineKeyboardBuilder()
    for food in food_list:
        builder.button(
            text=f"{food['name']} - {food['price']} ₽",
            callback_data=MenuCallbackFactory(
                action='show',
                food_id=food['id'],
                page=1)
        )
    if answer['next']:
        builder.button(
            text="➡️",
            callback_data=MenuCallbackFactory(
                action='show_page',
                page=2)
        )
    builder.adjust(1)
    await message.answer(
        main_message['text'],
        reply_markup=builder.as_markup()
    )


@router.callback_query(MenuCallbackFactory.filter(F.action == 'show'))
async def callbacks_show_food(
        callback: types.CallbackQuery,
        callback_data: MenuCallbackFactory
):
    answer = get_api_answer(f'food/{callback_data.food_id}')
    food = answer.json()
    text = (f"<b>{food['name']}</b> \n"
            f"{food['description']} \n"
            f"Вес: {food['weight']} г. \n"
            f"Цена: {food['price']} ₽"
            f"")
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f'Добавить в корзину',
        callback_data='add'
    )
    builder.button(
        text='Назад',
        callback_data=MenuCallbackFactory(
            action='show_page',
            page=callback_data.page)
    )
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


@router.callback_query(MenuCallbackFactory.filter(F.action == 'show_page'))
async def callbacks_show_page(
        callback: types.CallbackQuery,
        callback_data: MenuCallbackFactory
):
    main_message = get_api_answer('message/menu/')
    main_message = main_message.json()
    page = callback_data.page
    answer = get_api_answer('food/',
                            params={
                                'page': page
                            })
    answer = answer.json()
    food_list = answer['results']
    builder = InlineKeyboardBuilder()
    for food in food_list:
        builder.button(
            text=f"{food['name']} - {food['price']} ₽",
            callback_data=MenuCallbackFactory(
                action='show',
                food_id=food['id'],
                page=page)
        )
    if answer['previous']:
        builder.button(
            text="Назад ⬅️",
            callback_data=MenuCallbackFactory(
                action='show_page',
                page=page-1)
        )
    if answer['next']:
        builder.button(
            text="Вперед ➡️",
            callback_data=MenuCallbackFactory(
                action='show_page',
                page=page+1)
        )
    builder.adjust(1)
    await callback.message.answer(
        main_message['text'],
        reply_markup=builder.as_markup()
    )
    await callback.message.delete()
