import base64
import os
from typing import Optional

from aiogram.types import URLInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from service.cart import cart_action
from utils import Action, ArteleCallbackData, paginate_builder

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
    column: Optional[str]


async def menu_builder(json_response: dict,
                       pagination: bool = True,
                       admin: bool = False) -> InlineKeyboardBuilder:
    """
    Функция формирования кнопок для меню товаров.

            Parameters:
                    json_response (dict) : словарь ответа API товаров
                    pagination (bool) : включена ли пагинация в проекте
                    admin (bool): подключать ли функции администратора

            Returns:
                    builder (InlineKeyboardBuilder): объект кнопок
    """
    food_list = json_response
    page = 1
    if pagination:
        food_list = json_response['results']
        page = json_response['page']
    builder = InlineKeyboardBuilder()
    rows = []
    for food in food_list:
        builder.button(
            text=f"{food['name']} - {food['price']} ₽",
            callback_data=FoodCallbackFactory(
                action=food_action.get,
                page=page,
                id=food['id'])
        )
        rows.append(1)
    page_buttons, builder = await paginate_builder(
        json_response,
        builder,
        FoodCallbackFactory,
        food_action.get_all
    )
    if page_buttons > 0:
        rows.append(page_buttons)
    if admin:
        builder.button(
            text="Добавить товар",
            callback_data=FoodCallbackFactory(
                action=food_action.create_preview,
                page=page)
        )
        rows.append(1)
    builder.adjust(*rows)
    return builder


async def food_info(food: dict) -> dict:
    """
    Функция формирования текста сообщения определенного товара.

            Parameters:
                    food (dict) : словарь товара

            Returns:
                    data (dict): словарь содержащий текст и изображение товара
    """
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


async def food_builder(cart: dict,
                       food: dict,
                       page: int = 1,
                       admin: bool = False) -> InlineKeyboardBuilder:
    """
    Функция формирования кнопок для определенного товара.

            Parameters:
                    cart (dict) : словарь ответа API корзины
                    food (bool) : словаь определенного товара
                    page (int) : страница с которой перешли в карточку товара
                    admin (bool): подключать ли функции администратора

            Returns:
                    builder (InlineKeyboardBuilder): объект кнопок
    """
    amount = 0
    food_price = food['price']
    if len(cart['results']) > 0:
        cart = cart['results'][0]
        amount = cart['amount']
    builder = InlineKeyboardBuilder()
    rows = []
    builder.button(
        text=f'{amount} шт. ({amount * food_price} ₽)',
        callback_data=FoodCallbackFactory(
            action=cart_action.create,
            id=food['id']
        )
    )
    rows.append(1)
    builder.button(
        text='➖',
        callback_data=FoodCallbackFactory(
            action=cart_action.remove,
            id=food['id']
        )
    )
    builder.button(
        text='➕',
        callback_data=FoodCallbackFactory(
            action=cart_action.create,
            id=food['id']
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
    if admin:
        builder.button(
            text='Редактировать товар',
            callback_data=FoodCallbackFactory(
                action=food_action.update_preview,
                id=food['id'],
                page=page
            )
        )
        rows.append(1)
        builder.button(
            text='Удалить товар',
            callback_data=FoodCallbackFactory(
                action=food_action.remove_preview,
                id=food['id'],
                page=page)
        )
        rows.append(1)
    builder.adjust(*rows)
    return builder


async def admin_edit_food_builder(food_id: int,
                                  page: int = 1):
    """
    Функция формирования кнопок для редактирования товара.

            Parameters:
                    food_id (int) : id объекта Food
                    page (int) : страница для возврата к меню

            Returns:
                    builder (InlineKeyboardBuilder): объект кнопок
    """
    builder = InlineKeyboardBuilder()
    for col, name in FOOD_COL.items():
        builder.button(
            text=f'Изменить {name}',
            callback_data=FoodCallbackFactory(
                action=food_action.update_column,
                column=col,
                id=food_id)
        )

    builder.button(
        text='Назад',
        callback_data=FoodCallbackFactory(
            action=food_action.get,
            id=food_id,
            page=page)
    )
    builder.adjust(1)
    return builder


async def add_food_builder():
    """
    Функция формирования кнопок для добавления товара.

            Parameters:

            Returns:
                    builder (InlineKeyboardBuilder): объект кнопок
    """
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Отмена',
        callback_data=FoodCallbackFactory(
            action=food_action.get_all)
    )
    return builder


async def encode_image(img_dir: str) -> str:
    """
    Функция кодирования изображения в base64.

            Parameters:
                    img_dir (str) : путь к загруженному изображению

            Returns:
                    str (str): закодированную base64 строку изображения
    """
    with open(img_dir, "rb") as img_file:
        encoded_string = base64.b64encode(img_file.read())
    os.remove(img_dir)
    return encoded_string.decode('utf-8')
