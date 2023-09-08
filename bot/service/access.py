from http import HTTPStatus

from aiogram.utils.keyboard import InlineKeyboardBuilder
from core.actions import access_action
from core.factories import AccessCallbackFactory
from logger import logger
from service.message import send_message_to_user
from utils import get_api_answer, patch_api_answer


async def access_list_builder(page: int = 1):
    answer = get_api_answer('users/',
                            params={
                                'request_for_access': True
                            }).json()
    requests_data = answer['results']
    builder = InlineKeyboardBuilder()
    rows = []
    for user in requests_data:
        builder.button(
            text=user['fullname'],
            callback_data=AccessCallbackFactory(
                action=access_action.get,
                user_id=user['telegram_chat_id'],
                page=page)
        )
        rows.append(1)
    page_buttons = 0
    if answer['previous']:
        builder.button(
            text="⬅️",
            callback_data=AccessCallbackFactory(
                action=access_action.get_all,
                page=page - 1)
        )
        page_buttons += 1
    if answer['next']:
        builder.button(
            text="➡️",
            callback_data=AccessCallbackFactory(
                action=access_action.get_all,
                page=page + 1)
        )
        page_buttons += 1
    if page_buttons > 0:
        rows.append(page_buttons)
    builder.adjust(*rows)
    return builder


async def access_get_info(user_id: int):
    answer = get_api_answer(f'users/{user_id}')
    user = answer.json()
    return (f"Имя: {user['fullname']} \n"
            f"Телефон: {user['phone_number']} \n"
            )


async def access_get_builder(user_id: int,
                             page: int = 1):
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Одобрить',
        callback_data=AccessCallbackFactory(
            action=access_action.create,
            user_id=user_id,
            page=page)
    )
    builder.button(
        text='Отменить',
        callback_data=AccessCallbackFactory(
            action=access_action.remove,
            user_id=user_id,
            page=page)
    )
    builder.button(
        text='Назад',
        callback_data=AccessCallbackFactory(
            action=access_action.get_all,
            page=page)
    )
    builder.adjust(2, 1)
    return builder


async def access_create(user_id: int):
    answer = patch_api_answer(f'users/{user_id}/',
                              data={
                                  'role': 'user',
                                  'request_for_access': False
                              })
    if answer.status_code == HTTPStatus.OK:
        text = 'Одобрение заявки прошло успешно'
        logger.info(text)
        await send_message_to_user(user_id,
                                   'Ваша заявка одобрена!')
    else:
        text = f'Произошла ошибка при одобрении заявки {answer.json()}'
        logger.error(text)
    return text


async def access_remove(user_id: int):
    answer = patch_api_answer(f'users/{user_id}/',
                              data={
                                  'request_for_access': False
                              })
    if answer.status_code == HTTPStatus.OK:
        text = 'Отклонение заявки прошло успешно'
        logger.info(text)
        await send_message_to_user(user_id,
                                   'Ваша заявка отклонена!')
    else:
        text = f'Произошла ошибка при отклонении заявки {answer.json()}'
        logger.error(text)
    return text


async def access_request_builder():
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Отмена',
        callback_data=AccessCallbackFactory(
            action=access_action.stop)
    )
    return builder
