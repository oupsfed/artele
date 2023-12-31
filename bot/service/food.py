import base64
import os
from typing import Optional

from aiogram.types import PhotoSize, URLInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from middlewares.role import is_admin
from service.cart import cart_action
from utils import Action, ArteleCallbackData, bot, get_api_answer

FOOD_COL = {
    'name': 'название',
    'description': 'описание',
    'weight': 'масса',
    'price': 'цена',
    'image': 'фото'
}

food_action: Action = Action('food')
food_action.create_preview = 'create_preview'
food_action.update_preview = 'update_preview'
food_action.update_column = 'update_column'
food_action.remove_preview = 'remove_preview'


class FoodCallbackFactory(ArteleCallbackData, prefix='food'):
    food_id: Optional[int]
    food_column: Optional[str]
    for_staff: Optional[bool] = False


async def menu_builder(page: int = 1,
                       user_id: int = None):
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
            callback_data=FoodCallbackFactory(
                action=food_action.get,
                food_id=food['id'],
                page=page)
        )
        rows.append(1)
    page_buttons = 0
    if answer['previous']:
        builder.button(
            text="⬅️",
            callback_data=FoodCallbackFactory(
                action=food_action.get_all,
                page=page - 1
            )
        )
        page_buttons += 1
    if answer['next']:
        builder.button(
            text="➡️",
            callback_data=FoodCallbackFactory(
                action=food_action.get_all,
                page=page + 1,
            )
        )
        page_buttons += 1
    if page_buttons > 0:
        rows.append(page_buttons)
    if is_admin(user_id=user_id):
        builder.button(
            text="Добавить товар",
            callback_data=FoodCallbackFactory(
                action=food_action.create_preview,
                page=page)
        )
        rows.append(1)
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
    rows = []
    builder.button(
        text=f'{amount} шт. ({amount * food_price} ₽)',
        callback_data=FoodCallbackFactory(
            action=cart_action.create,
            food_id=food_id
        )
    )
    rows.append(1)
    builder.button(
        text='➖',
        callback_data=FoodCallbackFactory(
            action=cart_action.remove,
            food_id=food_id
        )
    )
    builder.button(
        text='➕',
        callback_data=FoodCallbackFactory(
            action=cart_action.create,
            food_id=food_id
        )
    )
    rows.append(2)
    builder.button(
        text='↩️',
        callback_data=FoodCallbackFactory(
            action=food_action.get_all,
            page=page
        )
    )
    rows.append(1)
    if is_admin(user_id):
        builder.button(
            text='Редактировать товар',
            callback_data=FoodCallbackFactory(
                action=food_action.update_preview,
                food_id=food_id,
                page=page
            )
        )
        rows.append(1)
        builder.button(
            text='Удалить товар',
            callback_data=FoodCallbackFactory(
                action=food_action.remove_preview,
                food_id=food_id,
                page=page)
        )
        rows.append(1)
    builder.adjust(*rows)
    return builder


async def admin_edit_food_builder(food_id: int,
                                  page: int = 1):
    builder = InlineKeyboardBuilder()
    for col, name in FOOD_COL.items():
        builder.button(
            text=f'Изменить {name}',
            callback_data=FoodCallbackFactory(
                action=food_action.update_column,
                food_column=col,
                food_id=food_id)
        )

    builder.button(
        text='Назад',
        callback_data=FoodCallbackFactory(
            action=food_action.get,
            food_id=food_id,
            page=page)
    )
    builder.adjust(1)
    return builder


async def add_food_builder():
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Отмена',
        callback_data=FoodCallbackFactory(
            action=food_action.get)
    )
    return builder


async def download_and_encode_image(photo: PhotoSize):
    direction = f"tmp/{photo.file_id}.jpg"
    await bot.download(
        photo,
        destination=direction
    )
    with open(direction, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    os.remove(direction)
    return encoded_string.decode('utf-8')
