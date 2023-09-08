from http import HTTPStatus

from aiogram.utils.keyboard import InlineKeyboardBuilder
from core.actions import user_list_actions
from core.factories import UserListCallbackFactory
from logger import logger
from service.message import send_message_to_user
from utils import get_api_answer, patch_api_answer


async def user_list_builder(page: int = 1):
    answer = get_api_answer('users/',
                            params={
                                'role': 'user'
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
                text=user['fullname'],
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
        if page_buttons > 0:
            rows.append(page_buttons)
    builder.adjust(*rows)
    return builder


async def user_list_get_info(user_id: int):
    answer = get_api_answer(f'users/{user_id}')
    user = answer.json()
    return (f"Имя: {user['fullname']} \n"
            f"Телефон: {user['phone_number']} \n"
            )


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
                                  'role': 'guest',
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
