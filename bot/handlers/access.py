import logging
from http import HTTPStatus
from typing import Optional

from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, URLInputFile
from aiogram.utils.markdown import hide_link
from aiogram import Router, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, Text
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from magic_filter import F
from utils import get_api_answer, post_api_answer, delete_api_answer, patch_api_answer
from middlewares.role import IsGuestMessageMiddleware

from bot.utils import check_phone_number

router = Router()
router.message.middleware(IsGuestMessageMiddleware())


class Access(StatesGroup):
    name = State()
    phone = State()


@router.message(Text('Заявка'))
async def access(
        message: types.Message,
        state: FSMContext
):
    await message.answer(
        "Для получения доступа напишите свое Имя Фамилию \n"
        "Пример: Иван Иванов"
    )
    await state.set_state(Access.name)


@router.message(Access.name)
async def callbacks_edit_food_name_confirm(
        message: Message,
        state: FSMContext,
        bot: Bot):
    await state.update_data(name=message.text)
    await message.answer(
        "А так же требуется ваш номер телефона \n"
        "Пример: +79781234567"
    )
    await state.set_state(Access.phone)


@router.message(Access.phone)
async def callbacks_edit_food_name_confirm(
        message: Message,
        state: FSMContext,
        bot: Bot):
    number = check_phone_number(message.text)
    if not number.isdigit():
        await message.answer(
            "Введите номер телефона в правильном формате \n"
            "Пример: +79781234567"
        )
        await state.set_state(Access.phone)
    else:
        await state.update_data(phone=number)
        data = await state.get_data()
        patch_api_answer(f'users/{message.from_user.id}/',
                         data={
                             'name': data['name'],
                             'phone_number': data['phone'],
                             'request_for_access': True
                         })
        await message.answer(
            'Ваша заявка отправлена!'
        )
        # TODO - отправка сообщения админу
