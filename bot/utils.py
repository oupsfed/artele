import json
import logging

import requests
from requests import Response

URL = 'http://127.0.0.1:8000/api/'
HEADERS = {'Content-type': 'application/json',
           'Content-Encoding': 'utf-8'}


class Action:
    get = 'get'
    create = 'create'
    remove = 'remove'
    get_all = 'get_all'
    update = 'update'

    def __init__(self,
                 callback_name):
        self.callback = callback_name
        self.get = self.callback + self.get
        self.create = self.callback + self.create
        self.remove = self.callback + self.remove
        self.get_all = self.callback + self.get_all
        self.update = self.callback + self.update

    def __str__(self):
        return self.callback


def get_api_answer(endpoint: str,
                   params=None) -> Response:
    """
    Делает GET запрос к эндпоинту API-сервиса.

            Parameters:
                    endpoint (str) : точка доступа
                    params (dict) : параметры запроса

            Returns:
                    answer (dict): Информация с API-сервиса
    """
    endpoint = f'{URL}{endpoint}'
    answer = requests.get(
        url=endpoint,
        headers=HEADERS,
        params=params
    )
    if answer.status_code != 200:
        logging.error(f'Запрос к {endpoint} отклонен')
    return answer


def post_api_answer(endpoint: str,
                    data: dict) -> Response:
    """
    Делает POST запрос к эндпоинту API-сервиса.

            Parameters:
                    endpoint (str) : точка доступа
                    data (dict): данные для отправки на API

            Returns:
                    homework (dict): Информация с API-сервиса в формате JSON
    """
    endpoint = f'{URL}{endpoint}'
    data = json.dumps(data)
    answer = requests.post(
        url=endpoint,
        data=data,
        headers=HEADERS
    )
    return answer


def patch_api_answer(endpoint: str,
                     data: dict) -> Response:
    """
    Делает POST запрос к эндпоинту API-сервиса.

            Parameters:
                    endpoint (str) : точка доступа
                    data (dict): данные для отправки на API

            Returns:
                    homework (dict): Информация с API-сервиса в формате JSON
    """
    endpoint = f'{URL}{endpoint}'
    data = json.dumps(data)
    answer = requests.patch(
        url=endpoint,
        data=data,
        headers=HEADERS
    )
    return answer


def delete_api_answer(endpoint: str) -> Response:
    """
    Делает GET запрос к эндпоинту API-сервиса.

            Parameters:
                    endpoint (str) : точка доступа

            Returns:
                    answer (dict): Информация с API-сервиса
    """
    endpoint = f'{URL}{endpoint}'
    answer = requests.delete(
        url=endpoint,
        headers=HEADERS,
    )
    return answer


def check_permissions(user_id: int) -> bool:
    answer = get_api_answer(f'users/{user_id}')
    return answer.json()['is_staff']


def check_phone_number(number: str) -> str:
    replace_data = [
        '+', ' ', '(', ')', '-'
    ]
    for replace_symbol in replace_data:
        number = number.replace(replace_symbol, '')
    if number[0] == '7':
        number = f'8{number[1:]}'
    return number


async def send_message_to_admin(bot, text):
    admin_data = get_api_answer('admin/').json()
    for admin in admin_data:
        try:
            await bot.send_message(
                chat_id=admin['telegram_chat_id'],
                text=text
            )
        except Exception as error:
            logging.error(f'Произошла ошибка при отправке сообщения пользователю \n {error}')
