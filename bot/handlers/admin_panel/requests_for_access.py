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


class AccessCallbackFactory(CallbackData, prefix='access'):
    action: str
    user_id: Optional[int]
    page: Optional[int]


@router.message(Text('Заявки на вступление'))
async def access_list(message: types.Message):
    answer = get_api_answer('users/',
                            params={
                                'request_for_access': True
                            }).json()
    requests_data = answer['results']
    print(requests_data)
    builder = InlineKeyboardBuilder()
    for user in requests_data:
        builder.button(
            text=user['name'],
            callback_data=AccessCallbackFactory(
                action='show',
                user_id=user['telegram_chat_id'],
                page=1)
        )
    if answer['next']:
        builder.button(
            text="Вперед ➡️",
            callback_data=AccessCallbackFactory(
                action='show_page',
                page=2)
        )
    builder.adjust(1)
    await message.answer(
        "Заявки на доступ к оформлению заказа",
        reply_markup=builder.as_markup()
    )


@router.callback_query(AccessCallbackFactory.filter(F.action == 'show'))
async def callbacks_show_request(
        callback: types.CallbackQuery,
        callback_data: AccessCallbackFactory
):
    answer = get_api_answer(f'users/{callback_data.user_id}')
    user = answer.json()
    text = (f"Имя: {user['name']} \n"
            f"Телефон: {user['phone_number']} \n"
            )
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f'Одобрить',
        callback_data=AccessCallbackFactory(
            action='request_accept',
            user_id=user['telegram_chat_id'],
            page=callback_data.page)
    )
    builder.button(
        text='Отменить',
        callback_data=AccessCallbackFactory(
            action='request_decline',
            user_id=user['telegram_chat_id'],
            page=callback_data.page)
    )
    builder.button(
        text='Назад',
        callback_data=AccessCallbackFactory(
            action='show_page',
            page=callback_data.page)
    )
    builder.adjust(2, 1)

    await callback.message.answer(
        text,
        reply_markup=builder.as_markup()
    )
    await callback.message.delete()


@router.callback_query(AccessCallbackFactory.filter(F.action == 'request_accept'))
async def callbacks_accepct_request(
        callback: types.CallbackQuery,
        callback_data: AccessCallbackFactory,
        bot: Bot
):
    answer = patch_api_answer(f'users/{callback_data.user_id}/',
                              data={
                                  'role': 'USER',
                                  'request_for_access': False
                              })
    main_message = ''
    if answer.status_code == HTTPStatus.OK:
        text = 'Одобрение заявки прошло успешно'
        logging.info(text)
    else:
        text = f'Произошла ошибка при одобрении заявки {answer.json()}'
    main_message += f'{text}\n'
    try:
        await bot.send_message(
            chat_id=callback_data.user_id,
            text='Ваша заявка одобрена!'
        )
    except Exception as error:
        text = f'Произошла ошибка при отправке сообщения пользователю \n {error}'
        logging.error(text)
        main_message += text
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f'Назад',
        callback_data=AccessCallbackFactory(
            action='show_page',
            page=callback_data.page)
    )
    builder.adjust(1)
    await callback.message.answer(main_message,
                                  reply_markup=builder.as_markup())
    await callback.message.delete()


@router.callback_query(AccessCallbackFactory.filter(F.action == 'request_decline'))
async def callbacks_accepct_request(
        callback: types.CallbackQuery,
        callback_data: AccessCallbackFactory,
        bot: Bot
):
    answer = patch_api_answer(f'users/{callback_data.user_id}/',
                              data={
                                  'request_for_access': False
                              })
    main_message = ''
    if answer.status_code == HTTPStatus.OK:
        text = 'Отклонение заявки прошло успешно'
        logging.info(text)
    else:
        text = f'Произошла ошибка при отклонении заявки {answer.json()}'
    main_message += f'{text}\n'
    try:
        await bot.send_message(
            chat_id=callback_data.user_id,
            text='Ваша заявка отклонена!'
        )
    except Exception as error:
        text = f'Произошла ошибка при отправке сообщения пользователю \n {error}'
        logging.error(text)
        main_message += text
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f'Назад',
        callback_data=AccessCallbackFactory(
            action='show_page',
            page=callback_data.page)
    )
    builder.adjust(1)
    await callback.message.answer(main_message,
                                  reply_markup=builder.as_markup())
    await callback.message.delete()


@router.callback_query(AccessCallbackFactory.filter(F.action == 'show_page'))
async def callbacks_accepct_request(
        callback: types.CallbackQuery,
        callback_data: AccessCallbackFactory,
        bot: Bot
):
    page = callback_data.page
    answer = get_api_answer('users/',
                            params={
                                'request_for_access': True,
                                'page': page
                            }).json()
    requests_data = answer['results']
    builder = InlineKeyboardBuilder()
    rows = []
    for user in requests_data:
        builder.button(
            text=user['name'],
            callback_data=AccessCallbackFactory(
                action='show',
                user_id=user['telegram_chat_id'],
                page=1)
        )
        rows.append(1)
    page_buttons = 0
    if answer['previous']:
        builder.button(
            text="Назад ⬅️",
            callback_data=AccessCallbackFactory(
                action='show_page',
                page=page - 1)
        )
        page_buttons += 1
    if answer['next']:
        builder.button(
            text="Вперед ➡️",
            callback_data=AccessCallbackFactory(
                action='show_page',
                page=page + 1)
        )
        page_buttons += 1
    if page_buttons > 0:
        rows.append(page_buttons)
    builder.adjust(*rows)
    await callback.message.answer(
        "Заявки на доступ к оформлению заказа",
        reply_markup=builder.as_markup()
    )
    await callback.message.delete()
