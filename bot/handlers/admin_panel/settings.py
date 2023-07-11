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

from middlewares.role import IsAdminMessageMiddleware

from bot.middlewares.role import is_admin

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


@router.message(Text('Настройки бота'))
async def edit_bot(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="Редактирование меню"),
        types.KeyboardButton(text='Заявки на вступление'),
    )
    builder.row(
        types.KeyboardButton(text="Оповещения пользователей"),
        types.KeyboardButton(text="Оформленные заказы"),
    )
    builder.row(
        types.KeyboardButton(text="Выйти из панели администратора"),
    )
    await message.answer(
        "Панель администратора",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )


@router.message(Text('Выйти из панели администратора'))
async def finding_lots(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="Меню"),
        types.KeyboardButton(text='Корзина'),
    )
    builder.row(
        types.KeyboardButton(text="Заказ"),
        types.KeyboardButton(text="Информация"),
    )
    builder.row(
        types.KeyboardButton(text="Настройки бота"),
    )
    await message.answer('Вы вышли из панели администратора',
                         parse_mode='HTML',
                         reply_markup=builder.as_markup(resize_keyboard=True))