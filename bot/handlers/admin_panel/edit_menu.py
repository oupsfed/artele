import base64
import io
import os
from typing import Optional

import requests
from aiogram import Router, types, F, Bot
from aiogram.filters import Text
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, URLInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from django.core.files.base import ContentFile

from utils import get_api_answer, post_api_answer, delete_api_answer, patch_api_answer

from bot.middlewares.role import IsAdminMessageMiddleware

FOOD_COL = {
    'name': 'название',
    'description': 'описание',
    'weight': 'масса',
    'price': 'цена',
    'image': 'фото'
}

router = Router()
router.message.middleware(IsAdminMessageMiddleware())


class EditFood(StatesGroup):
    name = State()


class AddFood(StatesGroup):
    name = State()
    description = State()
    weight = State()
    price = State()
    image = State()


class SettingsCallbackFactory(CallbackData, prefix='settings'):
    action: str
    food_id: Optional[int]
    food_column: Optional[str]
    page: Optional[int]


@router.message(Text('Редактирование меню'))
async def finding_lots(message: types.Message):
    main_message = get_api_answer('message/menu/')
    main_message = main_message.json()
    answer = get_api_answer('food/')
    answer = answer.json()
    food_list = answer['results']
    builder = InlineKeyboardBuilder()
    for food in food_list:
        builder.button(
            text=f"{food['name']} - {food['price']} ₽",
            callback_data=SettingsCallbackFactory(
                action='show_food',
                food_id=food['id'],
                page=1)
        )
    if answer['next']:
        builder.button(
            text="Вперед ➡️",
            callback_data=SettingsCallbackFactory(
                action='show_page',
                page=2)
        )
    builder.button(
        text=f"Добавить товар",
        callback_data=SettingsCallbackFactory(
            action='add_food',
            page=1)
    )
    builder.adjust(1)
    await message.answer(
        main_message['text'],
        reply_markup=builder.as_markup()
    )


@router.callback_query(SettingsCallbackFactory.filter(F.action == 'add_food'))
async def callbacks_add_food_name(
        callback: types.CallbackQuery,
        callback_data: SettingsCallbackFactory,
        state: FSMContext
):
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Отмена',
        callback_data=SettingsCallbackFactory(
            action='show_page',
            page=1)
    )
    await callback.message.answer(
        text=f'Введите Название',
        reply_markup=builder.as_markup()
    )
    await state.set_state(AddFood.name)


@router.message(AddFood.name)
async def callbacks_edit_food_name_confirm(
        message: Message,
        state: FSMContext,
        bot: Bot):
    await state.update_data(name=message.text)
    data = await state.get_data()
    print(data)
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Отмена',
        callback_data=SettingsCallbackFactory(
            action='show_page',
            page=1)
    )
    await message.answer(
        text=f'Введите Описание',
        reply_markup=builder.as_markup()
    )
    await state.set_state(AddFood.description)


@router.message(AddFood.description)
async def callbacks_edit_food_name_confirm(
        message: Message,
        state: FSMContext,
        bot: Bot):
    await state.update_data(description=message.text)
    data = await state.get_data()
    print(data)
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Отмена',
        callback_data=SettingsCallbackFactory(
            action='show_page',
            page=1)
    )
    await message.answer(
        text=f'Введите вес товара в граммах',
        reply_markup=builder.as_markup()
    )
    await state.set_state(AddFood.weight)


@router.message(AddFood.weight)
async def callbacks_edit_food_name_confirm(
        message: Message,
        state: FSMContext,
        bot: Bot):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    print(data)
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Отмена',
        callback_data=SettingsCallbackFactory(
            action='show_page',
            page=1)
    )
    await message.answer(
        text=f'Введите цену товара',
        reply_markup=builder.as_markup()
    )
    await state.set_state(AddFood.price)


@router.message(AddFood.price)
async def callbacks_edit_food_name_confirm(
        message: Message,
        state: FSMContext,
        bot: Bot):
    await state.update_data(price=message.text)
    data = await state.get_data()
    print(data)
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Отмена',
        callback_data=SettingsCallbackFactory(
            action='show_page',
            page=1)
    )
    await message.answer(
        text=f'Добавьте фото товара',
        reply_markup=builder.as_markup()
    )
    await state.set_state(AddFood.image)


@router.message(AddFood.image)
async def callbacks_edit_food_name_confirm(
        message: Message,
        state: FSMContext,
        bot: Bot):
    direction = f"tmp/{message.photo[-1].file_id}.jpg"
    await bot.download(
        message.photo[-1],
        destination=direction
    )
    with open(direction, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    image_string = encoded_string.decode('utf-8')
    os.remove(direction)
    await state.update_data(image=image_string)
    data = await state.get_data()
    post_api_answer('food/',
                    data=data)
    text = (f'Вы успешно создали товар: \n'
            f'Название: {data["name"]} \n'
            f'Описание: {data["description"]} \n'
            f'Вес: {data["weight"]} \n'
            f'Цена: {data["price"]}')
    await message.answer(text)


@router.callback_query(SettingsCallbackFactory.filter(F.action == 'show_page'))
async def show_food_page(
        callback: types.CallbackQuery,
        callback_data: SettingsCallbackFactory
):
    main_message = get_api_answer('message/menu/')
    main_message = main_message.json()
    page = 1
    if callback_data.page:
        page = callback_data.page

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
            callback_data=SettingsCallbackFactory(
                action='show_food',
                food_id=food['id'],
                page=page)
        )
        rows.append(1)
    page_buttons = 0
    if answer['previous']:
        builder.button(
            text="Назад ⬅️",
            callback_data=SettingsCallbackFactory(
                action='show_page',
                page=page - 1)
        )
        page_buttons += 1
    if answer['next']:
        builder.button(
            text="Вперед ➡️",
            callback_data=SettingsCallbackFactory(
                action='show_page',
                page=page + 1)
        )
        page_buttons += 1
    rows.append(page_buttons)
    builder.adjust(*rows)
    await callback.message.answer(
        main_message['text'],
        reply_markup=builder.as_markup()
    )


@router.callback_query(SettingsCallbackFactory.filter(F.action == 'show_food'))
async def callbacks_show_food(
        callback: types.CallbackQuery,
        callback_data: SettingsCallbackFactory
):
    page = callback_data.page
    answer = get_api_answer(f'food/{callback_data.food_id}')
    food = answer.json()
    text = (f"<b>{food['name']}</b> \n"
            f"{food['description']} \n"
            f"Вес: {food['weight']} г. \n"
            f"Цена: {food['price']} ₽"
            f"")
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f'Редактировать',
        callback_data=SettingsCallbackFactory(
            action='edit_food_menu',
            food_id=food['id'])
    )
    builder.button(
        text=f'Удалить',
        callback_data=SettingsCallbackFactory(
            action='delete_food',
            food_id=food['id'])
    )
    builder.button(
        text='Назад',
        callback_data=SettingsCallbackFactory(
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


@router.callback_query(SettingsCallbackFactory.filter(F.action == 'edit_food_menu'))
async def callbacks_show_food(
        callback: types.CallbackQuery,
        callback_data: SettingsCallbackFactory
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
        text=f'Изменить название',
        callback_data=SettingsCallbackFactory(
            action='edit_food',
            food_column='name',
            food_id=food['id'])
    )
    builder.button(
        text=f'Изменить описание',
        callback_data=SettingsCallbackFactory(
            action='edit_food',
            food_column='description',
            food_id=food['id'])
    )
    builder.button(
        text=f'Изменить вес',
        callback_data=SettingsCallbackFactory(
            action='edit_food',
            food_column='weight',
            food_id=food['id'])
    )
    builder.button(
        text=f'Изменить цену',
        callback_data=SettingsCallbackFactory(
            action='edit_food',
            food_column='price',
            food_id=food['id'])
    )
    builder.button(
        text=f'Изменить фото',
        callback_data=SettingsCallbackFactory(
            action='edit_food',
            food_column='image',
            food_id=food['id'])
    )
    builder.button(
        text=f'Назад',
        callback_data=SettingsCallbackFactory(
            action='show_food',
            food_id=food['id'])
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


@router.callback_query(
    SettingsCallbackFactory.filter(F.action == 'edit_food'))
async def callbacks_edit_food_name(
        callback: types.CallbackQuery,
        callback_data: SettingsCallbackFactory,
        state: FSMContext
):
    await state.update_data(id=callback_data.food_id,
                            col=callback_data.food_column)
    await callback.message.answer(
        text=f'Введите (Пришлите) {FOOD_COL[callback_data.food_column]}'
    )
    await state.set_state(EditFood.name)


@router.message(EditFood.name)
async def callbacks_edit_food_name_confirm(
        message: Message,
        state: FSMContext,
        bot: Bot):
    data = await state.get_data()
    if data['col'] == 'image':
        direction = f"tmp/{message.photo[-1].file_id}.jpg"
        await bot.download(
            message.photo[-1],
            destination=direction
        )
        with open(direction, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        data['name'] = encoded_string.decode('utf-8')
        os.remove(direction)
    else:
        await state.update_data(name=message.text)
        data = await state.get_data()
    answer = patch_api_answer(f'food/{data["id"]}/',
                              data={
                                  data['col']: data['name']
                              })
    await message.answer(f'{FOOD_COL[data["col"]]} успешно изменено')


@router.callback_query(SettingsCallbackFactory.filter(F.action == 'delete_food'))
async def callbacks_delete_food(
        callback: types.CallbackQuery,
        callback_data: SettingsCallbackFactory
):
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f'Удалить',
        callback_data=SettingsCallbackFactory(
            action='delete_food_confirm',
            food_id=callback_data.food_id)
    )
    builder.button(
        text=f'Отмена',
        callback_data=SettingsCallbackFactory(
            action='show_food',
            food_id=callback_data.food_id)
    )
    await callback.message.edit_reply_markup(
        reply_markup=builder.as_markup()
    )


@router.callback_query(SettingsCallbackFactory.filter(F.action == 'delete_food_confirm'))
async def callbacks_delete_food(
        callback: types.CallbackQuery,
        callback_data: SettingsCallbackFactory
):
    delete_api_answer(f'food/{callback_data.food_id}')
    await callback.message.answer(
        'Товар успешно удален')
    await callback.message.delete()
