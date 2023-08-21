from aiogram import Router, types
from aiogram.filters import Text
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from middlewares.role import IsAdminMessageMiddleware

router = Router()
router.message.middleware(IsAdminMessageMiddleware())


@router.message(Text('Панель администратора'))
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
        types.KeyboardButton(text="Панель администратора"),
    )
    await message.answer('Вы вышли из панели администратора',
                         parse_mode='HTML',
                         reply_markup=builder.as_markup(resize_keyboard=True))
