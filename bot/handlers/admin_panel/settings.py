from typing import Optional

from aiogram import Router, types
from aiogram.filters import Text
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

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


@router.message(Text('Настройки бота'))
async def edit_bot(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="Редактирование меню"),
        types.KeyboardButton(text='Заявки на вступление'),
    )
    builder.row(
        types.KeyboardButton(text="Оповещение пользователей"),
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