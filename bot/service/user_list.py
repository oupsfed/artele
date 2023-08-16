from http import HTTPStatus
from typing import Optional

from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.logger import logger
from bot.service.message import send_message_to_user
from bot.utils import (Action, ArteleCallbackData, get_api_answer,
                       patch_api_answer)

user_list_actions = Action('user_list')
user_list_actions.send_direct = 'send_direct'
user_list_actions.send_to_all = 'send_to_all'


class UserListCallbackFactory(ArteleCallbackData, prefix='user_list'):
    user_id: Optional[int]


async def user_list_builder(page: int = 1):
    answer = get_api_answer('users/',
                            params={
                                'role': 'USER'
                            }).json()
    user_data = answer['results']
    rows = []
    builder = InlineKeyboardBuilder()
    if answer['count'] > 0:
        builder.button(
            text='Отправить сообщение всем пользователям',
            callback_data=UserListCallbackFactory(
                action=user_list_actions.send_to_all,
            )
        )
        rows.append(1)
        for user in user_data:
            builder.button(
                text=user['name'],
                callback_data=UserListCallbackFactory(
                    action=user_list_actions.get,
                    user_id=user['telegram_chat_id'],
                    page=1)
            )
            rows.append(1)
        page_buttons = 0
        if answer['previous']:
            builder.button(
                text="⬅️",
                callback_data=UserListCallbackFactory(
                    action=user_list_actions.get_all,
                    page=page - 1)
            )
            page_buttons += 1
        if answer['next']:
            builder.button(
                text="➡️",
                callback_data=UserListCallbackFactory(
                    action=user_list_actions.get_all,
                    page=page + 1)
            )
            page_buttons += 1
        rows.append(page_buttons)
    builder.adjust(*rows)
    return builder


async def user_list_get_info(user_id: int):
    answer = get_api_answer(f'users/{user_id}')
    user = answer.json()
    text = (f"Имя: {user['name']} \n"
            f"Телефон: {user['phone_number']} \n"
            )
    return text


async def user_list_get_builder(user_id: int,
                                page: int = 1):
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Отправить сообщение',
        callback_data=UserListCallbackFactory(
            action=user_list_actions.send_direct,
            user_id=user_id,
        )
    )
    builder.button(
        text='Заблокировать',
        callback_data=UserListCallbackFactory(
            action=user_list_actions.remove,
            user_id=user_id,
        )
    )
    builder.button(
        text='Назад',
        callback_data=UserListCallbackFactory(
            action=user_list_actions.get_all,
            page=page)
    )
    builder.adjust(1)
    return builder


async def user_block(user_id: int):
    answer = patch_api_answer(f'users/{user_id}/',
                              data={
                                  'role': 'GUEST',
                                  'request_for_access': False
                              })
    if answer.status_code == HTTPStatus.OK:
        text = 'Пользователь успешно заблокирован!'
        logger.info(text)
        await send_message_to_user(user_id,
                                   'Вы были заблокированы!')
    else:
        text = f'Произошла ошибка при блокировке {answer.json()}'
        logger.error(text)
    return text
