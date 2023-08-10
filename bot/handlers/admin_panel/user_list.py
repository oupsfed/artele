import base64
import io
import logging
import os
from http import HTTPStatus
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

router = Router()
router.message.middleware(IsAdminMessageMiddleware())


class SendMessage(StatesGroup):
    direct = State()
    all = State()


class AddFood(StatesGroup):
    name = State()
    description = State()
    weight = State()
    price = State()
    image = State()


class UserListCallbackFactory(CallbackData, prefix='user_list'):
    action: str
    user_id: Optional[int]
    page: Optional[int]


@router.message(Text('Оповещение пользователей'))
async def user_list(message: types.Message):
    answer = get_api_answer('users/',
                            params={
                                'role': 'USER'
                            }).json()
    user_data = answer['results']
    builder = InlineKeyboardBuilder()
    text = 'У вас нет авторизированных пользователей!'
    if answer['count'] > 0:
        builder.button(
            text='Отправить сообщение всем пользователям',
            callback_data=UserListCallbackFactory(
                action='send_message_to_all',
            )
        )
        text = 'Список пользователей:'
    for user in user_data:
        builder.button(
            text=user['name'],
            callback_data=UserListCallbackFactory(
                action='show',
                user_id=user['telegram_chat_id'],
                page=1)
        )
    if answer['next']:
        builder.button(
            text="Вперед ➡️",
            callback_data=UserListCallbackFactory(
                action='show_page',
                page=2)
        )
    builder.adjust(1)
    await message.answer(
        text,
        reply_markup=builder.as_markup()
    )


@router.callback_query(UserListCallbackFactory.filter(F.action == 'show'))
async def callbacks_show_request(
        callback: types.CallbackQuery,
        callback_data: UserListCallbackFactory
):
    answer = get_api_answer(f'users/{callback_data.user_id}')
    user = answer.json()
    text = (f"Имя: {user['name']} \n"
            f"Телефон: {user['phone_number']} \n"
            )
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f'Отправить сообщение',
        callback_data=UserListCallbackFactory(
            action='send_message',
            user_id=user['telegram_chat_id'],
        )
    )
    builder.button(
        text='Заблокировать',
        callback_data=UserListCallbackFactory(
            action='block_user',
            user_id=user['telegram_chat_id'],
        )
    )
    builder.button(
        text='Назад',
        callback_data=UserListCallbackFactory(
            action='show_page',
            page=callback_data.page)
    )
    builder.adjust(1)

    await callback.message.answer(
        text,
        reply_markup=builder.as_markup()
    )
    await callback.message.delete()


@router.callback_query(UserListCallbackFactory.filter(F.action == 'block_user'))
async def callbacks_accepct_request(
        callback: types.CallbackQuery,
        callback_data: UserListCallbackFactory,
        bot: Bot
):
    answer = patch_api_answer(f'users/{callback_data.user_id}/',
                              data={
                                  'role': 'GUEST',
                                  'request_for_access': False
                              })
    main_message = ''
    if answer.status_code == HTTPStatus.OK:
        text = 'Блокировка прошла успешно'
        logging.info(text)
    else:
        text = f'Произошла ошибка при блокировке {answer.json()}'
    main_message += f'{text}\n'
    try:
        await bot.send_message(
            chat_id=callback_data.user_id,
            text='Вы были заблокированы!'
        )
    except Exception as error:
        text = f'Произошла ошибка при отправке сообщения пользователю \n {error}'
        logging.error(text)
        main_message += text
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f'Назад',
        callback_data=UserListCallbackFactory(
            action='show_page',
            page=callback_data.page)
    )
    builder.adjust(1)
    await callback.message.answer(main_message,
                                  reply_markup=builder.as_markup())
    await callback.message.delete()


@router.callback_query(UserListCallbackFactory.filter(F.action == 'show_page'))
async def callbacks_accepct_request(
        callback: types.CallbackQuery,
        callback_data: UserListCallbackFactory,
        bot: Bot
):
    page = callback_data.page
    answer = get_api_answer('users/',
                            params={
                                'role': 'USER',
                                'page': page
                            }).json()
    requests_data = answer['results']
    builder = InlineKeyboardBuilder()
    rows = []
    for user in requests_data:
        builder.button(
            text=user['name'],
            callback_data=UserListCallbackFactory(
                action='show',
                user_id=user['telegram_chat_id'],
                page=1)
        )
        rows.append(1)
    page_buttons = 0
    if answer['previous']:
        builder.button(
            text="Назад ⬅️",
            callback_data=UserListCallbackFactory(
                action='show_page',
                page=page - 1)
        )
        page_buttons += 1
    if answer['next']:
        builder.button(
            text="Вперед ➡️",
            callback_data=UserListCallbackFactory(
                action='show_page',
                page=page + 1)
        )
        page_buttons += 1
    if page_buttons > 0:
        rows.append(page_buttons)
    builder.adjust(*rows)
    await callback.message.answer(
        "Список пользователей",
        reply_markup=builder.as_markup()
    )
    await callback.message.delete()


@router.callback_query(UserListCallbackFactory.filter(F.action == 'send_message'))
async def callbacks_send_message(
        callback: types.CallbackQuery,
        callback_data: UserListCallbackFactory,
        state: FSMContext
):
    await callback.message.answer(
        text=f'Введите сообщение',
    )
    await state.update_data(user_id=callback_data.user_id)
    await state.set_state(SendMessage.direct)


@router.callback_query(UserListCallbackFactory.filter(F.action == 'send_message_to_all'))
async def callbacks_send_message(
        callback: types.CallbackQuery,
        callback_data: UserListCallbackFactory,
        state: FSMContext
):
    await callback.message.answer(
        text=f'Введите сообщение',
    )
    await state.set_state(SendMessage.all)


@router.message(SendMessage.direct)
async def callbacks_send_message_direct(
        message: Message,
        state: FSMContext,
        bot: Bot):
    data = await state.get_data()
    try:
        await bot.send_message(
            chat_id=data['user_id'],
            text=message.text
        )
        text = 'Сообщение успешно отправлено'
    except Exception as error:
        text = f'Произошла ошибка при отправке сообщения пользователю \n {error}'
        logging.error(text)
    await state.clear()
    await message.answer(text)


@router.message(SendMessage.all)
async def callbacks_send_message_all(
        message: Message,
        state: FSMContext,
        bot: Bot):
    answer = get_api_answer('authorized/').json()
    success = []
    for user in answer:
        try:
            await bot.send_message(
                chat_id=user['telegram_chat_id'],
                text=message.text
            )
            text = f'Сообщение успешно отправлено пользователю - {user["name"]}'
            success.append(user['name'])
            logging.info(text)
        except Exception as error:
            text = f'Произошла ошибка при отправке сообщения пользователю {user["name"]} \n{error}'
            logging.error(text)
            await message.answer(text)
    await state.clear()
    if len(success) > 0:
        await message.answer(f'Сообщения отправлены пользователям: {" ".join(success)}')
